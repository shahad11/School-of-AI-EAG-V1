# Agentic AI News Agent

## 📰 Project Overview
This project is an **Agentic AI workflow** that fetches the latest news articles about AI and Robotics, selects the most relevant ones, extracts their content, saves them to a Word document, generates a summary, and emails the summary to a specified address—all in an automated, step-by-step fashion.

- **Agentic workflow**: The system uses a chain-of-thought, tool-using agent that orchestrates multiple steps, calling tools for web scraping, document creation, and email sending.
- **MCP Tools**: All core functionalities (fetching news, extracting content, saving to Word, sending email) are implemented as MCP tools in `ai_news_tools.py`.
- **LLM Orchestration**: The main agent (`ai_news_main.py`) uses a large language model to select relevant articles and generate summaries.
- **Environment Management**: The project uses [UV](https://github.com/astral-sh/uv) for fast, isolated Python environment management and dependency installation.

---

## 🚀 Quick Start

### 1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/agentic-ai-news-agent.git
cd agentic-ai-news-agent
```

### 2. **Install [UV](https://github.com/astral-sh/uv) (if not already installed)**
UV is a super-fast Python package manager and virtual environment tool. It makes it easy to create isolated environments for each project.

```bash
pip install uv
```

### 3. **Install Dependencies**
```bash
uv pip install -r pyproject.toml
uv pip install python-dotenv
```

### 4. **Configure Environment Variables**
Create a `.env` file in the project root with the following content:

```env
GEMINI_API_KEY=your_gemini_api_key_here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
```
- For Gmail, you must use an [App Password](https://support.google.com/accounts/answer/185833?hl=en) (not your regular password).

### 5. **Run the MCP Tool Server**
Open a terminal and run:
```bash
py -m uv run ai_news_tools.py
defaults to stdio mode
```
This starts the MCP tool server, which exposes the tools for the agent to use.

### 6. **Run the Main Agent**
In another terminal, run:
```bash
py -m uv run ai_news_main.py
```
The agent will:
- Fetch the latest AI/Robotics news
- Select the 3 most relevant articles
- Extract and save their content to a Word file
- Generate a summary
- Email the summary to the address in your `.env`

---

## ⚙️ How It Works: Agentic Workflow
- The main agent (`ai_news_main.py`) acts as an orchestrator, using a large language model to decide which tools to call and in what order.
- Each step (fetching news, extracting content, saving, emailing) is a tool defined in `ai_news_tools.py`.
- The agent maintains a chain-of-thought, passing results from one tool to the next, and can handle errors or missing data gracefully.
- This modular, tool-based approach is called an **agentic workflow**—it enables flexible, explainable, and extensible automation.

---

## 🧑‍💻 Example Output
```
Step 1: Fetching articles from AI News website...
✓ Fetched 10 articles
Step 2: Selecting three most relevant articles in AI and Robotics...
✓ Selected 3 articles:
  1. ...
  2. ...
  3. ...
Step 3: Fetching content for each article...
✓ Fetched content for: ...
Step 4: Saving articles to ai_news_articles.docx...
✓ Saved to ai_news_articles.docx
Step 5: Generating summary of all articles...
✓ Summary generated
Step 6: Sending summary to youremail@gmail.com...
✓ Email sent successfully!
```

---

## 🙏 Credits & Acknowledgements
- Built with [UV](https://github.com/astral-sh/uv), [python-dotenv](https://github.com/theskumar/python-dotenv), [python-docx](https://python-docx.readthedocs.io/), [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/), and [Rich](https://github.com/Textualize/rich).
- Agentic workflow inspired by modern LLM tool-use research.

---

## 📬 Questions?
Open an issue or contact the maintainer at shahadmohammed111111@gmail.com.
