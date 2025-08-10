# AI News Agent - Modular Architecture

This project has been restructured into a modular, scalable architecture with four distinct layers that work together to provide intelligent AI news processing and delivery.

## Architecture Overview

The system is built around four core layers:

### 1. Perception Layer (`perception_layer.py`)
**Purpose**: Translates raw user input into structured information that the agent can reason with.

**Key Features**:
- Intent extraction using LLM
- Fact extraction and requirement parsing
- Article data structuring
- Confidence scoring for decisions

**Main Methods**:
- `extract_intent(user_input)` - Determines what the user wants to do
- `extract_facts(user_input)` - Extracts key facts and requirements
- `parse_articles(articles)` - Structures article data for reasoning
- `process_user_input(user_input)` - Main entry point for perception processing

### 2. Memory Layer (`memory_layer.py`)
**Purpose**: Stores facts and states about the user or environment for future reasoning.

**Key Features**:
- Persistent memory storage in JSON format
- User preferences tracking
- Session history management
- Article caching system
- Email history tracking
- System state monitoring

**Main Methods**:
- `store_user_preferences(preferences)` - Saves user preferences
- `cache_articles(articles, source)` - Caches articles to avoid refetching
- `store_session(session_data)` - Records session information
- `search_memory(query)` - Searches through stored data
- `get_memory_summary()` - Provides overview of stored data

### 3. Decision Layer (`decision_layer.py`)
**Purpose**: Decides what to do next based on current input and memory.

**Key Features**:
- Workflow planning and optimization
- Intelligent article selection using LLM
- Summary generation with context awareness
- Error recovery planning
- Priority determination
- Performance optimization based on historical data

**Main Methods**:
- `create_workflow_plan(perception_data, memory_data)` - Creates execution plan
- `select_relevant_articles(articles, memory_data)` - Chooses best articles
- `generate_summary(articles_with_content, memory_data)` - Creates summaries
- `create_error_recovery_plan(error, step, workflow)` - Plans error recovery
- `optimize_workflow(workflow, memory_data)` - Improves workflow based on history

### 4. Action Layer (`ai_news_tools.py`)
**Purpose**: Executes the decisions made by the decision layer.

**Key Features**:
- MCP (Model Context Protocol) tool integration
- Web scraping for news articles
- Word document generation
- Email sending capabilities
- Error handling and retry logic

**Available Tools**:
- `fetch_ai_news(url)` - Fetches articles from news sources
- `fetch_article_content(url)` - Gets full article content
- `save_to_word(filename, articles)` - Saves articles to Word file
- `send_email(subject, body, to_email)` - Sends email summaries

## Orchestrator (`ai_news_orchestrator.py`)

The main orchestrator coordinates all four layers:

- **Initialization**: Sets up all layers and MCP session
- **Workflow Execution**: Manages the complete workflow from perception to action
- **Error Handling**: Implements recovery strategies
- **State Management**: Tracks system status and performance

## Usage

### Running the Modular System

```bash
# Run the complete modular system
python ai_news_orchestrator.py
```

### Individual Layer Testing

```python
# Test perception layer
from perception_layer import PerceptionLayer
perception = PerceptionLayer()
result = perception.process_user_input("Fetch AI news and send me a summary")

# Test memory layer
from memory_layer import MemoryLayer
memory = MemoryLayer()
memory.store_user_preferences({"email": "user@example.com"})

# Test decision layer
from decision_layer import DecisionLayer
decision = DecisionLayer()
workflow = decision.create_workflow_plan(perception_data, memory_data)
```

## Configuration

### Environment Variables

Create a `.env` file with:

```env
GEMINI_API_KEY=your_gemini_api_key
SMTP_SERVER=your_smtp_server
SMTP_PORT=587
SMTP_USER=your_email
SMTP_PASSWORD=your_password
```

### Memory Configuration

The memory layer creates `agent_memory.json` to store:
- User preferences
- Session history
- Article cache
- Email history
- System state

## Benefits of Modular Architecture

### 1. Scalability
- Each layer can be enhanced independently
- Easy to add new capabilities to specific layers
- Modular design supports horizontal scaling

### 2. Maintainability
- Clear separation of concerns
- Easy to debug and test individual components
- Reduced coupling between components

### 3. Flexibility
- Can swap out individual layers without affecting others
- Easy to customize behavior for different use cases
- Support for different input/output formats

### 4. Intelligence
- Memory enables learning from past interactions
- Decision layer can optimize based on historical performance
- Perception layer improves understanding over time

### 5. Reliability
- Error recovery at each layer
- Fallback mechanisms for critical operations
- Comprehensive logging and state tracking

## Workflow Example

1. **User Input**: "Get me the latest AI news and send a summary to my email"

2. **Perception Layer**: 
   - Extracts intent: "fetch_news" with confidence 0.95
   - Identifies requirements: email delivery, AI focus
   - Structures the request for processing

3. **Memory Layer**:
   - Loads user preferences (email address, article count)
   - Checks for cached articles
   - Retrieves recent session history

4. **Decision Layer**:
   - Creates workflow plan with 6 steps
   - Determines priority: "high"
   - Optimizes based on past performance

5. **Action Layer**:
   - Executes each step using MCP tools
   - Handles errors with recovery strategies
   - Updates memory with results

## File Structure

```
mailer/
├── perception_layer.py      # Layer 1: Input processing
├── memory_layer.py         # Layer 2: Data persistence
├── decision_layer.py       # Layer 3: Planning and reasoning
├── ai_news_tools.py        # Layer 4: Action execution (unchanged)
├── ai_news_orchestrator.py # Main coordinator
├── ai_news_main.py         # Original monolithic version
├── agent_memory.json       # Memory storage (auto-generated)
├── ai_news_articles.docx   # Output file
└── README_MODULAR.md       # This file
```

## Migration from Original

The original `ai_news_main.py` has been preserved for reference. The new modular system:

- Maintains the same functionality
- Adds intelligence through memory and learning
- Improves error handling and recovery
- Enables easier customization and extension
- Provides better debugging and monitoring capabilities

## Future Enhancements

Potential improvements for each layer:

### Perception Layer
- Multi-modal input support (voice, images)
- Better intent classification
- Context awareness

### Memory Layer
- Database integration for larger datasets
- Advanced caching strategies
- Memory compression and optimization

### Decision Layer
- Advanced planning algorithms
- A/B testing for optimization
- Predictive analytics

### Action Layer
- Additional tool integrations
- Parallel execution capabilities
- Advanced error recovery

This modular architecture provides a solid foundation for scaling the AI news agent into a more sophisticated, intelligent system.
