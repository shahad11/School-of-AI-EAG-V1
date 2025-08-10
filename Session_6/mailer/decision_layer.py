from google import genai
import os
from dotenv import load_dotenv
from rich.console import Console
from typing import Dict, List, Any, Optional
import asyncio

console = Console()

# Load environment variables and setup Gemini
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

class DecisionLayer:
    """Decision-making layer responsible for planning the next steps based on input and memory."""
    
    def __init__(self):
        self.client = client
    
    async def generate_with_timeout(self, prompt: str, timeout: int = 10):
        """Generate content with timeout."""
        try:
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: self.client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=prompt
                    )
                ),
                timeout=timeout
            )
            return response
        except asyncio.TimeoutError:
            console.print(f"[red]Timeout error in decision generation after {timeout} seconds[/red]")
            return None
        except Exception as e:
            console.print(f"[red]Error in decision generation: {e}[/red]")
            return None
    
    def create_workflow_plan(self, perception_data: Dict[str, Any], memory_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a workflow plan based on perception and memory data."""
        console.print("[blue]Decision Layer: Creating workflow plan...[/blue]")
        
        intent = perception_data.get("intent", {})
        facts = perception_data.get("facts", {})
        user_prefs = memory_data.get("user_preferences", {})
        
        # Default workflow for AI news
        workflow = {
            "steps": [
                {
                    "step": 1,
                    "action": "fetch_ai_news",
                    "description": "Fetch articles from AI news sources",
                    "parameters": {"url": "https://www.artificialintelligence-news.com/artificial-intelligence-news/"},
                    "required": True
                },
                {
                    "step": 2,
                    "action": "select_relevant_articles",
                    "description": "Select most relevant articles using LLM",
                    "parameters": {"article_count": 3},
                    "required": True
                },
                {
                    "step": 3,
                    "action": "fetch_article_content",
                    "description": "Fetch content for each selected article",
                    "parameters": {},
                    "required": True
                },
                {
                    "step": 4,
                    "action": "save_to_word",
                    "description": "Save articles to Word document",
                    "parameters": {"filename": "ai_news_articles.docx"},
                    "required": True
                },
                {
                    "step": 5,
                    "action": "generate_summary",
                    "description": "Generate summary using LLM",
                    "parameters": {},
                    "required": True
                },
                {
                    "step": 6,
                    "action": "send_email",
                    "description": "Send summary via email",
                    "parameters": {"to_email": "shahadmohammed111111@gmail.com"},
                    "required": True
                }
            ],
            "total_steps": 6,
            "estimated_time": "2-3 minutes",
            "priority": "high"
        }
        
        # Customize workflow based on intent
        if intent.get("intent") == "custom":
            workflow = self._customize_workflow(workflow, perception_data, memory_data)
        
        console.print(f"[green]✓ Decision Layer: Created workflow with {workflow['total_steps']} steps[/green]")
        return workflow
    
    def _customize_workflow(self, base_workflow: Dict[str, Any], perception_data: Dict[str, Any], memory_data: Dict[str, Any]) -> Dict[str, Any]:
        """Customize workflow based on specific requirements."""
        facts = perception_data.get("facts", {})
        preferences = facts.get("preferences", {})
        
        # Update parameters based on user preferences
        for step in base_workflow["steps"]:
            if step["action"] == "select_relevant_articles":
                step["parameters"]["article_count"] = preferences.get("article_count", 3)
            elif step["action"] == "save_to_word":
                step["parameters"]["filename"] = preferences.get("filename", "ai_news_articles.docx")
            elif step["action"] == "send_email":
                step["parameters"]["to_email"] = preferences.get("email", "shahadmohammed111111@gmail.com")
        
        return base_workflow
    
    async def select_relevant_articles(self, articles: List[tuple], memory_data: Dict[str, Any]) -> List[tuple]:
        """Use LLM to select the most relevant articles based on context and memory."""
        console.print("[blue]Decision Layer: Selecting relevant articles...[/blue]")
        
        # Get user preferences and history
        user_prefs = memory_data.get("user_preferences", {})
        selection_history = memory_data.get("article_selections", [])
        
        # Build context from memory
        context = ""
        if selection_history:
            recent_selections = selection_history[-3:]  # Last 3 selections
            context += "Recent article selections:\n"
            for selection in recent_selections:
                context += f"- {selection.get('reason', 'No reason given')}\n"
        
        if user_prefs:
            context += f"User preferences: {user_prefs}\n"
        
        prompt = f"""Given this list of AI news articles and context, select the THREE most relevant ones:

Context:
{context}

Articles:
{articles}

Consider:
1. Relevance to AI and Robotics
2. User's previous selections and preferences
3. Current trends and importance

Return ONLY a Python list of tuples in this exact format:
[(title1, url1), (title2, url2), (title3, url3)]

Choose articles that are most relevant and valuable."""
        
        response = await self.generate_with_timeout(prompt)
        if response and response.text:
            try:
                # Extract the list from the response
                result = response.text.strip()
                if "[" in result and "]" in result:
                    start = result.find("[")
                    end = result.rfind("]") + 1
                    list_str = result[start:end]
                    selected = eval(list_str)
                    
                    # Validate that selected articles exist in original list
                    valid_selected = []
                    original_titles = [title for title, _ in articles]
                    for title, url in selected:
                        if title in original_titles:
                            valid_selected.append((title, url))
                    
                    if valid_selected:
                        console.print(f"[green]✓ Decision Layer: Selected {len(valid_selected)} relevant articles[/green]")
                        return valid_selected
            except Exception as e:
                console.print(f"[red]Error parsing selected articles: {e}[/red]")
        
        # Fallback: return first 3 articles
        fallback = articles[:3] if len(articles) >= 3 else articles
        console.print(f"[yellow]Decision Layer: Using fallback selection of {len(fallback)} articles[/yellow]")
        return fallback
    
    async def generate_summary(self, articles_with_content: List[tuple], memory_data: Dict[str, Any]) -> str:
        """Generate a comprehensive summary of articles using LLM."""
        console.print("[blue]Decision Layer: Generating article summary...[/blue]")
        
        # Get context from memory
        recent_summaries = memory_data.get("email_history", [])[-3:]  # Last 3 summaries
        context = ""
        if recent_summaries:
            context += "Recent summary styles and topics:\n"
            for summary in recent_summaries:
                if "subject" in summary:
                    context += f"- {summary['subject']}\n"
        
        content_text = ""
        for title, content in articles_with_content:
            content_text += f"\n\nTitle: {title}\nContent: {content[:500]}..."  # Truncate for LLM
        
        prompt = f"""Summarize these AI and Robotics news articles in a concise, informative way:

Context from previous summaries:
{context}

Articles to summarize:
{content_text}

Provide a comprehensive summary that:
1. Covers the key developments and their implications
2. Highlights the most important breakthroughs
3. Explains the significance for AI and robotics fields
4. Is engaging and well-structured for email delivery"""
        
        response = await self.generate_with_timeout(prompt)
        if response and response.text:
            summary = response.text.strip()
            console.print(f"[green]✓ Decision Layer: Generated summary ({len(summary)} characters)[/green]")
            return summary
        
        return "Summary generation failed. Please check the articles and try again."
    
    def should_use_cache(self, memory_data: Dict[str, Any]) -> bool:
        """Decide whether to use cached articles or fetch new ones."""
        system_state = memory_data.get("system_state", {})
        last_run = system_state.get("last_run")
        
        if not last_run:
            return False
        
        from datetime import datetime, timedelta
        try:
            last_run_time = datetime.fromisoformat(last_run)
            # Use cache if last run was less than 6 hours ago
            return datetime.now() - last_run_time < timedelta(hours=6)
        except:
            return False
    
    def determine_priority(self, perception_data: Dict[str, Any], memory_data: Dict[str, Any]) -> str:
        """Determine the priority of the current task."""
        intent = perception_data.get("intent", {})
        confidence = intent.get("confidence", 0.5)
        
        # High priority if high confidence or urgent keywords
        if confidence > 0.8:
            return "high"
        
        # Check for urgent keywords in user input
        user_input = intent.get("raw_input", "").lower()
        urgent_keywords = ["urgent", "asap", "important", "critical", "now"]
        if any(keyword in user_input for keyword in urgent_keywords):
            return "high"
        
        return "normal"
    
    def create_error_recovery_plan(self, error: str, current_step: int, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Create a plan to recover from errors."""
        console.print(f"[blue]Decision Layer: Creating error recovery plan for step {current_step}[/blue]")
        
        recovery_plan = {
            "error": error,
            "failed_step": current_step,
            "recovery_steps": [],
            "can_continue": True
        }
        
        # Define recovery strategies for different steps
        if current_step == 1:  # fetch_ai_news
            recovery_plan["recovery_steps"] = [
                "Try alternative news sources",
                "Use cached articles if available",
                "Generate sample articles for testing"
            ]
        elif current_step == 2:  # select_relevant_articles
            recovery_plan["recovery_steps"] = [
                "Use fallback selection (first 3 articles)",
                "Retry with different selection criteria"
            ]
        elif current_step == 3:  # fetch_article_content
            recovery_plan["recovery_steps"] = [
                "Skip problematic articles",
                "Use cached content if available",
                "Generate placeholder content"
            ]
        elif current_step == 4:  # save_to_word
            recovery_plan["recovery_steps"] = [
                "Try different filename",
                "Save to different location",
                "Create backup before overwriting"
            ]
        elif current_step == 5:  # generate_summary
            recovery_plan["recovery_steps"] = [
                "Use simpler summary approach",
                "Retry with different prompt",
                "Use template summary"
            ]
        elif current_step == 6:  # send_email
            recovery_plan["recovery_steps"] = [
                "Check email configuration",
                "Try different email service",
                "Save summary to file instead"
            ]
            recovery_plan["can_continue"] = False  # Email failure is terminal
        
        console.print(f"[green]✓ Decision Layer: Created recovery plan with {len(recovery_plan['recovery_steps'])} steps[/green]")
        return recovery_plan
    
    def optimize_workflow(self, workflow: Dict[str, Any], memory_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize workflow based on historical performance data."""
        console.print("[blue]Decision Layer: Optimizing workflow...[/blue]")
        
        system_state = memory_data.get("system_state", {})
        successful_runs = system_state.get("successful_runs", 0)
        failed_runs = system_state.get("failed_runs", 0)
        
        # If we have a good success rate, keep the workflow as is
        if successful_runs > failed_runs:
            console.print("[green]✓ Decision Layer: Workflow performing well, keeping current configuration[/green]")
            return workflow
        
        # If we have failures, try to optimize
        optimized_workflow = workflow.copy()
        
        # Add error handling to critical steps
        for step in optimized_workflow["steps"]:
            if step["action"] in ["fetch_ai_news", "send_email"]:
                step["retry_count"] = 3
                step["retry_delay"] = 5
        
        console.print("[green]✓ Decision Layer: Added error handling and retry logic[/green]")
        return optimized_workflow
