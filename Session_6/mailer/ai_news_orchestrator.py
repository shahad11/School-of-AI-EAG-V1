from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from rich.console import Console
from rich.panel import Panel
import asyncio
import sys
from datetime import datetime

# Import our layer modules
from perception_layer import PerceptionLayer
from memory_layer import MemoryLayer
from decision_layer import DecisionLayer
from models import (
    FetchAINewsInput,
    FetchAINewsOutput,
    FetchArticleContentInput,
    FetchArticleContentOutput,
    SaveToWordInput,
    ArticleContent,
    SendEmailInput,
)
import json

console = Console()

# Load environment variables
load_dotenv()

class AINewsOrchestrator:
    """Main orchestrator that coordinates all four layers for the AI News Agent."""
    
    def __init__(self):
        self.perception_layer = PerceptionLayer()
        self.memory_layer = MemoryLayer()
        self.decision_layer = DecisionLayer()
        self.session = None
        
    async def initialize_mcp_session(self):
        """Initialize the MCP session for tool execution."""
        try:
            server_params = StdioServerParameters(
                command=sys.executable,
                args=["ai_news_tools.py"]
            )
            
            self.stdio_client = stdio_client(server_params)
            self.read, self.write = await self.stdio_client.__aenter__()
            self.session = ClientSession(self.read, self.write)
            await self.session.__aenter__()
            await self.session.initialize()
            console.print("[green]✓ MCP Session initialized successfully[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Error initializing MCP session: {e}[/red]")
            return False
    
    async def close_mcp_session(self):
        """Close the MCP session."""
        try:
            if hasattr(self, 'session') and self.session:
                await self.session.__aexit__(None, None, None)
                console.print("[green]✓ MCP Session closed[/green]")
            if hasattr(self, 'stdio_client') and self.stdio_client:
                await self.stdio_client.__aexit__(None, None, None)
                console.print("[green]✓ Stdio client closed[/green]")
        except Exception as e:
            console.print(f"[red]Error closing MCP session: {e}[/red]")
    
    async def execute_workflow(self, user_input: str = "Fetch AI news and send me a summary"):
        """Execute the complete AI news workflow using all four layers."""
        try:
            console.print(Panel("AI News & Robotics Agent - Modular Architecture", border_style="cyan"))
            
            # Step 1: Perception Layer - Process user input
            console.print("\n[bold blue]Step 1: Perception Layer[/bold blue]")
            perception_data = self.perception_layer.process_user_input(user_input)
            
            # Step 2: Memory Layer - Load context and preferences
            console.print("\n[bold blue]Step 2: Memory Layer[/bold blue]")
            memory_data = self.memory_layer.get_memory_summary()
            user_preferences = self.memory_layer.get_user_preferences()
            
            # Store user preferences from perception
            if perception_data.get("facts", {}).get("preferences"):
                self.memory_layer.store_user_preferences(
                    perception_data["facts"]["preferences"]
                )
            
            # Step 3: Decision Layer - Create workflow plan
            console.print("\n[bold blue]Step 3: Decision Layer[/bold blue]")
            workflow = self.decision_layer.create_workflow_plan(perception_data, memory_data)
            
            # Optimize workflow based on historical data
            workflow = self.decision_layer.optimize_workflow(workflow, memory_data)
            
            # Determine priority
            priority = self.decision_layer.determine_priority(perception_data, memory_data)
            console.print(f"[blue]Priority: {priority}[/blue]")
            
            # Step 4: Action Layer - Execute the workflow
            console.print("\n[bold blue]Step 4: Action Layer[/bold blue]")
            
            if not await self.initialize_mcp_session():
                console.print("[red]❌ Failed to initialize MCP session. Exiting.[/red]")
                return False
            
            # Execute each step in the workflow
            success = await self._execute_workflow_steps(workflow, perception_data, memory_data)
            
            # Update system state
            if success:
                self.memory_layer.update_system_state(
                    successful_runs=memory_data.get("system_state", {}).get("successful_runs", 0) + 1,
                    total_articles_processed=memory_data.get("system_state", {}).get("total_articles_processed", 0) + 3
                )
            else:
                self.memory_layer.update_system_state(
                    failed_runs=memory_data.get("system_state", {}).get("failed_runs", 0) + 1
                )
            
            return success
            
        except Exception as e:
            console.print(f"[red]Error in workflow execution: {e}[/red]")
            import traceback
            console.print(f"[red]Traceback: {traceback.format_exc()}[/red]")
            return False
        finally:
            await self.close_mcp_session()
    
    async def _execute_workflow_steps(self, workflow: dict, perception_data: dict, memory_data: dict) -> bool:
        """Execute each step in the workflow."""
        try:
            articles = []
            selected_articles = []
            articles_with_content = []
            current_summary = None
            
            for step in workflow["steps"]:
                step_num = step["step"]
                action = step["action"]
                parameters = step["parameters"]
                
                console.print(f"\n[blue]Executing Step {step_num}: {step['description']}[/blue]")
                
                try:
                    if action == "fetch_ai_news":
                        # Check if we should use cached articles
                        if self.decision_layer.should_use_cache(memory_data):
                            cached_articles = self.memory_layer.get_cached_articles()
                            if cached_articles:
                                articles = cached_articles
                                console.print("[green]✓ Using cached articles[/green]")
                                continue
                        
                        # Fetch new articles
                        # Prefer v2 (Pydantic) tool if available; fallback to legacy
                        try:
                            result = await self.session.call_tool("fetch_ai_news_v2", arguments=FetchAINewsInput(url=parameters.get("url")).model_dump())
                            data = json.loads(result.content[0].text)
                            articles = [(a["title"], a["url"]) for a in data.get("articles", [])]
                        except Exception:
                            result = await self.session.call_tool("fetch_ai_news", arguments=parameters)
                            articles = eval(result.content[0].text)
                        console.print(f"[green]✓ Fetched {len(articles)} articles[/green]")
                        
                        # Cache the articles
                        self.memory_layer.cache_articles(articles)
                        
                    elif action == "select_relevant_articles":
                        # If we don't have articles from previous step, use fallback
                        if not articles:
                            console.print("[yellow]No articles available, using fallback sample articles[/yellow]")
                            articles = [
                                ("AI Breakthrough: New Model Achieves Human-Level Reasoning", "https://example.com/ai-breakthrough"),
                                ("Robotics Revolution: Self-Learning Robots Transform Manufacturing", "https://example.com/robotics-revolution"),
                                ("Machine Learning Advances: Neural Networks Solve Complex Problems", "https://example.com/ml-advances")
                            ]
                        
                        selected_articles = await self.decision_layer.select_relevant_articles(articles, memory_data)
                        console.print(f"[green]✓ Selected {len(selected_articles)} articles[/green]")
                        
                        # Remember the selection
                        self.memory_layer.remember_article_selection(
                            selected_articles, 
                            "AI and Robotics relevance"
                        )
                        
                    elif action == "fetch_article_content":
                        articles_with_content = []
                        for i, (title, url) in enumerate(selected_articles, 1):
                            console.print(f"  Fetching article {i}/{len(selected_articles)}...")
                            try:
                                # Prefer v2
                                try:
                                    content_result = await self.session.call_tool("fetch_article_content_v2", arguments=FetchArticleContentInput(url=url).model_dump())
                                    content = json.loads(content_result.content[0].text).get("content", "")
                                except Exception:
                                    content_result = await self.session.call_tool("fetch_article_content", arguments={"url": url})
                                    content = content_result.content[0].text
                                articles_with_content.append((title, content))
                                console.print(f"  [green]✓ Fetched content for: {title[:50]}...[/green]")
                            except Exception as content_error:
                                console.print(f"  [yellow]⚠ Failed to fetch content for {title[:50]}..., using placeholder[/yellow]")
                                # Use placeholder content for failed articles
                                articles_with_content.append((title, f"Content for {title} could not be fetched. This is placeholder content."))
                        
                        console.print(f"[green]✓ Fetched content for {len(articles_with_content)} articles[/green]")
                        
                    elif action == "save_to_word":
                        if not articles_with_content:
                            console.print("[yellow]No articles with content to save[/yellow]")
                            continue
                            
                        # Prefer v2
                        try:
                            payload = SaveToWordInput(
                                filename=parameters.get("filename", "ai_news_articles.docx"),
                                articles=[ArticleContent(title=t, content=c) for t, c in articles_with_content],
                            )
                            save_result = await self.session.call_tool("save_to_word_v2", arguments=payload.model_dump())
                            result_text = json.loads(save_result.content[0].text).get("message", "Saved")
                            console.print(f"[green]✓ {result_text}[/green]")
                        except Exception:
                            save_result = await self.session.call_tool("save_to_word", arguments={
                                "filename": parameters.get("filename", "ai_news_articles.docx"),
                                "articles": articles_with_content
                            })
                            console.print(f"[green]✓ {save_result.content[0].text}[/green]")
                        
                    elif action == "generate_summary":
                        if not articles_with_content:
                            console.print("[yellow]No articles with content to summarize[/yellow]")
                            continue
                            
                        summary = await self.decision_layer.generate_summary(articles_with_content, memory_data)
                        # If LLM failed, create a simple fallback summary
                        if not summary or "Summary generation failed" in summary:
                            bullets = []
                            for idx, (title, content) in enumerate(articles_with_content, start=1):
                                preview = (content or "").strip()[:220]
                                bullets.append(f"{idx}. {title}\n   {preview}...")
                            summary = "AI News & Robotics Summary (Fallback)\n\n" + "\n\n".join(bullets)
                        current_summary = summary
                        console.print(f"[green]✓ Generated summary ({len(summary)} characters)[/green]")
                        
                        # Store the summary for future reference
                        self.memory_layer.store_session({
                            "action": "generate_summary",
                            "summary_length": len(summary),
                            "articles_count": len(articles_with_content)
                        })
                        
                    elif action == "send_email":
                        if not articles_with_content:
                            console.print("[yellow]No articles with content to send email about[/yellow]")
                            continue
                            
                        # Reuse the summary from Step 5; only regenerate as a last resort
                        summary = current_summary
                        if not summary:
                            summary = await self.decision_layer.generate_summary(articles_with_content, memory_data)
                        if not summary or "Summary generation failed" in summary:
                            bullets = []
                            for idx, (title, content) in enumerate(articles_with_content, start=1):
                                preview = (content or "").strip()[:220]
                                bullets.append(f"{idx}. {title}\n   {preview}...")
                            summary = "AI News & Robotics Summary (Fallback)\n\n" + "\n\n".join(bullets)
                        # Persist the final summary used
                        current_summary = summary
                        
                        # Prefer v2
                        try:
                            email_payload = SendEmailInput(
                                subject="AI News & Robotics Summary",
                                body=summary,
                                to_email=parameters.get("to_email", "shahadmohammed111111@gmail.com"),
                            )
                            email_result = await self.session.call_tool("send_email_v2", arguments=email_payload.model_dump())
                            result_text = json.loads(email_result.content[0].text).get("message", "Email sent")
                            console.print(f"[green]✓ {result_text}[/green]")
                        except Exception:
                            email_result = await self.session.call_tool("send_email", arguments={
                                "subject": "AI News & Robotics Summary",
                                "body": summary,
                                "to_email": parameters.get("to_email", "shahadmohammed111111@gmail.com")
                            })
                            console.print(f"[green]✓ {email_result.content[0].text}[/green]")
                        
                        # Store email record
                        self.memory_layer.store_email_sent({
                            "subject": "AI News & Robotics Summary",
                            "to_email": parameters.get("to_email", "shahadmohammed111111@gmail.com"),
                            "summary_length": len(summary),
                            "articles_count": len(articles_with_content)
                        })
                    
                    # Store session data for this step
                    self.memory_layer.store_session({
                        "step": step_num,
                        "action": action,
                        "status": "success",
                        "parameters": parameters
                    })
                    
                except Exception as step_error:
                    console.print(f"[red]❌ Error in step {step_num}: {step_error}[/red]")
                    
                    # Create recovery plan
                    recovery_plan = self.decision_layer.create_error_recovery_plan(
                        str(step_error), step_num, workflow
                    )
                    
                    console.print(f"[yellow]Recovery plan: {recovery_plan['recovery_steps']}[/yellow]")
                    
                    # Store failed step
                    self.memory_layer.store_session({
                        "step": step_num,
                        "action": action,
                        "status": "failed",
                        "error": str(step_error),
                        "recovery_plan": recovery_plan
                    })
                    
                    # For step 1 (fetch_ai_news), continue with fallback
                    if step_num == 1:
                        console.print("[yellow]Continuing with fallback articles for remaining steps[/yellow]")
                        continue
                    
                    if not recovery_plan["can_continue"]:
                        console.print("[red]❌ Cannot continue after this error. Stopping workflow.[/red]")
                        return False
            
            console.print("\n[green]🎉 AI News workflow completed successfully![/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]Error executing workflow steps: {e}[/red]")
            return False
    
    def get_system_status(self) -> dict:
        """Get the current status of all layers."""
        memory_summary = self.memory_layer.get_memory_summary()
        
        return {
            "perception_layer": "Ready",
            "memory_layer": f"Active - {memory_summary['total_sessions']} sessions, {memory_summary['total_emails']} emails",
            "decision_layer": "Ready",
            "action_layer": "Ready (MCP tools available)",
            "system_state": memory_summary["system_state"],
            "last_run": memory_summary["system_state"].get("last_run", "Never")
        }

async def main():
    """Main function to run the AI News Orchestrator."""
    orchestrator = AINewsOrchestrator()
    
    # Get system status
    status = orchestrator.get_system_status()
    console.print("\n[bold cyan]System Status:[/bold cyan]")
    for layer, state in status.items():
        if layer != "system_state" and layer != "last_run":
            console.print(f"  {layer}: {state}")
    
    # Execute the workflow
    success = await orchestrator.execute_workflow()
    
    if success:
        console.print("\n[bold green]✅ Workflow completed successfully![/bold green]")
    else:
        console.print("\n[bold red]❌ Workflow failed![/bold red]")

if __name__ == "__main__":
    asyncio.run(main())
