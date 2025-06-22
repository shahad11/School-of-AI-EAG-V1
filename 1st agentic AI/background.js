// Background service worker for Research Paper AI - Proper Agent Architecture
class ResearchPaperAgent {
    constructor() {
        this.apiKey = null;
        this.maxIterations = 5;
        this.memory = {
            conversationHistory: [],
            searchResults: [],
            userPreferences: {}
        };
        this.tools = {
            searchArxiv: this.searchArxiv.bind(this),
            searchIEEE: this.searchIEEE.bind(this),
            searchGoogleScholar: this.searchGoogleScholar.bind(this),
            analyzePapers: this.analyzePapers.bind(this),
            filterPapers: this.filterPapers.bind(this)
        };
        
        console.log('🔬 Research Paper Agent initialized');
        this.initializeAPIKey();
    }
    
    async initializeAPIKey() {
        console.log('🔄 Initializing API key...');
        try {
            // Try to get API key from storage
            const result = await chrome.storage.local.get(['gemini_api_key']);
            console.log('📦 Storage result:', result);
            console.log('📦 Raw gemini_api_key:', result.gemini_api_key);
            
            if (result.gemini_api_key && result.gemini_api_key.trim() !== '') {
                this.apiKey = result.gemini_api_key.trim();
                console.log('✅ API key loaded from storage');
                console.log('  - Length:', this.apiKey.length);
                console.log('  - Starts with:', this.apiKey.substring(0, 10) + '...');
                console.log('  - Ends with:', '...' + this.apiKey.substring(this.apiKey.length - 5));
            } else {
                console.warn('⚠️ API key not found in storage. Please configure it.');
                console.log('🔍 Available storage keys:', Object.keys(result));
                console.log('🔍 gemini_api_key value:', result.gemini_api_key);
            }
        } catch (error) {
            console.error('❌ Error loading API key:', error);
        }
    }
    
    async processQuery(message, conversationHistory) {
        console.log('📝 Processing query:', message);
        console.log('🔑 Current API key status:', this.apiKey ? 'SET' : 'NOT SET');
        
        try {
            if (!this.apiKey) {
                await this.initializeAPIKey();
            }
            
            if (!this.apiKey) {
                throw new Error('API key not configured. Please set your Gemini API key in the extension options.');
            }
            
            // Update memory with new conversation
            this.memory.conversationHistory = conversationHistory || [];
            this.memory.conversationHistory.push({ role: 'user', content: message });
            
            // Run the agent
            const results = await this.runAgent(message);
            return { success: true, results };
        } catch (error) {
            console.error('❌ Error in processQuery:', error);
            return { success: false, error: error.message };
        }
    }
    
    async runAgent(userQuery) {
        let iteration = 0;
        let currentContext = userQuery;
        let finalResults = [];
        
        console.log('\n🤖 Starting Research Paper Agent...');
        console.log('📋 User Query:', userQuery);
        
        // Send debug info to popup
        this.sendDebugLog('🤖 Starting Research Paper Agent...', 'info');
        this.sendDebugLog(`📋 User Query: ${userQuery}`, 'info');
        
        while (iteration < this.maxIterations) {
            console.log(`\n--- Iteration ${iteration + 1} ---`);
            this.sendDebugLog(`--- Iteration ${iteration + 1} ---`, 'iteration');
            
            // Build orchestrator prompt
            const orchestratorPrompt = this.buildOrchestratorPrompt(currentContext, iteration);
            
            // Get LLM decision
            const llmResponse = await this.callLLM(orchestratorPrompt);
            console.log(`LLM Response: ${llmResponse}`);
            this.sendDebugLog(`LLM Response: ${llmResponse}`, 'llm-response');
            
            // Parse the response
            const parsedResponse = this.parseLLMResponse(llmResponse);
            
            if (parsedResponse.type === 'FINAL_ANSWER') {
                console.log('\n=== Agent Execution Complete ===');
                console.log('📊 Final Results:', finalResults.length, 'papers found');
                this.sendDebugLog('=== Agent Execution Complete ===', 'complete');
                this.sendDebugLog(`📊 Final Results: ${finalResults.length} papers found`, 'complete');
                return finalResults;
            } else if (parsedResponse.type === 'TOOL_CALL') {
                // Execute tool
                const toolResult = await this.executeTool(parsedResponse.tool, parsedResponse.params);
                console.log(`  Result: ${JSON.stringify(toolResult)}`);
                this.sendDebugLog(`  Result: ${JSON.stringify(toolResult)}`, 'tool-result');
                
                // Update memory
                this.memory.conversationHistory.push({ 
                    role: 'assistant', 
                    content: `Called ${parsedResponse.tool} with ${JSON.stringify(parsedResponse.params)} parameters` 
                });
                this.memory.conversationHistory.push({ 
                    role: 'system', 
                    content: `Tool result: ${JSON.stringify(toolResult)}` 
                });
                
                // Update results if papers were found
                if (toolResult.papers) {
                    finalResults = toolResult.papers;
                }
                
                // Prepare next context
                currentContext = this.buildNextContext(userQuery, parsedResponse, toolResult, iteration);
            } else {
                console.log('⚠️ Unexpected response type, treating as final answer');
                this.sendDebugLog('⚠️ Unexpected response type, treating as final answer', 'info');
                return finalResults;
            }
            
            iteration++;
        }
        
        console.log('\n=== Agent Execution Complete (Max Iterations Reached) ===');
        this.sendDebugLog('=== Agent Execution Complete (Max Iterations Reached) ===', 'complete');
        return finalResults;
    }
    
