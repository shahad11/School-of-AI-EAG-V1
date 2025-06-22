// Background service worker for Research Paper AI
class AgenticAI {
    constructor() {
        this.apiKey = null;
        this.maxIterations = 5;
        this.conversationHistory = [];
        console.log('🔬 AgenticAI constructor called');
        this.initializeAPIKey();
    }
    
    async initializeAPIKey() {
        console.log('🔄 Initializing API key...');
        try {
            // Try to get API key from storage
            const result = await chrome.storage.local.get(['gemini_api_key']);
            console.log('📦 Storage result:', result);
            
            if (result.gemini_api_key) {
                this.apiKey = result.gemini_api_key;
                console.log('✅ API key loaded from storage:', this.apiKey.substring(0, 10) + '...');
            } else {
                console.warn('⚠️ API key not found in storage. Please configure it.');
                console.log('🔍 Available storage keys:', Object.keys(result));
            }
        } catch (error) {
            console.error('❌ Error loading API key:', error);
        }
    }
    
    async processQuery(message, conversationHistory) {
        console.log('📝 Processing query:', message);
        console.log('🔑 Current API key status:', this.apiKey ? 'SET' : 'NOT SET');
        
        try {
            // Re-check API key before processing
            if (!this.apiKey) {
                console.log('🔄 Re-checking API key...');
                await this.initializeAPIKey();
            }
            
            if (!this.apiKey) {
                console.error('❌ API key still not available after re-check');
                throw new Error('API key not configured. Please set your Gemini API key in the extension options.');
            }
            
            console.log('✅ API key is available, proceeding with query');
            this.conversationHistory = conversationHistory || [];
            this.conversationHistory.push({ role: 'user', content: message });
            
            const results = await this.runAgenticSearch(message);
            return { success: true, results };
        } catch (error) {
            console.error('❌ Error in processQuery:', error);
            return { success: false, error: error.message };
        }
    }
    
    async runAgenticSearch(query) {
        let currentQuery = query;
        let iteration = 0;
        let searchResults = [];
        
        while (iteration < this.maxIterations) {
            console.log(`--- Iteration ${iteration + 1} ---`);
            
            // Build the full conversation context
            const fullContext = this.buildConversationContext(currentQuery);
            
            // Get LLM response
            const llmResponse = await this.callLLM(fullContext);
            console.log('LLM Response:', llmResponse);
            
            // Parse the response
            const parsedResponse = this.parseLLMResponse(llmResponse);
            
            if (parsedResponse.type === 'FINAL_ANSWER') {
                // Final answer - return the results
                console.log('✅ Got final answer, returning results');
                return searchResults;
            } else if (parsedResponse.type === 'TOOL_CALL') {
                // Execute tool call
                console.log('🔧 Executing tool:', parsedResponse.tool);
                const toolResult = await this.executeTool(parsedResponse.tool, parsedResponse.params);
                console.log('Tool Result:', toolResult);
                
                // Add to conversation history
                this.conversationHistory.push({ 
                    role: 'assistant', 
                    content: `Called ${parsedResponse.tool} with params: ${JSON.stringify(parsedResponse.params)}` 
                });
                this.conversationHistory.push({ 
                    role: 'system', 
                    content: `Tool result: ${JSON.stringify(toolResult)}` 
                });
                
                // Update search results if papers were found
                if (toolResult.papers) {
                    searchResults = toolResult.papers;
                }
                
                // Prepare next query
                currentQuery = `Previous query: ${query}\nTool called: ${parsedResponse.tool}\nTool result: ${JSON.stringify(toolResult)}\nWhat should I do next?`;
            } else {
                // Invalid response format - treat as final answer
                console.log('⚠️ Unexpected response type, treating as final answer');
                return searchResults;
            }
            
            iteration++;
        }
        
        // If we reach max iterations, return what we have
        console.log('⏰ Reached max iterations, returning current results');
        return searchResults;
    }
    
