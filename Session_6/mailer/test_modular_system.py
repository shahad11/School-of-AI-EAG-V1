#!/usr/bin/env python3
"""
Test script for the modular AI News system.
This script tests the individual layers without the MCP session to isolate issues.
"""

import asyncio
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv

# Import our layer modules
from perception_layer import PerceptionLayer
from memory_layer import MemoryLayer
from decision_layer import DecisionLayer

console = Console()
load_dotenv()

async def test_perception_layer():
    """Test the perception layer."""
    console.print("\n[bold blue]Testing Perception Layer[/bold blue]")
    
    perception = PerceptionLayer()
    
    # Test with different inputs
    test_inputs = [
        "Fetch AI news and send me a summary",
        "Get the latest robotics news and save to file",
        "Send me AI updates via email"
    ]
    
    for user_input in test_inputs:
        console.print(f"\n[cyan]Testing input: {user_input}[/cyan]")
        try:
            result = perception.process_user_input(user_input)
            console.print(f"[green]✓ Success: {result['intent']['intent']} (confidence: {result['intent']['confidence']})[/green]")
        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")

async def test_memory_layer():
    """Test the memory layer."""
    console.print("\n[bold blue]Testing Memory Layer[/bold blue]")
    
    memory = MemoryLayer("test_memory.json")
    
    try:
        # Test storing preferences
        memory.store_user_preferences({
            "email": "test@example.com",
            "article_count": 5,
            "topics": ["ai", "robotics"]
        })
        
        # Test storing session
        memory.store_session({
            "action": "test_action",
            "status": "success"
        })
        
        # Test caching articles
        test_articles = [
            ("Test Article 1", "https://example.com/1"),
            ("Test Article 2", "https://example.com/2")
        ]
        memory.cache_articles(test_articles)
        
        # Test retrieving data
        prefs = memory.get_user_preferences()
        sessions = memory.get_recent_sessions()
        summary = memory.get_memory_summary()
        
        console.print(f"[green]✓ Memory tests passed: {len(prefs)} preferences, {len(sessions)} sessions[/green]")
        
    except Exception as e:
        console.print(f"[red]✗ Memory test error: {e}[/red]")

async def test_decision_layer():
    """Test the decision layer."""
    console.print("\n[bold blue]Testing Decision Layer[/bold blue]")
    
    decision = DecisionLayer()
    memory = MemoryLayer("test_memory.json")
    
    try:
        # Test workflow creation
        perception_data = {
            "intent": {"intent": "fetch_news", "confidence": 0.9},
            "facts": {"preferences": {"email": "test@example.com"}}
        }
        memory_data = memory.get_memory_summary()
        
        workflow = decision.create_workflow_plan(perception_data, memory_data)
        console.print(f"[green]✓ Workflow created with {workflow['total_steps']} steps[/green]")
        
        # Test article selection
        test_articles = [
            ("AI Breakthrough", "https://example.com/ai"),
            ("Robotics News", "https://example.com/robotics"),
            ("ML Advances", "https://example.com/ml")
        ]
        
        selected = await decision.select_relevant_articles(test_articles, memory_data)
        console.print(f"[green]✓ Selected {len(selected)} articles[/green]")
        
        # Test summary generation
        articles_with_content = [
            ("Test Article", "This is test content for the article."),
            ("Another Article", "More test content here.")
        ]
        
        summary = await decision.generate_summary(articles_with_content, memory_data)
        console.print(f"[green]✓ Generated summary ({len(summary)} characters)[/green]")
        
    except Exception as e:
        console.print(f"[red]✗ Decision test error: {e}[/red]")

async def test_integration():
    """Test integration between layers."""
    console.print("\n[bold blue]Testing Layer Integration[/bold blue]")
    
    perception = PerceptionLayer()
    memory = MemoryLayer("test_memory.json")
    decision = DecisionLayer()
    
    try:
        # Simulate full workflow without MCP
        user_input = "Get AI news and send summary to my email"
        
        # Step 1: Perception
        perception_data = perception.process_user_input(user_input)
        console.print(f"[green]✓ Perception: {perception_data['intent']['intent']}[/green]")
        
        # Step 2: Memory
        memory_data = memory.get_memory_summary()
        memory.store_user_preferences(perception_data.get("facts", {}).get("preferences", {}))
        console.print(f"[green]✓ Memory: Loaded {memory_data['total_sessions']} sessions[/green]")
        
        # Step 3: Decision
        workflow = decision.create_workflow_plan(perception_data, memory_data)
        priority = decision.determine_priority(perception_data, memory_data)
        console.print(f"[green]✓ Decision: Created workflow with priority {priority}[/green]")
        
        # Test with sample data
        test_articles = [
            ("AI Breakthrough: New Model Achieves Human-Level Reasoning", "https://example.com/ai-breakthrough"),
            ("Robotics Revolution: Self-Learning Robots Transform Manufacturing", "https://example.com/robotics-revolution"),
            ("Machine Learning Advances: Neural Networks Solve Complex Problems", "https://example.com/ml-advances")
        ]
        
        selected = await decision.select_relevant_articles(test_articles, memory_data)
        console.print(f"[green]✓ Integration: Selected {len(selected)} articles[/green]")
        
        # Test summary generation
        articles_with_content = [
            (selected[0][0], "This is sample content for the first article about AI breakthroughs."),
            (selected[1][0], "This is sample content for the second article about robotics.")
        ]
        
        summary = await decision.generate_summary(articles_with_content, memory_data)
        console.print(f"[green]✓ Integration: Generated summary ({len(summary)} characters)[/green]")
        
        console.print("\n[bold green]🎉 All integration tests passed![/bold green]")
        
    except Exception as e:
        console.print(f"[red]✗ Integration test error: {e}[/red]")
        import traceback
        console.print(f"[red]Traceback: {traceback.format_exc()}[/red]")

async def main():
    """Run all tests."""
    console.print(Panel("Modular AI News System - Layer Tests", border_style="cyan"))
    
    # Test individual layers
    await test_perception_layer()
    await test_memory_layer()
    await test_decision_layer()
    
    # Test integration
    await test_integration()
    
    console.print("\n[bold green]✅ All tests completed![/bold green]")

if __name__ == "__main__":
    asyncio.run(main())
