from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
from rich.console import Console
from rich.panel import Panel
import requests
from bs4 import BeautifulSoup
from docx import Document
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

console = Console()
mcp = FastMCP("AINewsAgent")

@mcp.tool()
def fetch_ai_news(url: str) -> TextContent:
    """Fetch and parse the main AI news page, returning a list of (title, link) tuples for articles."""
    console.print("[blue]FUNCTION CALL:[/blue] fetch_ai_news()")
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        for article in soup.select('div.td-module-thumb > a[rel]'):
            title = article.get('title')
            link = article.get('href')
            if title and link:
                articles.append((title, link))
        return TextContent(type="text", text=str(articles[:10]))  # Return top 10 for selection
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        return TextContent(type="text", text=f"Error: {str(e)}")

@mcp.tool()
def fetch_article_content(url: str) -> TextContent:
    """Fetch the full content of a news article given its URL."""
    console.print("[blue]FUNCTION CALL:[/blue] fetch_article_content()")
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = [p.get_text() for p in soup.select('div.td-post-content p')]
        content = '\n'.join(paragraphs)
        return TextContent(type="text", text=content)
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        return TextContent(type="text", text=f"Error: {str(e)}")

@mcp.tool()
def save_to_word(filename: str, articles: list) -> TextContent:
    """Save a list of (title, content) tuples to a Word file."""
    console.print("[blue]FUNCTION CALL:[/blue] save_to_word()")
    try:
        doc = Document()
        for title, content in articles:
            doc.add_heading(title, level=1)
            doc.add_paragraph(content)
        doc.save(filename)
        return TextContent(type="text", text=f"Saved to {filename}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        return TextContent(type="text", text=f"Error: {str(e)}")

@mcp.tool()
def send_email(subject: str, body: str, to_email: str) -> TextContent:
    """Send an email with the given subject and body to the specified address. Uses SMTP settings from environment variables."""
    console.print("[blue]FUNCTION CALL:[/blue] send_email()")
    try:
        smtp_server = os.getenv("SMTP_SERVER")
        smtp_port = int(os.getenv("SMTP_PORT", 587))
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")
        from_email = smtp_user
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(from_email, to_email, msg.as_string())
        return TextContent(type="text", text="Email sent successfully.")
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        return TextContent(type="text", text=f"Error: {str(e)}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()
    else:
        mcp.run(transport="stdio") 