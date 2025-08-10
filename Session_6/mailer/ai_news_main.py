from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google import genai
import asyncio
from rich.console import Console
from rich.panel import Panel
import os
from pdb import set_trace
import sys

console = Console()

# Load environment variables and setup Gemini
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

NEWS_URL = "https://www.artificialintelligence-news.com/artificial-intelligence-news/"
WORD_FILENAME = "ai_news_articles.docx"
EMAIL = "shahadmohammed111111@gmail.com"

async def generate_with_timeout(client, prompt, timeout=15):
    try:
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None,
                lambda: client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )
            ),
            timeout=timeout
        )
        return response
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return None

async def select_relevant_articles(client, articles):
    """Use LLM to select three most relevant articles in AI and Robotics"""
    prompt = f"""Given this list of AI news articles, select the THREE most relevant ones focusing on AI and Robotics:

{articles}

Return ONLY a Python list of tuples in this exact format:
[(title1, url1), (title2, url2), (title3, url3)]

Choose articles that are most relevant to AI and Robotics advancements, research, or applications."""
    
    response = await generate_with_timeout(client, prompt)
    if response and response.text:
        try:
            # Extract the list from the response
            result = response.text.strip()
            if "[" in result and "]" in result:
                start = result.find("[")
                end = result.rfind("]") + 1
                list_str = result[start:end]
                return eval(list_str)
        except Exception as e:
            console.print(f"[red]Error parsing selected articles: {e}[/red]")
    
    # Fallback: return first 3 articles
    return articles[:3] if len(articles) >= 3 else articles

async def generate_summary(client, articles_with_content):
    """Use LLM to generate a summary of all articles"""
    content_text = ""
    for title, content in articles_with_content:
        content_text += f"\n\nTitle: {title}\nContent: {content[:500]}..."  # Truncate for LLM
    
    prompt = f"""Summarize these AI and Robotics news articles in a concise, informative way:

{content_text}

Provide a comprehensive summary that covers the key developments and their implications."""
    
    response = await generate_with_timeout(client, prompt)
    if response and response.text:
        return response.text.strip()
    return "Summary generation failed."

async def main():
    try:
        console.print(Panel("AI News & Robotics Agent", border_style="cyan"))

        server_params = StdioServerParameters(
            command=sys.executable,
            args=["ai_news_tools.py"]
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Step 1: Fetch all articles from the news website
                console.print("\n[blue]Step 1: Fetching articles from AI News website...[/blue]")
                news_result = await session.call_tool("fetch_ai_news", arguments={"url": NEWS_URL})
                articles = eval(news_result.content[0].text)
                console.print(f"[green]✓ Fetched {len(articles)} articles[/green]")
                
                if not articles:
                    console.print("[red]❌ No articles found. Please check the website URL or try again later.[/red]")
                    return

                # Step 2: Select three most relevant articles using LLM
                console.print("\n[blue]Step 2: Selecting three most relevant articles in AI and Robotics...[/blue]")
                selected_articles = await select_relevant_articles(client, articles)
                console.print(f"[green]✓ Selected {len(selected_articles)} articles:[/green]")
                for i, (title, url) in enumerate(selected_articles, 1):
                    console.print(f"  {i}. {title}")

                if not selected_articles:
                    console.print("[red]❌ No articles selected. Using first 3 articles as fallback.[/red]")
                    selected_articles = articles[:3] if len(articles) >= 3 else articles

                # Step 3: Fetch content for each selected article
                console.print("\n[blue]Step 3: Fetching content for each article...[/blue]")
                articles_with_content = []
                for i, (title, url) in enumerate(selected_articles, 1):
                    console.print(f"  Fetching article {i}/{len(selected_articles)}...")
                    content_result = await session.call_tool("fetch_article_content", arguments={"url": url})
                    content = content_result.content[0].text
                    articles_with_content.append((title, content))
                    console.print(f"  [green]✓ Fetched content for: {title[:50]}...[/green]")

                if not articles_with_content:
                    console.print("[red]❌ No article content could be fetched. Exiting.[/red]")
                    return

                # Step 4: Save all articles to Word file
                console.print(f"\n[blue]Step 4: Saving articles to {WORD_FILENAME}...[/blue]")
                save_result = await session.call_tool("save_to_word", arguments={
                    "filename": WORD_FILENAME, 
                    "articles": articles_with_content
                })
                console.print(f"[green]✓ {save_result.content[0].text}[/green]")

                # Step 5: Generate summary using LLM
                console.print("\n[blue]Step 5: Generating summary of all articles...[/blue]")
                summary = await generate_summary(client, articles_with_content)
                console.print(f"[green]✓ Summary generated[/green]")

                # Step 6: Send summary via email
                console.print(f"\n[blue]Step 6: Sending summary to {EMAIL}...[/blue]")
                email_result = await session.call_tool("send_email", arguments={
                    "subject": "AI News & Robotics Summary",
                    "body": summary,
                    "to_email": EMAIL
                })
                console.print(f"[green]✓ {email_result.content[0].text}[/green]")

                console.print("\n[green]🎉 AI News workflow completed successfully![/green]")
                console.print(f"[cyan]📄 Articles saved to: {WORD_FILENAME}[/cyan]")
                console.print(f"[cyan]📧 Summary sent to: {EMAIL}[/cyan]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        console.print(f"[red]Traceback: {traceback.format_exc()}[/red]")

if __name__ == "__main__":
    asyncio.run(main()) 