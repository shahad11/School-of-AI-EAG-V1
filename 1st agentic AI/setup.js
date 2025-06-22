// Setup page JavaScript for Research Paper AI Extension

class SetupPage {
    constructor() {
        this.apiKeyInput = document.getElementById('api-key');
        this.saveBtn = document.getElementById('save-btn');
        this.testBtn = document.getElementById('test-btn');
        this.status = document.getElementById('status');
        
        this.initializeEventListeners();
        this.loadExistingKey();
    }
    
    initializeEventListeners() {
        this.saveBtn.addEventListener('click', (e) => {
            e.preventDefault();
            this.saveConfiguration();
        });
        
        this.testBtn.addEventListener('click', () => {
            this.testConnection();
        });
        
        // Enter key to save
        this.apiKeyInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.saveConfiguration();
            }
        });
    }
    
    async loadExistingKey() {
        try {
            const result = await chrome.storage.local.get(['gemini_api_key']);
            if (result.gemini_api_key) {
                this.apiKeyInput.value = result.gemini_api_key;
                this.showStatus('API key loaded from storage', 'info');
            }
        } catch (error) {
            console.log('No existing API key found');
        }
    }
    
    async saveConfiguration() {
        const apiKey = this.apiKeyInput.value.trim();
        
        if (!apiKey) {
            this.showStatus('Please enter your API key', 'error');
            return;
        }
        
        this.saveBtn.disabled = true;
        this.saveBtn.textContent = 'Saving...';
        
        try {
            // Save to Chrome storage
            await chrome.storage.local.set({ gemini_api_key: apiKey });
            
            // Test the API key
            const isValid = await this.testAPIKey(apiKey);
            
            if (isValid) {
                this.showStatus('✅ Configuration saved successfully! Your extension is ready to use.', 'success');
                this.saveBtn.textContent = 'Saved!';
                
                // Show success animation
                setTimeout(() => {
                    this.saveBtn.textContent = 'Save Configuration';
                    this.saveBtn.disabled = false;
                }, 2000);
            } else {
                this.showStatus('❌ Invalid API key. Please check your key and try again.', 'error');
                this.saveBtn.textContent = 'Save Configuration';
                this.saveBtn.disabled = false;
            }
        } catch (error) {
            this.showStatus('❌ Error saving configuration: ' + error.message, 'error');
            this.saveBtn.textContent = 'Save Configuration';
            this.saveBtn.disabled = false;
        }
    }
    
    async testConnection() {
        const apiKey = this.apiKeyInput.value.trim();
        
        if (!apiKey) {
            this.showStatus('Please enter your API key first', 'error');
            return;
        }
        
        this.testBtn.disabled = true;
        this.testBtn.textContent = 'Testing...';
        
        try {
            const isValid = await this.testAPIKey(apiKey);
            
            if (isValid) {
                this.showStatus('✅ Connection successful! Your API key is working.', 'success');
            } else {
                this.showStatus('❌ Connection failed. Please check your API key.', 'error');
            }
        } catch (error) {
            this.showStatus('❌ Test failed: ' + error.message, 'error');
        } finally {
            this.testBtn.textContent = 'Test Connection';
            this.testBtn.disabled = false;
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
                            text: 'Hello, this is a test message to verify the API connection.'
                        }]
                    }],
                    generationConfig: {
                        temperature: 0.1,
                        maxOutputTokens: 50
                    }
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`API Error: ${errorData.error?.message || response.statusText}`);
            }
            
            const data = await response.json();
            return data.candidates && data.candidates.length > 0;
        } catch (error) {
            console.error('API test error:', error);
            return false;
        }
    }
    
    showStatus(message, type = 'info') {
        this.status.textContent = message;
        this.status.className = `status ${type}`;
        this.status.style.display = 'block';
        
        // Auto-hide success messages after 5 seconds
        if (type === 'success') {
            setTimeout(() => {
                this.status.style.display = 'none';
            }, 5000);
        }
    }
    
    hideStatus() {
        this.status.style.display = 'none';
    }
}

// Initialize setup page when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SetupPage();
});

// Add some helpful tips
document.addEventListener('DOMContentLoaded', () => {
    // Add helpful tips to the page
    const tips = [
        '💡 Make sure your API key is from Google AI Studio',
        '💡 The API key should start with "AI"',
        '💡 Keep your API key secure and don\'t share it',
        '💡 You can always update your key later'
    ];
    
    const tipsContainer = document.createElement('div');
    tipsContainer.style.cssText = `
        margin-top: 20px;
        padding: 16px;
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
    `;
    
    tipsContainer.innerHTML = `
        <h4 style="color: #856404; margin-bottom: 8px;">💡 Tips:</h4>
        <ul style="color: #856404; font-size: 14px; padding-left: 20px;">
            ${tips.map(tip => `<li>${tip}</li>`).join('')}
        </ul>
    `;
    
    document.querySelector('.test-section').appendChild(tipsContainer);
}); 