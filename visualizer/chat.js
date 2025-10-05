class ChatInterface {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.statusIndicator = document.getElementById('statusIndicator');
        this.isProcessing = false;
    }

    setStatus(status, text) {
        const statusDot = this.statusIndicator.querySelector('.status-dot');
        const statusText = this.statusIndicator.querySelector('.status-text');

        statusText.textContent = text;

        statusDot.style.background = {
            'ready': '#10b981',
            'listening': '#3b82f6',
            'processing': '#f59e0b',
            'error': '#ef4444'
        }[status] || '#10b981';

        statusDot.style.boxShadow = {
            'ready': '0 0 12px rgba(16, 185, 129, 0.6)',
            'listening': '0 0 12px rgba(59, 130, 246, 0.6)',
            'processing': '0 0 12px rgba(245, 158, 11, 0.6)',
            'error': '0 0 12px rgba(239, 68, 68, 0.6)'
        }[status] || '0 0 12px rgba(16, 185, 129, 0.6)';
    }

    clearWelcomeMessage() {
        const welcomeMessage = this.chatMessages.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.style.animation = 'messageSlide 0.3s reverse';
            setTimeout(() => welcomeMessage.remove(), 300);
        }
    }

    addMessage(text, type = 'user') {
        this.clearWelcomeMessage();

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = type === 'user' ? '👤' : '🤖';

        const content = document.createElement('div');
        content.className = 'message-content';

        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        bubble.textContent = text;

        const time = document.createElement('div');
        time.className = 'message-time';
        time.textContent = this.getCurrentTime();

        content.appendChild(bubble);
        content.appendChild(time);

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);

        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();

        return messageDiv;
    }

    addTypingIndicator() {
        if (this.isProcessing) return;

        this.isProcessing = true;

        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant typing-indicator-message';
        messageDiv.id = 'typingIndicator';

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = '🤖';

        const content = document.createElement('div');
        content.className = 'message-content';

        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';

        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'typing-indicator';
        typingIndicator.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';

        bubble.appendChild(typingIndicator);
        content.appendChild(bubble);

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);

        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    removeTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.style.animation = 'messageSlide 0.3s reverse';
            setTimeout(() => typingIndicator.remove(), 300);
        }
        this.isProcessing = false;
    }

    addAssistantMessage(text) {
        this.removeTypingIndicator();
        this.addMessage(text, 'assistant');
    }

    getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: true
        });
    }

    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }

    clear() {
        this.chatMessages.innerHTML = '<div class="welcome-message"><p>Speak to your assistant...</p></div>';
    }
}