    buildOrchestratorPrompt(currentContext, iteration) {
        const systemPrompt = `You are an intelligent research paper agent. Your job is to help users find relevant academic papers.

AVAILABLE TOOLS:
1. searchArxiv(query) - Search arXiv for papers
2. searchIEEE(query) - Search IEEE Xplore for papers  
3. searchGoogleScholar(query) - Search Google Scholar for papers
4. analyzePapers(papers, criteria) - Analyze and rank papers based on criteria
5. filterPapers(papers, filters) - Filter papers based on specific criteria

RESPONSE FORMAT:
- For tool calls: TOOL_CALL: tool_name|{"param1": "value1"}
- For final answer: FINAL_ANSWER: your response

AGENT STRATEGY:
1. First, understand what the user is looking for
2. Search multiple sources to get comprehensive results
3. Analyze and filter the papers based on relevance
4. Return the most relevant papers

CONVERSATION HISTORY:
${this.memory.conversationHistory.map(msg => `${msg.role.toUpperCase()}: ${msg.content}`).join('\n')}

Current iteration: ${iteration + 1}
Current context: ${currentContext}

What should I do next?`;

        return systemPrompt;
    }
    
    buildNextContext(originalQuery, toolCall, toolResult, iteration) {
        return `${originalQuery}

Iteration ${iteration + 1} completed:
- Tool called: ${toolCall.tool}
- Parameters: ${JSON.stringify(toolCall.params)}
- Result: ${JSON.stringify(toolResult)}

What should I do next?`;
    }
    
