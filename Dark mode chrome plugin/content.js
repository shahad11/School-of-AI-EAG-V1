// Initialize dark mode state
let isDarkModeEnabled = false;

// Function to apply dark mode
function applyDarkMode() {
  if (isDarkModeEnabled) return; // Prevent duplicate application
  isDarkModeEnabled = true;

  const style = document.createElement('style');
  style.id = 'dark-mode-style';
  style.textContent = `
    /* Base dark mode styles */
    :root {
      color-scheme: dark;
    }

    /* Global dark mode */
    html, body {
      background-color: #1a1a1a !important;
      color: #ffffff !important;
    }

    /* Text and content elements */
    p, h1, h2, h3, h4, h5, h6, span, div, li, td, th, label, strong, em, b, i {
      color: #ffffff !important;
    }

    /* Links */
    a {
      color: #4a9eff !important;
    }
    a:hover {
      color: #66b3ff !important;
    }

    /* Form elements */
    input:not([type="image"]), 
    textarea, 
    select,
    button,
    [role="button"],
    [type="button"],
    [type="submit"] {
      background-color: #2d2d2d !important;
      color: #ffffff !important;
      border-color: #404040 !important;
    }

    /* Tables */
    table, th, td {
      border-color: #404040 !important;
      background-color: #2d2d2d !important;
    }

    /* Code blocks */
    pre, code {
      background-color: #2d2d2d !important;
      color: #e0e0e0 !important;
    }

    /* Blockquotes */
    blockquote {
      border-left-color: #404040 !important;
      background-color: #2d2d2d !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
      width: 12px;
      background-color: #1a1a1a;
    }

    ::-webkit-scrollbar-thumb {
      background-color: #404040;
      border-radius: 6px;
    }

    ::-webkit-scrollbar-thumb:hover {
      background-color: #505050;
    }

    /* Cards and containers */
    [class*="card"],
    [class*="container"],
    [class*="wrapper"],
    [class*="box"],
    [class*="panel"],
    [class*="section"],
    [class*="content"],
    [class*="main"],
    [class*="sidebar"],
    [class*="header"],
    [class*="footer"],
    [class*="nav"],
    [class*="menu"] {
      background-color: #2d2d2d !important;
      color: #ffffff !important;
    }

    /* Images and media */
    img:not([src*="youtube.com"]):not([src*="ytimg.com"]) {
      filter: brightness(0.8) !important;
    }

    /* YouTube specific fixes */
    ytd-thumbnail img,
    ytd-video-preview img,
    ytd-playlist-thumbnail img,
    yt-img-shadow img {
      filter: none !important;
      opacity: 1 !important;
    }

    /* Excel specific fixes */
    .ms-Excel, 
    .ms-ExcelOnline,
    [class*="excel-"],
    [class*="Excel-"],
    [class*="spreadsheet"],
    [class*="Spreadsheet"] {
      background-color: #ffffff !important;
      color: #000000 !important;
    }

    /* Exclude certain elements */
    .no-dark-mode,
    [class*="light-mode"],
    [class*="LightMode"],
    [class*="excel-"],
    [class*="Excel-"] {
      background-color: initial !important;
      color: initial !important;
    }
  `;
  document.head.appendChild(style);

  // Function to handle dynamic content
  function handleDynamicContent(node) {
    if (!node || !node.nodeType) return;

    // Handle YouTube specific elements
    if (window.location.hostname.includes('youtube.com')) {
      const thumbnails = node.querySelectorAll('ytd-thumbnail img, ytd-video-preview img, ytd-playlist-thumbnail img');
      thumbnails.forEach(img => {
        img.style.filter = 'none';
        img.style.opacity = '1';
      });
    }

    // Handle Excel specific elements
    if (window.location.hostname.includes('excel.office.com') || 
        window.location.hostname.includes('onedrive.live.com')) {
      const excelElements = node.querySelectorAll('[class*="excel-"], [class*="Excel-"]');
      excelElements.forEach(el => {
        el.style.backgroundColor = '#ffffff';
        el.style.color = '#000000';
      });
    }

    // Handle general dynamic content
    const elements = node.querySelectorAll('div, p, span, h1, h2, h3, h4, h5, h6, li, td, th');
    elements.forEach(el => {
      if (!el.closest('.no-dark-mode') && 
          !el.closest('[class*="excel-"]') && 
          !el.closest('[class*="Excel-"]')) {
        el.style.color = '#ffffff';
      }
    });
  }

  // Create and start observers
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (mutation.addedNodes.length) {
        mutation.addedNodes.forEach(handleDynamicContent);
      }
    });
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });

  // Initial processing of existing content
  handleDynamicContent(document.body);
}

// Function to remove dark mode
function removeDarkMode() {
  if (!isDarkModeEnabled) return; // Prevent duplicate removal
  isDarkModeEnabled = false;
  
  const style = document.getElementById('dark-mode-style');
  if (style) {
    style.remove();
  }
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  if (request.action === 'toggleDarkMode') {
    if (request.isDarkMode) {
      applyDarkMode();
    } else {
      removeDarkMode();
    }
    // Send response to confirm message received
    sendResponse({ success: true });
  }
  return true; // Keep the message channel open for async response
});

// Check initial state when page loads
chrome.storage.sync.get(['darkMode'], function(result) {
  if (result.darkMode) {
    applyDarkMode();
  }
}); 