// API Configuration for Research Paper AI Extension
// This file is for development purposes only
// DO NOT commit this file with your actual API key

// Replace 'your-api-key-here' with your actual Gemini API key
const API_CONFIG = {
    GEMINI_API_KEY: 'your-api-key-here' // Replace with your actual key
};

// Function to set the API key in Chrome storage
async function setAPIKey() {
    try {
        await chrome.storage.local.set({ gemini_api_key: API_CONFIG.GEMINI_API_KEY });
        console.log('✅ API key set successfully');
        return true;
    } catch (error) {
        console.error('❌ Error setting API key:', error);
        return false;
    }
}

// Function to get the API key from Chrome storage
async function getAPIKey() {
    try {
        const result = await chrome.storage.local.get(['gemini_api_key']);
        return result.gemini_api_key;
    } catch (error) {
        console.error('❌ Error getting API key:', error);
        return null;
    }
}

// Function to test the API key
async function testAPIKey() {
    const apiKey = await getAPIKey();
    if (!apiKey) {
        console.log('❌ No API key found');
        return false;
    }

    try {
        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                contents: [{
                    parts: [{
                        text: 'Hello, this is a test.'
                    }]
                }]
            })
        });

        if (response.ok) {
            console.log('✅ API key is working');
            return true;
        } else {
            console.log('❌ API key test failed');
            return false;
        }
    } catch (error) {
        console.error('❌ API test error:', error);
        return false;
    }
}

// Auto-set API key when this script is loaded
if (typeof chrome !== 'undefined' && chrome.storage) {
    setAPIKey().then(success => {
        if (success) {
            testAPIKey();
        }
    });
}

// Export functions for manual use
if (typeof window !== 'undefined') {
    window.API_CONFIG = API_CONFIG;
    window.setAPIKey = setAPIKey;
    window.getAPIKey = getAPIKey;
    window.testAPIKey = testAPIKey;
} 