// PyMOL AI Assistant - Frontend JavaScript
class PyMOLChat {
    constructor() {
        this.chatMessages = document.getElementById('chat-messages');
        this.userInput = document.getElementById('user-input');
        this.sendButton = document.getElementById('send-button');
        this.clearButton = document.getElementById('clear-chat');
        this.loadingOverlay = document.getElementById('loading-overlay');
        this.statusIndicator = document.getElementById('status');
        
        this.initializeEventListeners();
        this.autoResizeTextarea();
    }
    
    initializeEventListeners() {
        // Send button click
        this.sendButton.addEventListener('click', () => this.sendMessage());
        
        // Enter key to send (Shift+Enter for new line)
        this.userInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Input validation
        this.userInput.addEventListener('input', () => {
            const hasText = this.userInput.value.trim().length > 0;
            this.sendButton.disabled = !hasText;
        });
        
        // Clear chat button
        this.clearButton.addEventListener('click', () => this.clearChat());
        
        // Initialize highlight.js
        hljs.highlightAll();
    }
    
    autoResizeTextarea() {
        this.userInput.addEventListener('input', () => {
            this.userInput.style.height = 'auto';
            this.userInput.style.height = Math.min(this.userInput.scrollHeight, 200) + 'px';
        });
    }
    
    async sendMessage() {
        const message = this.userInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Clear input and disable send button
        this.userInput.value = '';
        this.userInput.style.height = 'auto';
        this.sendButton.disabled = true;
        
        // Show loading state
        this.showLoading(true);
        this.updateStatus('Generating...', 'generating');
        
        try {
            // Send request to backend
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.addAssistantMessage(data.message, data.pymol_commands);
                this.updateStatus('Ready', 'ready');
            } else {
                this.addErrorMessage(data.error || 'An error occurred');
                this.updateStatus('Error', 'error');
            }
            
        } catch (error) {
            console.error('Error:', error);
            this.addErrorMessage('Failed to connect to the server. Please try again.');
            this.updateStatus('Error', 'error');
        } finally {
            this.showLoading(false);
        }
    }
    
    addMessage(content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        const avatar = type === 'user' ? '👤' : '🤖';
        const avatarClass = type === 'user' ? 'user-avatar' : 'assistant-avatar';
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <div class="avatar ${avatarClass}">${avatar}</div>
            </div>
            <div class="message-content">
                <div class="message-text">
                    ${this.formatMessage(content)}
                </div>
            </div>
        `;
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    addAssistantMessage(explanation, pymolCommands) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant-message';
        
        let content = `
            <div class="message-avatar">
                <div class="avatar assistant-avatar">🤖</div>
            </div>
            <div class="message-content">
                <div class="message-text">
                    ${this.formatMessage(explanation)}
                </div>
        `;
        
        // Add PyMOL commands if available
        if (pymolCommands && pymolCommands.length > 0) {
            const commandsText = pymolCommands.join('\n');
            const codeId = 'code-' + Date.now();
            
            content += `
                <div class="code-container">
                    <div class="code-header">
                        <span class="code-title">PyMOL Commands</span>
                        <button class="copy-button" onclick="copyCode('${codeId}')">
                            📋 Copy
                        </button>
                    </div>
                    <div class="code-content">
                        <pre><code id="${codeId}" class="language-python">${this.escapeHtml(commandsText)}</code></pre>
                    </div>
                </div>
            `;
        }
        
        content += `
            </div>
        `;
        
        messageDiv.innerHTML = content;
        this.chatMessages.appendChild(messageDiv);
        
        // Highlight code
        messageDiv.querySelectorAll('pre code').forEach(block => {
            hljs.highlightElement(block);
        });
        
        this.scrollToBottom();
    }
    
    addErrorMessage(error) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant-message';
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <div class="avatar assistant-avatar">⚠️</div>
            </div>
            <div class="message-content">
                <div class="error-message">
                    <strong>Error:</strong> ${this.escapeHtml(error)}
                </div>
            </div>
        `;
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    formatMessage(text) {
        // Convert markdown-style formatting to HTML
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>')
            .replace(/#{1,6}\s(.*?)(?:\n|$)/g, '<h3>$1</h3>');
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }
    
    showLoading(show) {
        if (show) {
            this.loadingOverlay.classList.add('active');
        } else {
            this.loadingOverlay.classList.remove('active');
        }
    }
    
    updateStatus(text, type) {
        const statusText = this.statusIndicator.querySelector('span');
        const statusDot = this.statusIndicator.querySelector('.status-dot');
        
        statusText.textContent = text;
        
        // Update status dot color
        statusDot.className = 'status-dot';
        if (type === 'generating') {
            statusDot.style.background = '#f59e0b';
        } else if (type === 'error') {
            statusDot.style.background = '#ef4444';
        } else {
            statusDot.style.background = '#10a37f';
        }
    }
    
    async clearChat() {
        try {
            const response = await fetch('/api/clear', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (response.ok) {
                // Clear chat messages (keep welcome message)
                const messages = this.chatMessages.querySelectorAll('.message');
                messages.forEach((msg, index) => {
                    if (index > 0) { // Keep first message (welcome)
                        msg.remove();
                    }
                });
                
                this.updateStatus('Ready', 'ready');
                this.userInput.focus();
            }
        } catch (error) {
            console.error('Error clearing chat:', error);
        }
    }
}

// Global function for copying code
function copyCode(elementId) {
    const codeElement = document.getElementById(elementId);
    const text = codeElement.textContent;
    
    navigator.clipboard.writeText(text).then(() => {
        // Show success feedback
        const button = codeElement.parentElement.parentElement.querySelector('.copy-button');
        const originalText = button.innerHTML;
        button.innerHTML = '✅ Copied!';
        
        setTimeout(() => {
            button.innerHTML = originalText;
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy code:', err);
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
    });
}

// Initialize the chat application
document.addEventListener('DOMContentLoaded', () => {
    new PyMOLChat();
    
    // Focus on input
    document.getElementById('user-input').focus();
    
    // Check server health
    fetch('/api/health')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'healthy') {
                console.log('✅ Server is healthy');
                if (!data.pymol_agent_available) {
                    console.warn('⚠️ PyMOL Agent not fully available');
                }
            }
        })
        .catch(error => {
            console.error('❌ Server health check failed:', error);
        });
});

// Handle page visibility for better performance
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // Page is hidden, pause any animations
        document.querySelectorAll('.status-dot').forEach(dot => {
            dot.style.animationPlayState = 'paused';
        });
    } else {
        // Page is visible, resume animations
        document.querySelectorAll('.status-dot').forEach(dot => {
            dot.style.animationPlayState = 'running';
        });
    }
});
