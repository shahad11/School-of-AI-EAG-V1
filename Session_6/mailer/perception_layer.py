from google import genai
import os
from dotenv import load_dotenv
from rich.console import Console

console = Console()

# Load environment variables and setup Gemini
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

class PerceptionLayer:
    """Perception layer responsible for translating raw user input into structured information."""
    
    def __init__(self):
        self.client = client
    
    def extract_intent(self, user_input: str) -> dict:
        """Extract the user's intent from their input."""
        prompt = f"""Analyze this user input and extract the intent:
        
User Input: {user_input}

Return a JSON object with the following structure:
{{
    "intent": "fetch_news|summarize|email|save_document|custom",
    "confidence": 0.95,
    "parameters": {{
        "topic": "ai_robotics|general_ai|specific_topic",
        "action": "fetch|process|send|save",
        "target": "email|file|console"
    }},
    "raw_input": "{user_input}"
}}"""
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            # Parse the response to extract JSON
            import json
            import re
            
            # Find JSON in the response
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback to default structure
                return {
                    "intent": "fetch_news",
                    "confidence": 0.8,
                    "parameters": {
                        "topic": "ai_robotics",
                        "action": "fetch",
                        "target": "email"
                    },
                    "raw_input": user_input
                }
        except Exception as e:
            console.print(f"[red]Error extracting intent: {e}[/red]")
            return {
                "intent": "fetch_news",
                "confidence": 0.5,
                "parameters": {
                    "topic": "ai_robotics",
                    "action": "fetch",
                    "target": "email"
                },
                "raw_input": user_input
            }
    
    def extract_facts(self, user_input: str) -> dict:
        """Extract key facts and requirements from user input."""
        prompt = f"""Extract key facts and requirements from this input:

{user_input}

Return a JSON object with the following structure:
{{
    "facts": [
        "fact1",
        "fact2"
    ],
    "requirements": [
        "requirement1", 
        "requirement2"
    ],
    "constraints": [
        "constraint1",
        "constraint2"
    ],
    "preferences": {{
        "email": "user@example.com",
        "filename": "articles.docx",
        "article_count": 3,
        "topics": ["ai", "robotics"]
    }}
}}"""
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            import json
            import re
            
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {
                    "facts": ["User wants AI news"],
                    "requirements": ["Fetch articles", "Generate summary"],
                    "constraints": [],
                    "preferences": {
                        "email": "shahadmohammed111111@gmail.com",
                        "filename": "ai_news_articles.docx",
                        "article_count": 3,
                        "topics": ["ai", "robotics"]
                    }
                }
        except Exception as e:
            console.print(f"[red]Error extracting facts: {e}[/red]")
            return {
                "facts": ["User wants AI news"],
                "requirements": ["Fetch articles", "Generate summary"],
                "constraints": [],
                "preferences": {
                    "email": "shahadmohammed111111@gmail.com",
                    "filename": "ai_news_articles.docx",
                    "article_count": 3,
                    "topics": ["ai", "robotics"]
                }
            }
    
    def parse_articles(self, articles: list) -> dict:
        """Parse and structure article data for reasoning."""
        if not articles:
            return {"articles": [], "topics": [], "count": 0}
        
        # Extract topics from article titles
        topics = []
        for title, url in articles:
            if "ai" in title.lower() or "artificial intelligence" in title.lower():
                topics.append("ai")
            if "robot" in title.lower() or "automation" in title.lower():
                topics.append("robotics")
            if "machine learning" in title.lower() or "ml" in title.lower():
                topics.append("machine_learning")
        
        return {
            "articles": articles,
            "topics": list(set(topics)),
            "count": len(articles),
            "urls": [url for _, url in articles],
            "titles": [title for title, _ in articles]
        }
    
    def process_user_input(self, user_input: str) -> dict:
        """Main method to process user input and return structured information."""
        console.print("[blue]Perception Layer: Processing user input...[/blue]")
        
        intent = self.extract_intent(user_input)
        facts = self.extract_facts(user_input)
        
        structured_info = {
            "intent": intent,
            "facts": facts,
            "timestamp": "2024-01-01T00:00:00Z",  # In real app, use actual timestamp
            "processed": True
        }
        
        console.print(f"[green]✓ Perception Layer: Extracted intent '{intent['intent']}' with confidence {intent['confidence']}[/green]")
        return structured_info
