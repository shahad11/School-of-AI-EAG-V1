function extractPageContent() {
  // Create a clone of the body to avoid modifying the actual page
  const bodyClone = document.body.cloneNode(true);
  
  // Remove unwanted elements
  const elementsToRemove = bodyClone.querySelectorAll('script, style, nav, footer, header, iframe, [role="navigation"], [role="banner"], [role="complementary"], .ad, .advertisement, .banner, .sidebar, .menu, .navigation, .footer, .header');
  elementsToRemove.forEach(el => el.remove());

  // Get all text content
  const bodyText = bodyClone.innerText;
  
  // Clean up the text
  const cleanedText = bodyText
    .replace(/\s+/g, ' ')  // Replace multiple spaces with single space
    .replace(/\n+/g, '\n') // Replace multiple newlines with single newline
    .trim();

  return cleanedText;
}

// Listen for messages from the popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getPageContent') {
    try {
      const content = extractPageContent();
      sendResponse({ content });
    } catch (error) {
      console.error('Error extracting content:', error);
      sendResponse({ error: error.message });
    }
  }
  return true; // Keep the message channel open for async response
}); 