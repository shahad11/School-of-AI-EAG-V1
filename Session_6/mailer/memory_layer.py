import json
import os
from datetime import datetime
from rich.console import Console
from typing import Dict, List, Any, Optional

console = Console()

class MemoryLayer:
    """Memory layer responsible for storing and retrieving facts and states."""
    
    def __init__(self, memory_file: str = "agent_memory.json"):
        self.memory_file = memory_file
        self.memory = self._load_memory()
    
    def _load_memory(self) -> Dict[str, Any]:
        """Load memory from file or create new if doesn't exist."""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    memory = json.load(f)
                console.print(f"[blue]Memory Layer: Loaded existing memory from {self.memory_file}[/blue]")
                return memory
            else:
                memory = {
                    "user_preferences": {},
                    "session_history": [],
                    "article_cache": {},
                    "email_history": [],
                    "system_state": {
                        "last_run": None,
                        "total_articles_processed": 0,
                        "successful_runs": 0,
                        "failed_runs": 0
                    },
                    "created_at": datetime.now().isoformat()
                }
                self._save_memory(memory)
                console.print(f"[blue]Memory Layer: Created new memory file {self.memory_file}[/blue]")
                return memory
        except Exception as e:
            console.print(f"[red]Error loading memory: {e}[/red]")
            return self._get_default_memory()
    
    def _get_default_memory(self) -> Dict[str, Any]:
        """Get default memory structure."""
        return {
            "user_preferences": {},
            "session_history": [],
            "article_cache": {},
            "email_history": [],
            "system_state": {
                "last_run": None,
                "total_articles_processed": 0,
                "successful_runs": 0,
                "failed_runs": 0
            },
            "created_at": datetime.now().isoformat()
        }
    
    def _save_memory(self, memory: Optional[Dict[str, Any]] = None) -> None:
        """Save memory to file."""
        try:
            memory_to_save = memory if memory is not None else self.memory
            with open(self.memory_file, 'w') as f:
                json.dump(memory_to_save, f, indent=2)
        except Exception as e:
            console.print(f"[red]Error saving memory: {e}[/red]")
    
    def store_user_preferences(self, preferences: Dict[str, Any]) -> None:
        """Store user preferences in memory."""
        self.memory["user_preferences"].update(preferences)
        self._save_memory()
        console.print(f"[green]✓ Memory Layer: Stored user preferences[/green]")
    
    def get_user_preferences(self) -> Dict[str, Any]:
        """Retrieve user preferences from memory."""
        return self.memory.get("user_preferences", {})
    
    def store_session(self, session_data: Dict[str, Any]) -> None:
        """Store session information."""
        session_data["timestamp"] = datetime.now().isoformat()
        self.memory["session_history"].append(session_data)
        
        # Keep only last 50 sessions
        if len(self.memory["session_history"]) > 50:
            self.memory["session_history"] = self.memory["session_history"][-50:]
        
        self._save_memory()
        console.print(f"[green]✓ Memory Layer: Stored session data[/green]")
    
    def get_recent_sessions(self, count: int = 5) -> List[Dict[str, Any]]:
        """Get recent session history."""
        return self.memory.get("session_history", [])[-count:]
    
    def cache_articles(self, articles: List[tuple], source: str = "ai_news") -> None:
        """Cache articles to avoid refetching."""
        cache_key = f"{source}_{datetime.now().strftime('%Y%m%d')}"
        self.memory["article_cache"][cache_key] = {
            "articles": articles,
            "timestamp": datetime.now().isoformat(),
            "count": len(articles)
        }
        
        # Clean old cache entries (older than 7 days)
        self._clean_old_cache()
        self._save_memory()
        console.print(f"[green]✓ Memory Layer: Cached {len(articles)} articles[/green]")
    
    def get_cached_articles(self, source: str = "ai_news", max_age_hours: int = 24) -> Optional[List[tuple]]:
        """Get cached articles if they're recent enough."""
        from datetime import timedelta
        
        cache_key = f"{source}_{datetime.now().strftime('%Y%m%d')}"
        cached_data = self.memory["article_cache"].get(cache_key)
        
        if cached_data:
            cached_time = datetime.fromisoformat(cached_data["timestamp"])
            if datetime.now() - cached_time < timedelta(hours=max_age_hours):
                console.print(f"[blue]Memory Layer: Using cached articles from {cached_time}[/blue]")
                return cached_data["articles"]
        
        return None
    
    def _clean_old_cache(self) -> None:
        """Remove old cache entries."""
        from datetime import timedelta
        
        current_time = datetime.now()
        keys_to_remove = []
        
        for key, data in self.memory["article_cache"].items():
            cached_time = datetime.fromisoformat(data["timestamp"])
            if current_time - cached_time > timedelta(days=7):
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.memory["article_cache"][key]
    
    def store_email_sent(self, email_data: Dict[str, Any]) -> None:
        """Store information about sent emails."""
        email_data["timestamp"] = datetime.now().isoformat()
        self.memory["email_history"].append(email_data)
        
        # Keep only last 100 emails
        if len(self.memory["email_history"]) > 100:
            self.memory["email_history"] = self.memory["email_history"][-100:]
        
        self._save_memory()
        console.print(f"[green]✓ Memory Layer: Stored email record[/green]")
    
    def get_email_history(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent email history."""
        return self.memory.get("email_history", [])[-count:]
    
    def update_system_state(self, **kwargs) -> None:
        """Update system state information."""
        self.memory["system_state"].update(kwargs)
        self.memory["system_state"]["last_run"] = datetime.now().isoformat()
        self._save_memory()
        console.print(f"[green]✓ Memory Layer: Updated system state[/green]")
    
    def get_system_state(self) -> Dict[str, Any]:
        """Get current system state."""
        return self.memory.get("system_state", {})
    
    def remember_article_selection(self, selected_articles: List[tuple], reason: str = "") -> None:
        """Remember which articles were selected and why."""
        selection_data = {
            "articles": selected_articles,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "count": len(selected_articles)
        }
        
        if "article_selections" not in self.memory:
            self.memory["article_selections"] = []
        
        self.memory["article_selections"].append(selection_data)
        
        # Keep only last 20 selections
        if len(self.memory["article_selections"]) > 20:
            self.memory["article_selections"] = self.memory["article_selections"][-20:]
        
        self._save_memory()
        console.print(f"[green]✓ Memory Layer: Remembered article selection[/green]")
    
    def get_article_selection_history(self) -> List[Dict[str, Any]]:
        """Get history of article selections."""
        return self.memory.get("article_selections", [])
    
    def search_memory(self, query: str) -> List[Dict[str, Any]]:
        """Search through memory for relevant information."""
        results = []
        query_lower = query.lower()
        
        # Search in session history
        for session in self.memory.get("session_history", []):
            if query_lower in str(session).lower():
                results.append({"type": "session", "data": session})
        
        # Search in email history
        for email in self.memory.get("email_history", []):
            if query_lower in str(email).lower():
                results.append({"type": "email", "data": email})
        
        # Search in user preferences
        for key, value in self.memory.get("user_preferences", {}).items():
            if query_lower in str(value).lower():
                results.append({"type": "preference", "key": key, "value": value})
        
        console.print(f"[blue]Memory Layer: Found {len(results)} results for query '{query}'[/blue]")
        return results
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get a summary of memory contents."""
        return {
            "total_sessions": len(self.memory.get("session_history", [])),
            "total_emails": len(self.memory.get("email_history", [])),
            "cached_articles_count": len(self.memory.get("article_cache", {})),
            "user_preferences_count": len(self.memory.get("user_preferences", {})),
            "system_state": self.memory.get("system_state", {}),
            "memory_created": self.memory.get("created_at", "Unknown")
        }