    buildConversationContext(currentQuery) {
        const systemPrompt = `You are a research paper search agent. You can search for academic papers from IEEE, arXiv, Google Scholar, and Semantic Scholar.

Available tools:
1. SEARCH_PAPERS(query, source) - Search for papers using the given query and source (ieee, arxiv, scholar, semantic)
2. FINAL_ANSWER - Provide the final results

IMPORTANT: You MUST respond with EXACTLY ONE of these formats:

For tool calls:
TOOL_CALL: tool_name|{"param1": "value1", "param2": "value2"}

For final answers:
FINAL_ANSWER: your final response here

Examples:
- TOOL_CALL: SEARCH_PAPERS|{"query": "machine learning", "source": "all"}
- FINAL_ANSWER: Here are the research papers I found...

Search strategy:
1. First, analyze the user's query to understand what they're looking for
2. Search multiple sources to get comprehensive results
3. Filter and rank the most relevant papers
4. Return the best matches

Always respond with exactly one action per iteration. Do not include any other text or formatting.`;

        let context = systemPrompt + '\n\n';
        
        // Add conversation history
        this.conversationHistory.forEach(msg => {
            context += `${msg.role.toUpperCase()}: ${msg.content}\n`;
        });
        
        context += `\nCurrent query: ${currentQuery}\n`;
        
        return context;
    }
    
