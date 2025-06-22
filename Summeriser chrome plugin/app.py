from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Get API key and verify it exists
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# Initialize Gemini client
genai.configure(api_key=api_key)

@app.route('/')
def home():
    return jsonify({
        'status': 'running',
        'message': 'Web Page Summarizer API is running',
        'endpoints': {
            '/summarize': 'POST - Send webpage content for summarization'
        }
    })

@app.route('/summarize', methods=['POST'])
def summarize():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        content = data.get('content', '')

        if not content:
            return jsonify({'error': 'No content provided'}), 400

        # Truncate content if it's too long (Gemini has a context limit)
        max_length = 30000  # Adjust based on Gemini's limits
        if len(content) > max_length:
            content = content[:max_length] + "... (truncated)"

        # Generate summary using Gemini
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Create the prompt
        prompt = f"""Please provide a concise summary of the following text. 
        Focus on the main points and key information. 
        Keep the summary clear and easy to understand.

        Text to summarize:
        {content}"""

        # Generate the summary
        response = model.generate_content(prompt)
        
        if not response or not response.text:
            return jsonify({'error': 'Failed to generate summary'}), 500

        return jsonify({'summary': response.text})

    except Exception as e:
        print(f"Error in summarize endpoint: {str(e)}")  # Add logging
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Flask server...")
    print("API is running at http://localhost:5000")
    print("Available endpoints:")
    print("- GET  /")
    print("- POST /summarize")
    app.run(debug=True) 