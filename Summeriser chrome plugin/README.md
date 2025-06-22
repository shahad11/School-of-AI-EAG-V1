# Web Page Summarizer Chrome Extension

A Chrome extension that summarizes web pages using Google's Gemini AI. The extension extracts text content from the current page and sends it to a local Flask backend, which uses the Gemini API to generate a concise summary.

## Features

- One-click webpage summarization
- Clean and simple UI
- Secure API key handling
- Error handling and loading states
- CORS support for local development
- Uses Gemini 2.0 Flash model for fast and accurate summaries

## Prerequisites

- Python 3.8 or higher
- Chrome browser
- Gemini API key (Get it from [Google AI Studio](https://makersuite.google.com/app/apikey))

## Project Structure

```
.
├── manifest.json          # Chrome extension manifest
├── popup.html            # Extension popup UI
├── popup.js             # Popup interaction logic
├── content.js           # Content script for page text extraction
├── app.py              # Flask backend
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (API key)
└── icons/             # Extension icons
    ├── icon16.png
    ├── icon48.png
    └── icon128.png
```

## Setup Instructions

### 1. Clone or Download the Project

Download or clone this repository to your local machine.

### 2. Set Up Python Environment

1. Open PowerShell as Administrator:
   - Press Windows key
   - Type "PowerShell"
   - Right-click and select "Run as administrator"

2. Set PowerShell execution policy:
   ```powershell
   Set-ExecutionPolicy RemoteSigned
   ```
   Type 'Y' when prompted

3. Navigate to the project directory:
   ```powershell
   cd "path\to\your\project"
   ```

4. Create and activate virtual environment:
   ```powershell
   python -m venv venv
   venv\Scripts\activate
   ```

5. Install required packages:
   ```powershell
   pip install -r requirements.txt
   ```

### 3. Configure API Key

1. Create a `.env` file in the project root:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
   Replace `your_api_key_here` with your actual Gemini API key

2. Test the API key:
   ```powershell
   python test_api.py
   ```
   This should show available models and a test response

### 4. Start the Backend Server

1. With the virtual environment activated, run:
   ```powershell
   python app.py
   ```
   You should see:
   ```
   Starting Flask server...
   API is running at http://localhost:5000
   Available endpoints:
   - GET  /
   - POST /summarize
   ```

### 5. Load the Chrome Extension

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the project directory containing the extension files

### 6. Create Extension Icons

Create an `icons` directory and add three icon files:
- `icon16.png` (16x16 pixels)
- `icon48.png` (48x48 pixels)
- `icon128.png` (128x128 pixels)

You can create these using any image editor or icon generator.

## Using the Extension

1. Navigate to any webpage you want to summarize
2. Click the extension icon in the Chrome toolbar
3. Click the "Summarize Page" button
4. Wait for the summary to appear in the popup

## How It Works

1. **Content Extraction**:
   - The extension extracts text content from the current webpage
   - Removes unwanted elements (scripts, styles, navigation, etc.)
   - Cleans and formats the text

2. **Backend Processing**:
   - Sends the cleaned text to the Flask backend
   - Backend uses Gemini 2.0 Flash model to generate a summary
   - Returns the summary to the extension

3. **Display**:
   - Shows the summary in the extension popup
   - Handles errors and loading states

## Troubleshooting

### Common Issues

1. **"Could not establish connection" error**:
   - Make sure the Flask backend is running
   - Check if the extension is properly loaded
   - Verify the content script is injected

2. **API Key Issues**:
   - Verify the API key in `.env` file
   - Check if the key is valid using `test_api.py`
   - Ensure the key has proper permissions

3. **Backend Connection Issues**:
   - Verify Flask server is running on port 5000
   - Check CORS settings
   - Ensure no other service is using port 5000

### Debugging

1. **Chrome Extension**:
   - Open Chrome DevTools (F12)
   - Go to Console tab
   - Look for error messages

2. **Backend**:
   - Check Flask server console for errors
   - Verify API responses
   - Check Python error logs

## Security Notes

- API key is stored securely in the backend
- CORS is enabled only for local development
- Content is truncated if it exceeds model limits
- No sensitive data is stored

## Development

### Adding Features

1. **Modify Extension**:
   - Edit `popup.html` for UI changes
   - Update `content.js` for content extraction
   - Modify `popup.js` for new functionality

2. **Update Backend**:
   - Edit `app.py` for new endpoints
   - Add new dependencies to `requirements.txt`

### Testing

1. Test the API:
   ```powershell
   python test_api.py
   ```

2. Test the backend:
   ```powershell
   curl http://localhost:5000
   ```

3. Test the extension:
   - Reload the extension after changes
   - Test on different types of webpages

## License

MIT License

## Contributing

Feel free to submit issues and enhancement requests! 