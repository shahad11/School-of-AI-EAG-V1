document.addEventListener('DOMContentLoaded', () => {
  const summarizeBtn = document.getElementById('summarizeBtn');
  const loadingDiv = document.getElementById('loading');
  const errorDiv = document.getElementById('error');
  const summaryDiv = document.getElementById('summary');

  summarizeBtn.addEventListener('click', async () => {
    try {
      // Show loading state
      summarizeBtn.disabled = true;
      loadingDiv.style.display = 'block';
      errorDiv.style.display = 'none';
      summaryDiv.style.display = 'none';

      // Get the active tab
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      if (!tab) {
        throw new Error('No active tab found');
      }

      // Inject content script if not already injected
      try {
        await chrome.scripting.executeScript({
          target: { tabId: tab.id },
          files: ['content.js']
        });
      } catch (err) {
        console.log('Content script already injected or injection failed:', err);
      }

      // Get page content
      const response = await new Promise((resolve, reject) => {
        chrome.tabs.sendMessage(tab.id, { action: 'getPageContent' }, (response) => {
          if (chrome.runtime.lastError) {
            reject(new Error(chrome.runtime.lastError.message));
          } else {
            resolve(response);
          }
        });
      });

      if (!response || !response.content) {
        throw new Error('Failed to get page content');
      }

      // Send to backend
      const backendResponse = await fetch('http://localhost:5000/summarize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content: response.content }),
      });

      if (!backendResponse.ok) {
        throw new Error('Failed to get summary from server');
      }

      const data = await backendResponse.json();

      // Display summary
      summaryDiv.textContent = data.summary;
      summaryDiv.style.display = 'block';
    } catch (error) {
      console.error('Error:', error);
      errorDiv.textContent = error.message || 'An error occurred while summarizing the page';
      errorDiv.style.display = 'block';
    } finally {
      // Reset UI state
      summarizeBtn.disabled = false;
      loadingDiv.style.display = 'none';
    }
  });
}); 