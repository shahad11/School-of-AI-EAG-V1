// Content script for Research Paper AI
// This script can interact with web pages and extract paper information

class ContentScript {
    constructor() {
        this.initialize();
    }
    
    initialize() {
        // Listen for messages from the extension
        chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
            if (request.action === 'extractPaperInfo') {
                const paperInfo = this.extractPaperInfo();
                sendResponse({ success: true, paperInfo });
            }
        });
        
        // Add context menu for paper extraction
        this.addContextMenu();
    }
    
    extractPaperInfo() {
        const paperInfo = {
            title: '',
            authors: '',
            abstract: '',
            url: window.location.href,
            source: this.detectSource()
        };
        
        // Extract based on the current site
        switch (paperInfo.source) {
            case 'arxiv':
                return this.extractArxivInfo();
            case 'ieee':
                return this.extractIEEEInfo();
            case 'scholar':
                return this.extractScholarInfo();
            default:
                return this.extractGenericInfo();
        }
    }
    
    detectSource() {
        const url = window.location.href;
        if (url.includes('arxiv.org')) return 'arxiv';
        if (url.includes('ieeexplore.ieee.org')) return 'ieee';
        if (url.includes('scholar.google.com')) return 'scholar';
        return 'unknown';
    }
    
    extractArxivInfo() {
        return {
            title: this.getTextContent('h1.title') || this.getTextContent('.title'),
            authors: this.getTextContent('.authors') || this.getTextContent('.author'),
            abstract: this.getTextContent('.abstract') || this.getTextContent('.summary'),
            url: window.location.href,
            source: 'arXiv'
        };
    }
    
    extractIEEEInfo() {
        return {
            title: this.getTextContent('h1') || this.getTextContent('.document-title'),
            authors: this.getTextContent('.authors') || this.getTextContent('.author'),
            abstract: this.getTextContent('.abstract') || this.getTextContent('.description'),
            url: window.location.href,
            source: 'IEEE'
        };
    }
    
    extractScholarInfo() {
        return {
            title: this.getTextContent('h3') || this.getTextContent('.gs_rt'),
            authors: this.getTextContent('.gs_a') || this.getTextContent('.author'),
            abstract: this.getTextContent('.gs_rs') || this.getTextContent('.abstract'),
            url: window.location.href,
            source: 'Google Scholar'
        };
    }
    
    extractGenericInfo() {
        return {
            title: this.getTextContent('h1') || this.getTextContent('title'),
            authors: this.getTextContent('.author') || this.getTextContent('.authors'),
            abstract: this.getTextContent('.abstract') || this.getTextContent('.summary'),
            url: window.location.href,
            source: 'Unknown'
        };
    }
    
    getTextContent(selector) {
        const element = document.querySelector(selector);
        return element ? element.textContent.trim() : '';
    }
    
    addContextMenu() {
        // Add a floating button for quick paper extraction
        const button = document.createElement('div');
        button.innerHTML = '📄';
        button.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            z-index: 10000;
            font-size: 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            transition: transform 0.2s;
        `;
        
        button.addEventListener('mouseenter', () => {
            button.style.transform = 'scale(1.1)';
        });
        
        button.addEventListener('mouseleave', () => {
            button.style.transform = 'scale(1)';
        });
        
        button.addEventListener('click', () => {
            this.handlePaperExtraction();
        });
        
        // Only show on research sites
        if (this.detectSource() !== 'unknown') {
            document.body.appendChild(button);
        }
    }
    
    async handlePaperExtraction() {
        const paperInfo = this.extractPaperInfo();
        
        // Send to background script for processing
        chrome.runtime.sendMessage({
            action: 'savePaper',
            paperInfo: paperInfo
        }, (response) => {
            if (response.success) {
                this.showNotification('Paper saved to your collection!', 'success');
            } else {
                this.showNotification('Failed to save paper', 'error');
            }
        });
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            background: ${type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : '#2196f3'};
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            z-index: 10001;
            font-size: 14px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            animation: slideIn 0.3s ease-out;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Initialize content script
new ContentScript(); 