    async callLLM(context) {
        if (!this.apiKey) {
            throw new Error('API key not configured');
        }
        
        console.log('🔑 API Key Debug Info:');
        console.log('  - Key length:', this.apiKey.length);
        console.log('  - Key starts with:', this.apiKey.substring(0, 10) + '...');
        console.log('  - Key ends with:', '...' + this.apiKey.substring(this.apiKey.length - 5));
        console.log('  - Contains spaces:', this.apiKey.includes(' '));
        console.log('  - Contains newlines:', this.apiKey.includes('\n'));
        console.log('  - Trimmed length:', this.apiKey.trim().length);
        
        // Use trimmed key to avoid any whitespace issues
        const cleanApiKey = this.apiKey.trim();
        
        const requestBody = {
            contents: [{
                parts: [{
                    text: context
                }]
            }],
            generationConfig: {
                temperature: 0.1,
                maxOutputTokens: 1000
            }
        };
        
        console.log('🌐 Making API request to Gemini...');
        console.log('  - URL:', `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${cleanApiKey.substring(0, 10)}...`);
        console.log('  - Request body:', JSON.stringify(requestBody, null, 2));
        
        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${cleanApiKey}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });
        
        console.log('📡 Response status:', response.status);
        console.log('📡 Response headers:', Object.fromEntries(response.headers.entries()));
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ API Error Response:', errorText);
            console.error('❌ Full error details:', {
                status: response.status,
                statusText: response.statusText,
                url: response.url,
                body: errorText
            });
            throw new Error(`API call failed: ${response.status} - ${errorText}`);
        }
        
        const data = await response.json();
        console.log('✅ API call successful');
        return data.candidates[0].content.parts[0].text;
    }
    
    parseLLMResponse(response) {
        console.log('🔍 Parsing LLM response:', response);
        
        const cleanResponse = response.trim();
        const lines = cleanResponse.split('\n');
        const firstLine = lines[0].trim();
        
        console.log('📝 First line:', firstLine);
        
        if (firstLine.startsWith('TOOL_CALL:')) {
            const parts = firstLine.split(':', 2)[1].split('|');
            const tool = parts[0].trim();
            let params;

            if (parts[1]) {
                const paramsString = parts[1].trim();
                try {
                    params = JSON.parse(paramsString);
                    console.log('🔧 Parsed tool call with JSON params:', { tool, params });
                } catch (error) {
                    console.warn('⚠️ JSON parsing failed for params. Assuming simple string query.', error.message);
                    params = { "query": paramsString, "source": "all" };
                    console.log('🔧 Parsed tool call with fallback params:', { tool, params });
                }
            } else {
                params = {};
            }

            return { type: 'TOOL_CALL', tool, params };
        } 
        else if (firstLine.startsWith('FINAL_ANSWER:')) {
            const results = firstLine.split(':', 2)[1].trim();
            console.log('✅ Parsed final answer:', results);
            return { type: 'FINAL_ANSWER', results };
        }
        else {
            console.log('⚠️ LLM didn\'t use expected format, treating as final answer');
            return { type: 'FINAL_ANSWER', results: cleanResponse };
        }
    }
    
    async executeTool(toolName, params) {
        console.log(`🔧 Executing tool: ${toolName} with params:`, params);
        
        switch (toolName) {
            case 'searchArxiv':
                return await this.tools.searchArxiv(params.query || params);
            case 'searchIEEE':
                return await this.tools.searchIEEE(params.query || params);
            case 'searchGoogleScholar':
                return await this.tools.searchGoogleScholar(params.query || params);
            case 'analyzePapers':
                return await this.tools.analyzePapers(params.papers, params.criteria);
            case 'filterPapers':
                return await this.tools.filterPapers(params.papers, params.filters);
            default:
                throw new Error(`Unknown tool: ${toolName}`);
        }
    }
    
    // Tool implementations
    async searchArxiv(query) {
        const searchUrl = `https://export.arxiv.org/api/query?search_query=all:${encodeURIComponent(query)}&start=0&max_results=5&sortBy=relevance&sortOrder=descending`;
        
        try {
            console.log('🔍 Searching ArXiv for:', query);
            const response = await fetch(searchUrl);
            const xmlText = await response.text();
            
            const papers = this.parseArxivXML(xmlText);
            console.log('📄 Found ArXiv papers:', papers.length);
            return { papers };
        } catch (error) {
            console.error('ArXiv search error:', error);
            return { papers: [] };
        }
    }
    
    parseArxivXML(xmlText) {
        const papers = [];
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
                    title: title.replace(/^\s*Title:\s*/, ''),
                    authors: authors || 'Unknown Authors',
                    abstract: abstract || 'Abstract not available',
                    url: url,
                    source: 'arXiv'
                });
            }
        }
        
        return papers;
    }
    
    async searchIEEE(query) {
        console.log('🔍 Searching IEEE for:', query);
        const searchUrl = `https://ieeexplore.ieee.org/search/searchresult.jsp?queryText=${encodeURIComponent(query)}`;
        
        return {
            papers: [{
                title: `IEEE Search Results for: ${query}`,
                authors: 'IEEE Xplore',
                abstract: `Click to view IEEE Xplore search results for "${query}". This will open IEEE's search page with relevant papers.`,
                url: searchUrl,
                source: 'IEEE Xplore'
            }]
        };
    }
    
    async searchGoogleScholar(query) {
        console.log('🔍 Searching Google Scholar for:', query);
        const searchUrl = `https://scholar.google.com/scholar?q=${encodeURIComponent(query)}`;
        
        return {
            papers: [{
                title: `Google Scholar Results for: ${query}`,
                authors: 'Google Scholar',
                abstract: `Click to view Google Scholar search results for "${query}". This will open Google Scholar with relevant papers.`,
                url: searchUrl,
                source: 'Google Scholar'
            }]
        };
    }
    
    async analyzePapers(papers, criteria) {
        console.log('🔍 Analyzing papers with criteria:', criteria);
        // Simple analysis - in a real implementation, this would use the LLM to analyze papers
        return { papers: papers.slice(0, 3) }; // Return top 3
    }
    
    async filterPapers(papers, filters) {
        console.log('🔍 Filtering papers with filters:', filters);
        // Simple filtering - in a real implementation, this would apply specific filters
        return { papers: papers };
    }
    
    sendDebugLog(message, type = 'info') {
        // Send debug log to popup if it's open
        chrome.runtime.sendMessage({
            action: 'debugLog',
            message: message,
            type: type
        }).catch(() => {
            // Popup might not be open, ignore error
        });
    }
}

// Initialize the agent
console.log('🚀 Initializing Research Paper Agent...');
const agent = new ResearchPaperAgent();

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('📨 Received message:', request.action);
    if (request.action === 'processQuery') {
        agent.processQuery(request.message, request.conversationHistory)
            .then(results => {
                console.log('✅ Query processed successfully');
                sendResponse(results);
            })
            .catch(error => {
                console.error('❌ Query processing failed:', error);
                sendResponse({ success: false, error: error.message });
            });
        return true;
    }
});

// Listen for storage changes
chrome.storage.onChanged.addListener((changes, namespace) => {
    if (namespace === 'local' && changes.gemini_api_key) {
        console.log('🔄 API key updated, reinitializing...');
        agent.apiKey = changes.gemini_api_key.newValue;
    }
});

// Handle extension installation
chrome.runtime.onInstalled.addListener(() => {
    console.log('🔬 Research Paper Agent extension installed');
}); 