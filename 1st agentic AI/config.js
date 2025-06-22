// Configuration file for Research Paper AI Extension
// This file helps users configure their API key and other settings

class Config {
    constructor() {
        this.initializeConfig();
    }
    
    async initializeConfig() {
        // Check if API key is already set
        const result = await chrome.storage.local.get(['gemini_api_key']);
        if (!result.gemini_api_key) {
            this.showSetupModal();
        }
    }
    
    showSetupModal() {
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 100000;
        `;
        
        const content = document.createElement('div');
        content.style.cssText = `
            background: white;
            padding: 30px;
            border-radius: 12px;
            max-width: 500px;
            width: 90%;
            text-align: center;
        `;
        
        content.innerHTML = `
            <h2 style="color: #667eea; margin-bottom: 20px;">🔬 Research Paper AI Setup</h2>
            <p style="margin-bottom: 20px; color: #666;">
                To use this extension, you need to configure your Gemini API key.
            </p>
            <div style="margin-bottom: 20px;">
                <label style="display: block; margin-bottom: 8px; font-weight: 600;">Gemini API Key:</label>
                <input type="password" id="api-key-input" placeholder="Enter your Gemini API key" 
                       style="width: 100%; padding: 12px; border: 2px solid #e1e5e9; border-radius: 8px; font-size: 14px;">
            </div>
            <div style="margin-bottom: 20px;">
                <a href="https://aistudio.google.com/app/apikey" target="_blank" 
                   style="color: #667eea; text-decoration: none; font-size: 14px;">
                    🔑 Get your API key from Google AI Studio
                </a>
            </div>
            <button id="save-config" style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                margin-right: 10px;
            ">Save Configuration</button>
            <button id="skip-config" style="
                background: #f5f5f5;
                color: #666;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                cursor: pointer;
            ">Skip for Now</button>
        `;
        
        modal.appendChild(content);
        document.body.appendChild(modal);
        
        // Event listeners
        document.getElementById('save-config').addEventListener('click', () => {
            this.saveAPIKey();
        });
        
        document.getElementById('skip-config').addEventListener('click', () => {
            document.body.removeChild(modal);
        });
        
        // Enter key to save
        document.getElementById('api-key-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.saveAPIKey();
            }
        });
    }
    
    async saveAPIKey() {
        const apiKey = document.getElementById('api-key-input').value.trim();
        
        if (!apiKey) {
            alert('Please enter your API key');
            return;
        }
        
        try {
            await chrome.storage.local.set({ gemini_api_key: apiKey });
            
            // Test the API key
            const isValid = await this.testAPIKey(apiKey);
            
            if (isValid) {
                this.showSuccessMessage();
                document.body.removeChild(document.querySelector('div[style*="position: fixed"]'));
            } else {
                alert('Invalid API key. Please check your key and try again.');
            }
        } catch (error) {
            alert('Error saving API key: ' + error.message);
        }
    }
    
    async testAPIKey(apiKey) {
        try {
            const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    contents: [{
                        parts: [{
                            text: 'Hello'
                        }]
                    }]
                })
            });
            
            return response.ok;
        } catch (error) {
            return false;
        }
    }
    
    showSuccessMessage() {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #4caf50;
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            z-index: 100001;
            font-size: 14px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        `;
        notification.textContent = '✅ API key configured successfully!';
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 3000);
    }
}

// Initialize configuration when the script loads
if (typeof chrome !== 'undefined' && chrome.storage) {
    new Config();
} 