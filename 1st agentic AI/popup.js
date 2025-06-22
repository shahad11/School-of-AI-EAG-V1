class ResearchPaperAI {
    constructor() {
        this.chatMessages = document.getElementById('chat-messages');
        this.userInput = document.getElementById('user-input');
        this.sendBtn = document.getElementById('send-btn');
        this.status = document.getElementById('status');
        this.conversationHistory = [];
        
        this.initializeEventListeners();
        this.checkAPIKey();
    }
    
    async checkAPIKey() {
        try {
            const result = await chrome.storage.local.get(['gemini_api_key']);
            if (!result.gemini_api_key) {
                this.showAPIKeyError();
            }
        } catch (error) {
            console.error('Error checking API key:', error);
        }
    }
    
    showAPIKeyError() {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'message system';
        errorDiv.innerHTML = `
            <div class="message-content" style="background: #ffebee; color: #c62828; border: 1px solid #ffcdd2;">
                <strong>⚠️ API Key Not Configured</strong><br>
                Please set your Gemini API key to use this extension.<br>
                <button id="open-options" style="
                    background: #667eea; 
                    color: white; 
                    border: none; 
                    padding: 8px 16px; 
                    border-radius: 4px; 
                    margin-top: 8px; 
                    cursor: pointer;
                ">Open Settings</button>
            </div>
        `;
        
        this.chatMessages.appendChild(errorDiv);
        
        // Add event listener to the button
        document.getElementById('open-options').addEventListener('click', () => {
            chrome.runtime.openOptionsPage();
        });
    }
    
    initializeEventListeners() {
        this.sendBtn.addEventListener('click', () => this.handleSendMessage());
        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSendMessage();
            }
        });
    }
    
    async handleSendMessage() {
        const message = this.userInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        this.userInput.value = '';
        
        // Disable input and show loading
        this.setLoading(true);
        this.updateStatus('Analyzing your query...', 'searching');
        
        try {
            // Send message to background script for processing
            const response = await chrome.runtime.sendMessage({
                action: 'processQuery',
                message: message,
                conversationHistory: this.conversationHistory
            });
            
            if (response.success) {
                this.updateStatus('Found relevant papers!', 'success');
                this.displayResults(response.results);
            } else {
                this.updateStatus('Error: ' + response.error, 'error');
                
                // Check if it's an API key error
                if (response.error && response.error.includes('API key')) {
                    this.addMessage('Please configure your Gemini API key in the extension settings. Click the extension icon and select "Options" to set up your API key.', 'assistant');
                } else {
                    this.addMessage('Sorry, I encountered an error while searching for papers. Please try again.', 'assistant');
                }
            }
        } catch (error) {
            console.error('Error processing query:', error);
            this.updateStatus('Connection error', 'error');
            this.addMessage('Sorry, I encountered a connection error. Please check your internet connection and try again.', 'assistant');
        } finally {
            this.setLoading(false);
        }
    }
    
    addMessage(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = content;
        
        messageDiv.appendChild(contentDiv);
        this.chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        
        // Add to conversation history
        this.conversationHistory.push({ role: sender, content: content });
    }
    
    displayResults(results) {
        if (!results || results.length === 0) {
            this.addMessage('I couldn\'t find any relevant papers for your query. Try rephrasing your question or being more specific.', 'assistant');
            return;
        }
        
        let response = `I found ${results.length} relevant paper${results.length > 1 ? 's' : ''} for you:\n\n`;
        
        results.forEach((paper, index) => {
            response += `${index + 1}. **${paper.title}**\n`;
            response += `   Authors: ${paper.authors}\n`;
            response += `   Source: ${paper.source}\n`;
            if (paper.abstract) {
                response += `   Abstract: ${paper.abstract.substring(0, 200)}...\n`;
            }
            response += `   [Read Paper](${paper.url})\n\n`;
        });
        
        this.addMessage(response, 'assistant');
        
        // Create paper result cards
        results.forEach((paper, index) => {
            this.createPaperCard(paper, index + 1);
        });
    }
    
    createPaperCard(paper, index) {
        const cardDiv = document.createElement('div');
        cardDiv.className = 'paper-result';
        
        const titleDiv = document.createElement('div');
        titleDiv.className = 'paper-title';
        titleDiv.textContent = `${index}. ${paper.title}`;
        
        const authorsDiv = document.createElement('div');
        authorsDiv.className = 'paper-authors';
        authorsDiv.textContent = `Authors: ${paper.authors}`;
        
        const sourceDiv = document.createElement('div');
        sourceDiv.className = 'paper-authors';
        sourceDiv.textContent = `Source: ${paper.source}`;
        
        const abstractDiv = document.createElement('div');
        abstractDiv.className = 'paper-abstract';
        abstractDiv.textContent = paper.abstract ? paper.abstract.substring(0, 150) + '...' : 'Abstract not available';
        
        const linkDiv = document.createElement('div');
        const link = document.createElement('a');
        link.className = 'paper-link';
        link.textContent = 'Open Paper';
        link.href = paper.url;
        link.target = '_blank';
        link.addEventListener('click', (e) => {
            e.preventDefault();
            chrome.tabs.create({ url: paper.url });
        });
        linkDiv.appendChild(link);
        
        cardDiv.appendChild(titleDiv);
        cardDiv.appendChild(authorsDiv);
        cardDiv.appendChild(sourceDiv);
        cardDiv.appendChild(abstractDiv);
        cardDiv.appendChild(linkDiv);
        
        this.chatMessages.appendChild(cardDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    setLoading(loading) {
        this.sendBtn.disabled = loading;
        this.userInput.disabled = loading;
        
        const btnText = this.sendBtn.querySelector('.btn-text');
        const spinner = this.sendBtn.querySelector('.loading-spinner');
        
        if (loading) {
            btnText.style.display = 'none';
            spinner.style.display = 'inline';
        } else {
            btnText.style.display = 'inline';
            spinner.style.display = 'none';
        }
    }
    
    updateStatus(message, type = '') {
        this.status.textContent = message;
        this.status.className = `status ${type}`;
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ResearchPaperAI();
}); 