    async callLLM(context) {
        if (!this.apiKey) {
            throw new Error('API key not configured');
        }
        
        console.log('🔑 Using API key:', this.apiKey.substring(0, 10) + '...');
        
        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${this.apiKey}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                contents: [{
                    parts: [{
                        text: context
                    }]
                }],
                generationConfig: {
                    temperature: 0.1,
                    maxOutputTokens: 1000
                }
            })
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('API Error Response:', errorText);
            throw new Error(`API call failed: ${response.status} - ${errorText}`);
        }
        
        const data = await response.json();
        return data.candidates[0].content.parts[0].text;
    }
    
    parseLLMResponse(response) {
        console.log('🔍 Parsing LLM response:', response);
        
        // Clean up the response
        const cleanResponse = response.trim();
        const lines = cleanResponse.split('\n');
        const firstLine = lines[0].trim();
        
        console.log('📝 First line:', firstLine);
        
        // Check for TOOL_CALL format
        if (firstLine.startsWith('TOOL_CALL:')) {
            const parts = firstLine.split(':', 2)[1].split('|');
            const tool = parts[0].trim();
            let params;

            if (parts[1]) {
                const paramsString = parts[1].trim();
                try {
                    // Try to parse as JSON first
                    params = JSON.parse(paramsString);
                    console.log('🔧 Parsed tool call with JSON params:', { tool, params });
                } catch (error) {
                    // If JSON parsing fails, assume it's a simple string for the 'query' parameter
                    console.warn('⚠️ JSON parsing failed for params. Assuming simple string query.', error.message);
                    params = { "query": paramsString, "source": "all" }; // Fallback for simple string
                    console.log('🔧 Parsed tool call with fallback params:', { tool, params });
                }
            } else {
                params = {};
            }

            return { type: 'TOOL_CALL', tool, params };
        } 
        // Check for FINAL_ANSWER format
        else if (firstLine.startsWith('FINAL_ANSWER:')) {
            const results = firstLine.split(':', 2)[1].trim();
            console.log('✅ Parsed final answer:', results);
            return { type: 'FINAL_ANSWER', results };
        }
        // Handle case where LLM gives a direct response without our format
        else {
            console.log('⚠️ LLM didn\'t use expected format, treating as final answer');
            return { type: 'FINAL_ANSWER', results: cleanResponse };
        }
    }
    
    async executeTool(toolName, params) {
        switch (toolName) {
            case 'SEARCH_PAPERS':
                return await this.searchPapers(params.query, params.source);
            default:
                throw new Error(`Unknown tool: ${toolName}`);
        }
    }
    
    async searchPapers(query, source = 'all') {
        const sources = source === 'all' ? ['arxiv', 'ieee', 'scholar'] : [source];
        let allPapers = [];
        
        for (const src of sources) {
            try {
                const papers = await this.searchSource(query, src);
                allPapers = allPapers.concat(papers);
            } catch (error) {
                console.error(`Error searching ${src}:`, error);
            }
        }
        
        // Remove duplicates and limit results
        const uniquePapers = this.removeDuplicates(allPapers);
        return { papers: uniquePapers.slice(0, 5) };
    }
    
    async searchSource(query, source) {
        switch (source) {
            case 'arxiv':
                return await this.searchArxiv(query);
            case 'ieee':
                return await this.searchIEEE(query);
            case 'scholar':
                return await this.searchGoogleScholar(query);
            default:
                return [];
        }
    }
    
    async searchArxiv(query) {
        const searchUrl = `https://export.arxiv.org/api/query?search_query=all:${encodeURIComponent(query)}&start=0&max_results=5&sortBy=relevance&sortOrder=descending`;
        
        try {
            const response = await fetch(searchUrl);
            const xmlText = await response.text();
            
            // Simple XML parsing for service worker context
            const papers = this.parseArxivXML(xmlText);
            return papers;
        } catch (error) {
            console.error('ArXiv search error:', error);
            return [];
        }
    }
    
    parseArxivXML(xmlText) {
        const papers = [];
        
        // Simple regex-based parsing for service worker
        const entryRegex = /<entry>([\s\S]*?)<\/entry>/g;
        let match;
        
        while ((match = entryRegex.exec(xmlText)) !== null) {
            const entry = match[1];
            
            const titleMatch = entry.match(/<title[^>]*>([\s\S]*?)<\/title>/);
            const title = titleMatch ? titleMatch[1].replace(/\s+/g, ' ').trim() : '';
            
            const authorMatches = entry.match(/<author>[\s\S]*?<name>([\s\S]*?)<\/name>[\s\S]*?<\/author>/g);
            const authors = authorMatches ? 
                authorMatches.map(a => a.match(/<name>([\s\S]*?)<\/name>/)[1]).join(', ') : '';
            
            const summaryMatch = entry.match(/<summary[^>]*>([\s\S]*?)<\/summary>/);
            const abstract = summaryMatch ? summaryMatch[1].replace(/\s+/g, ' ').trim() : '';
            
            const idMatch = entry.match(/<id>([\s\S]*?)<\/id>/);
            const url = idMatch ? idMatch[1].trim() : '';
            
            if (title && url) {
                papers.push({
                    title,
                    authors,
                    abstract,
                    url,
                    source: 'arXiv'
                });
            }
        }
        
        return papers;
    }
    
    async searchIEEE(query) {
        // IEEE doesn't have a public API, so we'll simulate results
        // In a real implementation, you might use web scraping or a paid API
        return [
            {
                title: `IEEE Paper on ${query}`,
                authors: 'IEEE Authors',
                abstract: `This is a simulated IEEE paper about ${query}. In a real implementation, this would be fetched from IEEE Xplore.`,
                url: `https://ieeexplore.ieee.org/search/searchresult.jsp?queryText=${encodeURIComponent(query)}`,
                source: 'IEEE'
            }
        ];
    }
    
    async searchGoogleScholar(query) {
        // Google Scholar doesn't have a public API, so we'll simulate results
        return [
            {
                title: `Google Scholar Paper on ${query}`,
                authors: 'Scholar Authors',
                abstract: `This is a simulated Google Scholar paper about ${query}. In a real implementation, this would be fetched from Google Scholar.`,
                url: `https://scholar.google.com/scholar?q=${encodeURIComponent(query)}`,
                source: 'Google Scholar'
            }
        ];
    }
    
    removeDuplicates(papers) {
        const seen = new Set();
        return papers.filter(paper => {
            const key = paper.title.toLowerCase();
            if (seen.has(key)) {
                return false;
            }
            seen.add(key);
            return true;
        });
    }
}

// Initialize the agentic AI
console.log('🚀 Initializing Research Paper AI...');
const agenticAI = new AgenticAI();

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('📨 Received message:', request.action);
    if (request.action === 'processQuery') {
        agenticAI.processQuery(request.message, request.conversationHistory)
            .then(results => {
                console.log('✅ Query processed successfully');
                sendResponse(results);
            })
            .catch(error => {
                console.error('❌ Query processing failed:', error);
                sendResponse({ success: false, error: error.message });
            });
        return true; // Keep the message channel open for async response
    }
});

// Listen for storage changes to update API key
chrome.storage.onChanged.addListener((changes, namespace) => {
    if (namespace === 'local' && changes.gemini_api_key) {
        console.log('🔄 API key updated, reinitializing...');
        agenticAI.apiKey = changes.gemini_api_key.newValue;
    }
});

// Handle extension installation
chrome.runtime.onInstalled.addListener(() => {
    console.log('🔬 Research Paper AI extension installed');
}); 