# 🔬 Research Paper AI - Chrome Extension

An intelligent Chrome extension that uses agentic AI to find and fetch relevant research papers from IEEE, arXiv, Google Scholar, and other research sites based on your queries.

## ✨ Features

- **Agentic AI Search**: Uses multiple LLM calls to intelligently search for research papers
- **Multi-Source Search**: Searches across IEEE, arXiv, Google Scholar, and Semantic Scholar
- **Smart Query Processing**: Understands your research questions and finds the most relevant papers
- **One-Click Paper Opening**: Opens papers directly in new tabs
- **Beautiful UI**: Modern, intuitive interface with real-time chat
- **Paper Extraction**: Extract paper information from research sites with a floating button
- **Conversation Memory**: Remembers your search history for better results

## 🚀 Installation

### Prerequisites
- Google Chrome browser
- Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

### Steps

1. **Download the Extension**
   ```bash
   # Clone or download this repository
   git clone <repository-url>
   cd research-paper-ai-extension
   ```

2. **Load Extension in Chrome**
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode" (toggle in top right)
   - Click "Load unpacked"
   - Select the folder containing the extension files

3. **Configure API Key**
   - Click on the extension icon in your toolbar
   - Enter your Gemini API key when prompted
   - Or manually set it in Chrome storage:
     ```javascript
     chrome.storage.local.set({ gemini_api_key: 'your-api-key-here' });
     ```

## 🎯 Usage

### Basic Search
1. Click the extension icon in your Chrome toolbar
2. Type your research question or topic in the chat window
3. Press Enter or click "Search Papers"
4. The AI will find relevant papers and display them
5. Click "Open Paper" to view any paper in a new tab

### Example Queries
- "Find papers about transformer architecture in NLP"
- "Research on quantum computing algorithms"
- "Recent papers about machine learning in healthcare"
- "Papers about blockchain technology and security"

### Paper Extraction
- When visiting research sites (arXiv, IEEE, etc.), a floating 📄 button appears
- Click it to extract and save paper information
- Useful for building your personal research collection

## 🔧 How It Works

The extension uses an **agentic AI approach** with multiple LLM calls:

```
Query → LLM Response → Tool Call → Tool Result → Query → LLM Response → Tool Call → Tool Result → Final Result
```

### Agentic Process:
1. **Query Analysis**: LLM analyzes your research question
2. **Search Strategy**: Determines which sources to search
3. **Paper Search**: Calls search tools for different sources
4. **Result Filtering**: Ranks and filters the most relevant papers
5. **Final Delivery**: Returns the best matches with direct links

### Supported Sources:
- **arXiv**: Real-time search using arXiv API
- **IEEE**: Simulated search (can be enhanced with web scraping)
- **Google Scholar**: Simulated search (can be enhanced with web scraping)
- **Semantic Scholar**: Ready for integration

## 📁 File Structure

```
research-paper-ai-extension/
├── manifest.json          # Extension configuration
├── popup.html            # Main UI interface
├── popup.css             # Styling for the popup
├── popup.js              # Frontend logic
├── background.js         # Service worker with AI logic
├── content.js            # Content script for web interaction
├── config.js             # Configuration and setup
└── README.md             # This file
```

## 🛠️ Development

### Local Development
1. Make changes to the code
2. Go to `chrome://extensions/`
3. Click the refresh icon on your extension
4. Test your changes

### API Integration
The extension currently supports:
- **Gemini 2.0 Flash**: Primary LLM for agentic reasoning
- **ArXiv API**: Real paper search
- **IEEE/Google Scholar**: Simulated (ready for real integration)

### Adding New Sources
To add a new research source:
1. Add the source to `searchSource()` in `background.js`
2. Implement the search function
3. Update the system prompt in `buildConversationContext()`

## 🔒 Privacy & Security

- **API Key**: Stored locally in Chrome storage
- **No Data Collection**: Your queries and results stay on your device
- **Secure API Calls**: Uses HTTPS for all external requests
- **No Tracking**: Extension doesn't track or store your search history

## 🐛 Troubleshooting

### Common Issues

**Extension not working:**
- Check if API key is properly configured
- Verify internet connection
- Check Chrome console for errors

**No papers found:**
- Try rephrasing your query
- Be more specific about your research topic
- Check if the research sources are accessible

**API key errors:**
- Verify your Gemini API key is valid
- Check your API quota/limits
- Ensure the key has proper permissions

### Debug Mode
Enable debug logging:
```javascript
// In Chrome console on extension page
chrome.storage.local.set({ debug_mode: true });
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Areas for Improvement:
- Add more research sources (PubMed, ACM, etc.)
- Implement web scraping for IEEE and Google Scholar
- Add paper recommendation features
- Improve search algorithms
- Add export functionality for paper collections

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Gemini API for AI capabilities
- ArXiv for providing open access to research papers
- Chrome Extension API for the platform

## 📞 Support

If you encounter any issues or have questions:
1. Check the troubleshooting section above
2. Review the Chrome console for error messages
3. Create an issue in the repository

---

**Happy Researching! 🔬📚** 