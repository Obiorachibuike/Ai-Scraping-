document.addEventListener('DOMContentLoaded', function() {
    const initBtn = document.getElementById('init-btn');
    const geminiKeyInput = document.getElementById('gemini-key');
    const googleKeyInput = document.getElementById('google-key');
    const cseIdInput = document.getElementById('cse-id');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const clearBtn = document.getElementById('clear-btn');
    const chatContainer = document.getElementById('chat-container');
    const queryHistory = document.getElementById('query-history');
    const agentStatus = document.getElementById('agent-status');
    
    let isAgentInitialized = false;
    
    // Auto-resize textarea
    userInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });
    
    // Initialize agent
    initBtn.addEventListener('click', async function() {
        const geminiKey = geminiKeyInput.value.trim();
        const googleKey = googleKeyInput.value.trim();
        const cseId = cseIdInput.value.trim();
        
        if (!geminiKey) {
            showAlert('Please enter your Gemini API key', 'error');
            return;
        }
        
        initBtn.disabled = true;
        initBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Initializing...';
        
        try {
            const response = await fetch('/initialize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    gemini_api_key: geminiKey,
                    google_api_key: googleKey,
                    google_cse_id: cseId
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                isAgentInitialized = true;
                agentStatus.innerHTML = '<i class="fas fa-circle"></i> Agent ready';
                agentStatus.classList.add('initialized');
                showAlert('Agent initialized successfully!', 'success');
                
                // Clear welcome message
                const welcome = document.querySelector('.welcome-message');
                if (welcome) {
                    welcome.style.display = 'none';
                }
            } else {
                throw new Error(data.error || 'Initialization failed');
            }
        } catch (error) {
            showAlert(error.message, 'error');
        } finally {
            initBtn.disabled = false;
            initBtn.innerHTML = '<i class="fas fa-rocket"></i> Initialize Agent';
        }
    });
    
    // Send message
    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Clear chat
    clearBtn.addEventListener('click', function() {
        chatContainer.innerHTML = '';
        showAlert('Chat cleared', 'info');
    });
    
    // Example prompt insertion
    window.insertExample = function(prompt) {
        userInput.value = prompt;
        userInput.focus();
        userInput.dispatchEvent(new Event('input'));
    }
    
    async function sendMessage() {
        const message = userInput.value.trim();
        
        if (!message) return;
        
        if (!isAgentInitialized) {
            showAlert('Please initialize the agent first', 'error');
            return;
        }
        
        // Add user message to chat
        addMessageToChat(message, 'user');
        userInput.value = '';
        userInput.style.height = 'auto';
        
        // Add loading indicator
        const loadingId = 'loading-' + Date.now();
        chatContainer.innerHTML += `
            <div class="message assistant-message" id="${loadingId}">
                <div class="loading-dots">
                    <div></div>
                    <div></div>
                    <div></div>
                </div>
            </div>
        `;
        
        // Scroll to bottom
        scrollToBottom();
        
        try {
            const response = await fetch('/research', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query: message })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Research failed');
            }
            
            // Remove loading indicator
            document.getElementById(loadingId).remove();
            
            // Add assistant response
            addMessageToChat(data.response, 'assistant', data.sources);
            
            // Add to query history
            addToHistory(message);
            
        } catch (error) {
            // Remove loading indicator
            document.getElementById(loadingId).remove();
            
            // Show error message
            addMessageToChat(error.message, 'error');
        }
        
        scrollToBottom();
    }
    
    function addMessageToChat(content, type, sources = null) {
        let messageHtml;
        
        if (type === 'user') {
            messageHtml = `
                <div class="message user-message">
                    <div class="message-content">${content}</div>
                </div>
            `;
        } else if (type === 'error') {
            messageHtml = `
                <div class="message assistant-message" style="color: var(--danger-color);">
                    <div class="message-content">
                        <strong>Error:</strong> ${content}
                    </div>
                </div>
            `;
        } else {
            let sourcesHtml = '';
            if (sources && sources.length > 0) {
                sourcesHtml = `
                    <button class="sources-btn" onclick="toggleSources(this)">
                        <i class="fas fa-chevron-down"></i> Show Sources (${sources.length})
                    </button>
                    <div class="sources-panel">
                        ${sources.map(source => `
                            <div class="source-item">
                                <a href="${source.link}" target="_blank">${source.title}</a>
                            </div>
                        `).join('')}
                    </div>
                `;
            }
            
            messageHtml = `
                <div class="message assistant-message">
                    <div class="message-content">
                        ${content}
                        ${sourcesHtml}
                    </div>
                </div>
            `;
        }
        
        chatContainer.innerHTML += messageHtml;
    }
    
    function addToHistory(query) {
        const now = new Date();
        const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        queryHistory.innerHTML += `
            <div class="history-item" onclick="insertExample('${query.replace(/'/g, "\\'")}')">
                <span class="query-text">${query}</span>
                <span class="query-time">${timeStr}</span>
            </div>
        `;
    }
    
    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    function showAlert(message, type) {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.textContent = message;
        document.body.appendChild(alert);
        
        setTimeout(() => {
            alert.classList.add('show');
            setTimeout(() => {
                alert.classList.remove('show');
                setTimeout(() => {
                    alert.remove();
                }, 300);
            }, 3000);
        }, 10);
    }
});

// Toggle sources visibility (made global)
window.toggleSources = function(btn) {
    btn.classList.toggle('active');
    const panel = btn.nextElementSibling;
    panel.classList.toggle('active');
};
