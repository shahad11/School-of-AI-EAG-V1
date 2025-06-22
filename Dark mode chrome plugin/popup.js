document.addEventListener('DOMContentLoaded', function() {
  const toggle = document.getElementById('darkModeToggle');

  // Load saved state
  chrome.storage.sync.get(['darkMode'], function(result) {
    toggle.checked = result.darkMode || false;
  });

  // Save state when toggled
  toggle.addEventListener('change', function() {
    const isDarkMode = toggle.checked;
    chrome.storage.sync.set({ darkMode: isDarkMode });

    // Send message to content script with error handling
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
      if (tabs[0]) {
        chrome.tabs.sendMessage(tabs[0].id, {
          action: 'toggleDarkMode',
          isDarkMode: isDarkMode
        }).catch(error => {
          // If content script is not loaded, inject it
          if (error.message.includes('Receiving end does not exist')) {
            chrome.scripting.executeScript({
              target: { tabId: tabs[0].id },
              files: ['content.js']
            }).then(() => {
              // Retry sending the message after script injection
              chrome.tabs.sendMessage(tabs[0].id, {
                action: 'toggleDarkMode',
                isDarkMode: isDarkMode
              });
            }).catch(err => {
              console.error('Failed to inject content script:', err);
            });
          }
        });
      }
    });
  });
}); 