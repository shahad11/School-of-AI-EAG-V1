import asyncio
import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from rich.console import Console
from rich.panel import Panel
from pdb import set_trace

console = Console()

# Load environment variables
load_dotenv()

async def test_email():
    """Test the email functionality independently"""
    try:
        console.print(Panel("Email Test", border_style="cyan"))
        
        # Check if SMTP settings are configured
        smtp_server = os.getenv("SMTP_SERVER")
        smtp_port = os.getenv("SMTP_PORT")
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")
        set_trace()
        
        console.print(f"SMTP Server: {smtp_server}")
        console.print(f"SMTP Port: {smtp_port}")
        console.print(f"SMTP User: {smtp_user}")
        console.print(f"SMTP Password: {'*' * len(smtp_password) if smtp_password else 'Not set'}")
        
        if not all([smtp_server, smtp_user, smtp_password]):
            console.print("[red]❌ SMTP settings not configured in .env file[/red]")
            console.print("\nPlease add these to your .env file:")
            console.print("SMTP_SERVER=smtp.gmail.com")
            console.print("SMTP_PORT=587")
            console.print("SMTP_USER=your_email@gmail.com")
            console.print("SMTP_PASSWORD=your_app_password")
            return
        
        # Test email configuration
        server_params = StdioServerParameters(
            command="python",
            args=["ai_news_tools.py"]
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Test email
                test_subject = "AI News Agent - Email Test"
                test_body = """This is a test email from your AI News Agent.

If you receive this email, it means:
✅ SMTP configuration is correct
✅ Email sending functionality is working
✅ Your AI News Agent can send emails successfully

Test completed at: """ + str(asyncio.get_event_loop().time())
                
                console.print(f"\n[blue]Sending test email to: shahadmohammed111111@gmail.com[/blue]")
                console.print(f"[blue]Subject: {test_subject}[/blue]")
                
                email_result = await session.call_tool("send_email", arguments={
                    "subject": test_subject,
                    "body": test_body,
                    "to_email": "shahadmohammed111111@gmail.com"
                })
                
                result_text = email_result.content[0].text
                console.print(f"\n[green]✓ {result_text}[/green]")
                
                if "Error" in result_text:
                    console.print("[red]❌ Email test failed[/red]")
                else:
                    console.print("[green]🎉 Email test successful! Check your inbox.[/green]")
                    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        console.print(f"[red]Traceback: {traceback.format_exc()}[/red]")

if __name__ == "__main__":
    asyncio.run(test_email()) 