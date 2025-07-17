from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google import genai
import asyncio
from rich.console import Console
from rich.panel import Panel
import os
from pdb import set_trace

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

async def main():
    try:
        console.print(Panel("AI News & Robotics Agent", border_style="cyan"))
        server_params = StdioServerParameters(
            command="python",
            args=["ai_news_tools.py"]
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                system_prompt = '''You are an AI news and robotics research agent. Your job is to:
1. Fetch the latest news articles from the provided AI news website.
2. Select the three most relevant topics in AI and Robotics.
3. For each, fetch the full article content.
4. Save all articles to a Word file.
5. Summarize all the content in a concise report.
6. Send the summary to the user's email address.

You have access to these tools:
- fetch_ai_news(url: str) - Get a list of (title, link) tuples for news articles
- fetch_article_content(url: str) - Get the full text of an article
- save_to_word(filename: str, articles: list) - Save articles to a Word file
- send_email(subject: str, body: str, to_email: str) - Send an email

Respond with EXACTLY ONE line in one of these formats:
1. FUNCTION_CALL: function_name|param1|param2|...
2. FINAL_ANSWER: [answer]

Example:
User: Fetch the latest news.
Assistant: FUNCTION_CALL: fetch_ai_news|https://www.artificialintelligence-news.com/artificial-intelligence-news/
User: Here are the articles. Select three most relevant in AI and Robotics.
Assistant: FINAL_ANSWER: [(title1, link1), (title2, link2), (title3, link3)]
User: Fetch content for each article.
Assistant: FUNCTION_CALL: fetch_article_content|link1
... (repeat for each)
User: Save all to Word file.
Assistant: FUNCTION_CALL: save_to_word|ai_news_articles.docx|[(title1, content1), (title2, content2), (title3, content3)]
User: Summarize all articles.
Assistant: FINAL_ANSWER: [summary]
User: Send summary to email.
Assistant: FUNCTION_CALL: send_email|AI News Summary|summary|shahadmohammed111111@gmail.com
User: Done.
Assistant: FINAL_ANSWER: [Completed]
'''

                prompt = f"{system_prompt}\n\nFetch the latest news."
                conversation_history = []
                selected_articles = []
                article_contents = []
                summary = ""

                while True:
                    response = await generate_with_timeout(client, prompt)
                    if not response or not response.text:
                        break
                    result = response.text.strip()
                    console.print(f"\n[yellow]Assistant:[/yellow] {result}")

                    if result.startswith("FUNCTION_CALL:"):
                        _, function_info = result.split(":", 1)
                        parts = [p.strip() for p in function_info.split("|")]
                        func_name = parts[0]

                        if func_name == "fetch_ai_news":
                            url = parts[1]
                            news_result = await session.call_tool("fetch_ai_news", arguments={"url": url})
                            articles = eval(news_result.content[0].text)
                            prompt += f"\nUser: Here are the articles. Select three most relevant in AI and Robotics."
                            conversation_history.append(("articles", articles))

                        elif func_name == "fetch_article_content":
                            url = parts[1]
                            content_result = await session.call_tool("fetch_article_content", arguments={"url": url})
                            content = content_result.content[0].text
                            article_contents.append(content)
                            prompt += f"\nUser: Content fetched."

                        elif func_name == "save_to_word":
                            filename = parts[1]
                            # articles: list of (title, content)
                            articles = eval(parts[2])
                            await session.call_tool("save_to_word", arguments={"filename": filename, "articles": articles})
                            prompt += f"\nUser: Articles saved to Word. Summarize all articles."

                        elif func_name == "send_email":
                            subject, body, to_email = parts[1], parts[2], parts[3]
                            await session.call_tool("send_email", arguments={"subject": subject, "body": body, "to_email": to_email})
                            prompt += f"\nUser: Done."

                    elif result.startswith("FINAL_ANSWER:"):
                        answer = result.split("[", 1)[1].split("]")[0]
                        if "Completed" in answer:
                            break
                        elif answer.startswith("(") or answer.startswith("["):
                            # This is the list of selected articles
                            selected_articles = eval(answer)
                            prompt += f"\nUser: Fetch content for each article."
                        else:
                            # This is the summary
                            summary = answer
                            prompt += f"\nUser: Send summary to email."

                    prompt += f"\nAssistant: {result}"

                console.print("\n[green]AI News workflow completed![/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    asyncio.run(main()) 