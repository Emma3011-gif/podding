// Global variables
let currentDocId = null;
let isProcessing = false;
let sessionMessages = []; // Track messages for session saving

// DOM element references (will be initialized on DOMContentLoaded)
let dropArea, fileInput, fileInfo, fileName, fileStatus, errorMessage;
let uploadSection, chatSection, chatMessages, messageInput, sendButton;
let typingIndicator, docName, uploadNew, generateQuiz, quizSection;
let quizContent, closeQuiz, statusDot, statusText, themeToggle;
let userMenu, userAvatar, userDropdown, userName, userEmail, logoutBtn, openProfileBtn;
let userAvatarImg, userAvatarPlaceholder;
let drawerOverlay, sideDrawer, drawerClose, drawerTabs, drawerProfileTab, drawerHistoryTab;
let drawerProfile, drawerHistory, drawerProfileMessage, drawerDisplayName, drawerSaveProfileBtn;
let drawerAvatarInput, drawerChangeAvatarBtn, drawerAvatarImg, drawerAvatarPlaceholder;
let drawerDocumentList, drawerChatHistory, drawerChatBackBtn, drawerChatDocName, drawerChatMessages;

// Initialize DOM elements and event listeners
function init() {
    // DOM Elements - assign to global variables
    dropArea = document.getElementById('dropArea');
    fileInput = document.getElementById('fileInput');
    fileInfo = document.getElementById('fileInfo');
    fileName = document.getElementById('fileName');
    fileStatus = document.getElementById('fileStatus');
    errorMessage = document.getElementById('errorMessage');
    uploadSection = document.getElementById('uploadSection');
    chatSection = document.getElementById('chatSection');
    chatMessages = document.getElementById('chatMessages');
    messageInput = document.getElementById('messageInput');
    sendButton = document.getElementById('sendButton');
    typingIndicator = document.getElementById('typingIndicator');
    docName = document.getElementById('docName');
    uploadNew = document.getElementById('uploadNew');
    generateQuiz = document.getElementById('generateQuiz');
    quizSection = document.getElementById('quizSection');
    quizContent = document.getElementById('quizContent');
    closeQuiz = document.getElementById('closeQuiz');
    statusDot = document.getElementById('statusDot');
    statusText = document.getElementById('statusText');
    themeToggle = document.getElementById('themeToggle');

    // User menu elements
    userMenu = document.getElementById('userMenu');
    userAvatar = document.getElementById('userAvatar');
    userDropdown = document.getElementById('userDropdown');
    userName = document.getElementById('userName');
    userEmail = document.getElementById('userEmail');
    userAvatarImg = document.getElementById('userAvatarImg');
    userAvatarPlaceholder = document.getElementById('userAvatarPlaceholder');
    logoutBtn = document.getElementById('logoutBtn');
    openProfileBtn = document.getElementById('openProfileBtn');

    // Drawer elements
    drawerOverlay = document.getElementById('drawerOverlay');
    sideDrawer = document.getElementById('sideDrawer');
    drawerClose = document.getElementById('drawerClose');
    drawerTabs = document.querySelectorAll('.drawer-tab');
    drawerProfileTab = document.getElementById('drawerProfile');
    drawerHistoryTab = document.getElementById('drawerHistory');
    drawerProfileMessage = document.getElementById('drawerProfileMessage');
    drawerDisplayName = document.getElementById('drawerDisplayName');
    drawerSaveProfileBtn = document.getElementById('drawerSaveProfileBtn');
    drawerAvatarInput = document.getElementById('drawerAvatarInput');
    drawerChangeAvatarBtn = document.getElementById('drawerChangeAvatarBtn');
    drawerAvatarImg = document.getElementById('drawerAvatarImg');
    drawerAvatarPlaceholder = document.getElementById('drawerAvatarPlaceholder');
    drawerDocumentList = document.getElementById('drawerDocumentList');
    drawerChatHistory = document.getElementById('drawerChatHistory');
    drawerChatBackBtn = document.getElementById('drawerChatBackBtn');
    drawerChatDocName = document.getElementById('drawerChatDocName');
    drawerChatMessages = document.getElementById('drawerChatMessages');

    // Attach event listeners
    if (themeToggle) {
        try {
            // Load saved theme
            loadThemePreference();
            // Attach click handler
            themeToggle.addEventListener('click', toggleTheme);
        } catch (e) {
            console.error('Failed to initialize theme toggle:', e);
        }
    } else {
        console.warn('Theme toggle button not found in DOM');
    }

    // Drawer event listeners
    if (openProfileBtn) {
        openProfileBtn.addEventListener('click', () => {
            hideUserMenu();
            openDrawer('profile');
            loadUserProfile();
            loadUserDocuments();
        });
    }

    // User menu toggle
    if (userAvatar) {
        userAvatar.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleUserDropdown();
        });
    }

    // Logout button
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
            try {
                const response = await fetch('/auth/logout', { method: 'POST' });
                if (response.ok) {
                    window.location.href = '/auth';
                } else {
                    const data = await response.json();
                    alert('Logout failed: ' + (data.error || 'Unknown error'));
                }
            } catch (error) {
                console.error('Logout error:', error);
                alert('Logout failed. Please try again.');
            }
        });
    }

    // Close dropdown when clicking outside
    document.addEventListener('click', handleDocumentClick);

    if (drawerClose) {
        drawerClose.addEventListener('click', closeDrawer);
    }

    if (drawerOverlay) {
        drawerOverlay.addEventListener('click', closeDrawer);
    }

    drawerTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const tabName = tab.dataset.drawerTab;
            switchDrawerTab(tabName);
        });
    });

    if (drawerChangeAvatarBtn) {
        drawerChangeAvatarBtn.addEventListener('click', () => {
            drawerAvatarInput.click();
        });
    }

    if (drawerAvatarInput) {
        drawerAvatarInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleAvatarUpload(e.target.files[0]);
            }
        });
    }

    if (drawerSaveProfileBtn) {
        drawerSaveProfileBtn.addEventListener('click', saveProfile);
    }

    if (drawerChatBackBtn) {
        drawerChatBackBtn.addEventListener('click', () => {
            drawerChatHistory.style.display = 'none';
        });
    }

    // Document list action buttons (event delegation)
    if (drawerDocumentList) {
        drawerDocumentList.addEventListener('click', (e) => {
            const btn = e.target.closest('.drawer-btn-small');
            if (!btn) return;
            const card = btn.closest('.drawer-document-card');
            if (!card) return;
            const docId = card.dataset.docId;
            if (!docId) return;

            if (btn.classList.contains('delete-btn')) {
                deleteDocument(docId);
            } else if (btn.classList.contains('load-btn')) {
                loadDocumentFromHistory(docId);
            } else if (btn.classList.contains('view-chat-btn')) {
                viewChatHistory(docId);
            }
        });
    }

    // File Upload Event Listeners
    if (dropArea && fileInput) {
        dropArea.addEventListener('click', () => fileInput.click());

        dropArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropArea.classList.add('dragover');
        });

        dropArea.addEventListener('dragleave', () => {
            dropArea.classList.remove('dragover');
        });

        dropArea.addEventListener('drop', (e) => {
            e.preventDefault();
            dropArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileUpload(files[0]);
            }
        });
    }

    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileUpload(e.target.files[0]);
            }
        });
    }

    if (uploadNew) {
        uploadNew.addEventListener('click', () => {
            clearSession();
            sessionMessages = [];
            currentDocId = null;
            uploadSection.style.display = 'flex';
            chatSection.style.display = 'none';
            fileInput.value = '';
            hideFileInfo();
            hideError();
            messageInput.value = '';
            chatMessages.innerHTML = '';
            addMessage("Hey there! 👋 I've finished reading your document and I'm ready to help! Feel free to ask me anything about it - I'm here to make understanding it easy and enjoyable. What would you like to know first?", 'assistant');
            messageInput.focus();
            if (generateQuiz) generateQuiz.style.display = 'none';
            if (quizSection) quizSection.style.display = 'none';
        });
    }

    if (generateQuiz) {
        generateQuiz.addEventListener('click', async () => {
            if (!currentDocId) return;
            generateQuiz.disabled = true;
            quizContent.innerHTML = '<p>Generating quiz based on your document...</p>';
            quizSection.style.display = 'block';
            try {
                const response = await fetch('/quiz', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ doc_id: currentDocId })
                });
                if (response.ok) {
                    const data = await response.json();
                    quizContent.innerHTML = formatQuiz(data.quiz);
                } else {
                    const error = await response.json();
                    quizContent.innerHTML = `<p class="error">Error: ${error.error || 'Failed to generate quiz'}</p>`;
                }
            } catch (error) {
                quizContent.innerHTML = `<p class="error">Failed to generate quiz: ${error.message}</p>`;
            } finally {
                generateQuiz.disabled = false;
            }
        });
    }

    if (closeQuiz) {
        closeQuiz.addEventListener('click', () => {
            quizSection.style.display = 'none';
        });
    }

    // Message input handlers
    if (messageInput) {
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    }

    // Auto-resize textarea
    if (messageInput) {
        messageInput.addEventListener('input', autoResize);
    }

    // Check auth on page load
    checkAuth();

    // Initialize backend status check
    checkBackendStatus();
    setInterval(checkBackendStatus, 30000);

    // Try to restore previous session
    setTimeout(() => {
        loadSession();
    }, 1000);
}

// Wait for DOM to be ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

// Avatar SVG Images
const AVATAR_IMAGES = {
    user: `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="12" cy="9" r="3" stroke="currentColor" stroke-width="2"/>
        <path d="M12 15C14.2091 15 16 13.2091 16 11C16 8.79086 14.2091 7 12 7C9.79086 7 8 8.79086 8 11C8 13.2091 9.79086 15 12 15Z" stroke="currentColor" stroke-width="2"/>
    </svg>`,
    assistant: `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
        <circle cx="8.5" cy="8.5" r="1.5" fill="currentColor"/>
        <path d="M21 15C21 15.5304 20.7893 16.0391 20.4142 16.4142C20.0391 16.7893 19.5304 17 19 17H7L3 21V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H19C19.5304 3 20.0391 3.21071 20.4142 3.58579C20.7893 3.96086 21 4.46957 21 5V15Z" stroke="currentColor" stroke-width="2"/>
    </svg>`
};

// Format plain text to HTML with justified paragraphs and bold headers
function formatMessage(text) {
    if (!text) return '';
    // Remove code blocks entirely (triple backticks) to avoid language detection errors
    // This removes ```language and the code inside, keeping only the text outside code blocks
    let withoutCodeBlocks = text.replace(/```[\s\S]*?```/g, '');

    // Remove markdown formatting symbols (# for headers, * for bold/italic)
    // This removes: # headers, **bold**, *italic*, ***bold italic***
    let cleaned = withoutCodeBlocks
        // Remove markdown headers (# Heading)
        .replace(/^#{1,6}\s+/gm, '')
        // Remove bold/italic markers but keep the text
        .replace(/\*\*(.*?)\*\*/g, '$1')
        .replace(/\*(.*?)\*/g, '$1')
        .replace(/__(.*?)__/g, '$1')
        .replace(/_(.*?)_/g, '$1');

    // Split into paragraphs by blank lines (one or more empty lines)
    const paragraphs = cleaned.split(/\n\s*\n/);
    return paragraphs.map(p => {
        const trimmed = p.trim();
        if (!trimmed) return '';
        // Determine if it's a header: all uppercase and relatively short
        const isHeader = trimmed.length > 0 && trimmed.length < 100 && trimmed === trimmed.toUpperCase() && /[A-Za-z]/.test(trimmed);
        // Escape HTML (use cleaned text)
        const escaped = escapeHtml(trimmed);
        // Replace single newlines with <br>
        const withBreaks = escaped.replace(/\n/g, '<br>');
        if (isHeader) {
            return `<p class="justified header"><strong>${withBreaks}</strong></p>`;
        } else {
            return `<p class="justified">${withBreaks}</p>`;
        }
    }).join('');
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Status Check
async function checkBackendStatus() {
    try {
        const response = await fetch('/status');
        const data = await response.json();

        if (data.backend === 'connected') {
            statusDot.className = 'status-dot connected';
            statusText.textContent = 'Backend Connected';
        } else {
            statusDot.className = 'status-dot disconnected';
            statusText.textContent = 'Backend Disconnected';
        }
    } catch (error) {
        statusDot.className = 'status-dot disconnected';
        statusText.textContent = 'Backend Disconnected';
    }
}

async function handleFileUpload(file) {
    const allowedExtensions = ['.pdf', '.docx', '.jpg', '.jpeg', '.png', '.webp', '.bmp'];
    const fileName = file.name.toLowerCase();
    if (!allowedExtensions.some(ext => fileName.endsWith(ext))) {
        showError('Please select a PDF, DOCX, or image file (JPG, PNG, etc.)');
        return;
    }

    if (file.size > 25 * 1024 * 1024) {
        showError('File size must be less than 25MB');
        return;
    }

    hideError();
    showFileInfo(file.name, 'Processing...');

    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            currentDocId = data.doc_id;

            // Update chat header icon based on file type
            const docIcon = document.getElementById('docIcon');
            if (docIcon) {
                const ext = file.name.toLowerCase().split('.').pop();
                const icons = {
                    pdf: '📄',
                    docx: '📘',
                    jpg: '🖼️', jpeg: '🖼️', png: '🖼️', webp: '🖼️', bmp: '🖼️'
                };
                docIcon.textContent = icons[ext] || '📎';
            }

            // Show file info as "Analyzing..." while we generate document overview
            showFileInfo(file.name, 'Analyzing document...');
            docName.textContent = file.name;

            // Show quiz button and hide any previous quiz
            if (generateQuiz) generateQuiz.style.display = 'inline-block';
            if (quizSection) quizSection.style.display = 'none';

            // Clear previous session since we uploaded new file
            clearSession();
            sessionMessages = [];

            // Save the new document session
            saveSession();

            // Short delay to allow UI to update, then fetch analysis and show chat
            setTimeout(async () => {
                // Fetch document analysis
                let analysisMsg = null;
                try {
                    const analysisResponse = await fetch('/document-analysis', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ doc_id: currentDocId })
                    });

                    if (analysisResponse.ok) {
                        const analysisData = await analysisResponse.json();
                        if (analysisData.analysis) {
                            analysisMsg = analysisData.analysis;
                        }
                    }
                } catch (error) {
                    console.error('Failed to fetch analysis:', error);
                }

                // Update file status to Ready
                showFileInfo(file.name, 'Ready');

                // Show chat interface
                uploadSection.style.display = 'none';
                chatSection.style.display = 'flex';
                messageInput.disabled = false;
                sendButton.disabled = false;
                messageInput.focus();

                // Clear and add initial messages
                chatMessages.innerHTML = '';
                sessionMessages = [];

                if (analysisMsg) {
                    addMessage(analysisMsg, 'assistant');
                    sessionMessages.push({
                        type: 'assistant',
                        content: analysisMsg,
                        timestamp: new Date().toISOString()
                    });
                } else {
                    // Fallback if analysis failed
                    const fallbackMsg = `Great! I've successfully processed "${file.name}". The document is ready for questions. Feel free to ask me anything about its content!`;
                    addMessage(fallbackMsg, 'assistant');
                    sessionMessages.push({
                        type: 'assistant',
                        content: fallbackMsg,
                        timestamp: new Date().toISOString()
                    });
                }

                saveSession();
            }, 500);
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Upload failed');
        }
    } catch (error) {
        showError(error.message);
        hideFileInfo();
    }
}

function showFileInfo(name, status, icon = null) {
    fileName.textContent = name;
    fileStatus.textContent = status;
    const fileIconEl = document.getElementById('fileIcon');
    if (fileIconEl) {
        if (icon) {
            fileIconEl.textContent = icon;
        } else {
            // Auto-detect based on file extension
            const ext = name.toLowerCase().split('.').pop();
            const icons = {
                pdf: '📄',
                docx: '📘',
                jpg: '🖼️', jpeg: '🖼️', png: '🖼️', webp: '🖼️', bmp: '🖼️'
            };
            fileIconEl.textContent = icons[ext] || '📎';
        }
    }
    fileInfo.style.display = 'flex';
}

function hideFileInfo() {
    fileInfo.style.display = 'none';
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
}

function hideError() {
    errorMessage.style.display = 'none';
}

// ==================== SESSION MANAGEMENT ====================
// Save current session to localStorage
function saveSession() {
    const session = {
        docId: currentDocId,
        filename: fileName.textContent,
        messages: sessionMessages,
        timestamp: new Date().toISOString()
    };
    try {
        localStorage.setItem('pdfqa_session', JSON.stringify(session));
        console.log('Session saved');
    } catch (e) {
        console.error('Failed to save session:', e);
    }
}

// Load session from localStorage
function loadSession() {
    try {
        const saved = localStorage.getItem('pdfqa_session');
        if (!saved) return false;

        const session = JSON.parse(saved);
        if (!session.docId || !session.messages) {
            console.log('Invalid session data');
            return false;
        }

        // Check if backend is connected before offering to restore
        currentDocId = session.docId;
        sessionMessages = session.messages;
        fileName.textContent = session.filename || 'Unknown Document';
        docName.textContent = session.filename || 'Unknown Document';
        fileStatus.textContent = 'Ready (restored)';

        // Show restore notification
        showRestoreNotification(session);
        return true;
    } catch (e) {
        console.error('Failed to load session:', e);
        return false;
    }
}

// Clear session from localStorage
function clearSession() {
    try {
        localStorage.removeItem('pdfqa_session');
        console.log('Session cleared');
    } catch (e) {
        console.error('Failed to clear session:', e);
    }
}

// Show notification to restore session
function showRestoreNotification(session) {
    const messageCount = session.messages.filter(m => m.type === 'user' || m.type === 'assistant').length;
    const time = new Date(session.timestamp).toLocaleString();

    // Create a temporary banner
    const banner = document.createElement('div');
    banner.style.cssText = `
        position: fixed;
        top: 80px;
        left: 50%;
        transform: translateX(-50%);
        background: var(--surface);
        border: 1px solid var(--primary-color);
        border-radius: 8px;
        padding: 1rem 2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 1000;
        max-width: 90%;
        text-align: center;
    `;
    banner.innerHTML = `
        <div style="margin-bottom: 0.5rem; font-weight: 600; color: var(--primary-color);">
            Previous Session Found
        </div>
        <div style="margin-bottom: 0.75rem; color: var(--text-secondary); font-size: 0.9rem;">
            You had ${messageCount} messages from ${time}. Would you like to continue?
        </div>
        <div style="display: flex; gap: 12px; justify-content: center;">
            <button id="restoreSessionBtn" style="
                padding: 0.5rem 1.5rem;
                background: var(--primary-color);
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-weight: 500;
            ">Continue Session</button>
            <button id="discardSessionBtn" style="
                padding: 0.5rem 1.5rem;
                background: var(--surface);
                color: var(--text-secondary);
                border: 1px solid var(--border);
                border-radius: 6px;
                cursor: pointer;
                font-weight: 500;
            ">Start Fresh</button>
        </div>
    `;

    document.body.appendChild(banner);

    // Event listeners
    document.getElementById('restoreSessionBtn').onclick = () => {
        banner.remove();
        restoreSessionMessages();
    };

    document.getElementById('discardSessionBtn').onclick = () => {
        banner.remove();
        clearSession();
        // Reset UI to upload screen
        uploadSection.style.display = 'flex';
        chatSection.style.display = 'none';
        fileInput.value = '';
        hideFileInfo();
        hideError();
        currentDocId = null;
        sessionMessages = [];
        messageInput.value = '';
        chatMessages.innerHTML = '';
        // Hide quiz elements
        if (generateQuiz) generateQuiz.style.display = 'none';
        if (quizSection) quizSection.style.display = 'none';
    };

    // Auto-dismiss after 30 seconds
    setTimeout(() => {
        if (banner.parentNode) {
            banner.remove();
        }
    }, 30000);
}

// Restore chat messages from session
function restoreSessionMessages() {
    uploadSection.style.display = 'none';
    chatSection.style.display = 'flex';
    messageInput.disabled = false;
    sendButton.disabled = false;

    // Show file info (already set by loadSession)
    showFileInfo(fileName.textContent || 'Unknown Document', 'Ready (restored)');

    // Show quiz button
    if (generateQuiz) generateQuiz.style.display = 'inline-block';
    if (quizSection) quizSection.style.display = 'none';

    // Clear and rebuild chat history
    // Note: sessionMessages already contains the messages, we just need to render them
    // without adding to sessionMessages again
    chatMessages.innerHTML = '';
    sessionMessages.forEach(msg => {
        // Use a temporary function that doesn't track in sessionMessages
        renderMessageOnly(msg.content, msg.type);
    });

    console.log('Session restored with', sessionMessages.length, 'messages');
}

// Helper to render a message without tracking in sessionMessages
function renderMessageOnly(content, type) {
    const message = document.createElement('div');
    message.className = `message message-${type}`;

    const avatarHTML = type === 'user' ? AVATAR_IMAGES.user : AVATAR_IMAGES.assistant;
    const contentHTML = formatMessage(content);

    message.innerHTML = `
        <div class="message-avatar">${avatarHTML}</div>
        <div class="message-content">${contentHTML}</div>
    `;

    chatMessages.appendChild(message);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message || isProcessing || !currentDocId) return;

    isProcessing = true;
    sendButton.disabled = true;
    messageInput.disabled = true;

    // Add user message
    addMessage(message, 'user');
    messageInput.value = '';
    autoResize();

    // Show typing indicator with AI avatar
    showTyping();

    try {
        // Send full conversation history to maintain context
        const conversationMessages = sessionMessages.map(msg => ({
            role: msg.type === 'user' ? 'user' : 'assistant',
            content: msg.content
        }));

        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                doc_id: currentDocId,
                messages: conversationMessages
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Chat request failed');
        }

        // Stream response
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let assistantMessage = '';

        addMessage('', 'assistant');
        const messageElement = chatMessages.lastElementChild.querySelector('.message-content');

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            assistantMessage += chunk;
            // Format the assistant message as HTML with justified paragraphs
            messageElement.innerHTML = formatMessage(assistantMessage);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

    } catch (error) {
        addMessage(`Error: ${error.message}`, 'assistant', true);
    } finally {
        hideTyping();
        isProcessing = false;
        sendButton.disabled = false;
        messageInput.disabled = false;
        messageInput.focus();
        // Save session after completing the conversation turn
        saveSession();
    }
}

function addMessage(content, type, isError = false) {
    const message = document.createElement('div');
    message.className = `message message-${type}`;

    // Choose avatar based on type
    const avatarHTML = type === 'user' ? AVATAR_IMAGES.user : AVATAR_IMAGES.assistant;

    // Format content with HTML structure for both user and assistant
    const contentHTML = formatMessage(content);

    message.innerHTML = `
        <div class="message-avatar">${avatarHTML}</div>
        <div class="message-content">${contentHTML}</div>
    `;

    if (isError) {
        message.querySelector('.message-content').style.background = 'rgba(239, 68, 68, 0.1)';
        message.querySelector('.message-content').style.borderColor = 'var(--error)';
    }

    chatMessages.appendChild(message);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Track message in session
    if (!isError || !content.includes('Error:')) {
        sessionMessages.push({
            type: type,
            content: content,
            timestamp: new Date().toISOString()
        });
    }

    return message.querySelector('.message-content');
}

function showTyping() {
    const typingAvatar = typingIndicator.querySelector('.typing-avatar');
    typingAvatar.innerHTML = AVATAR_IMAGES.assistant;
    typingIndicator.style.display = 'flex';
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideTyping() {
    typingIndicator.style.display = 'none';
}

function autoResize() {
    messageInput.style.height = 'auto';
    messageInput.style.height = Math.min(messageInput.scrollHeight, 150) + 'px';
}

// Dark Mode Toggle
function loadThemePreference() {
    try {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    } catch (e) {
        console.warn('Failed to load theme preference:', e);
    }
}

function saveThemePreference(theme) {
    try {
        localStorage.setItem('theme', theme);
    } catch (e) {
        console.warn('Failed to save theme preference:', e);
    }
}

function toggleTheme() {
    try {
        const isDark = document.documentElement.classList.toggle('dark');
        saveThemePreference(isDark ? 'dark' : 'light');
    } catch (e) {
        console.error('Theme toggle failed:', e);
    }
}

// Theme toggle will be initialized in init() after themeToggle element is assigned

function formatQuiz(quizText) {
    // Remove code blocks entirely (triple backticks) to avoid language detection errors
    let withoutCodeBlocks = quizText.replace(/```[\s\S]*?```/g, '');

    // Remove markdown formatting symbols (# and *)
    let cleaned = withoutCodeBlocks
        .replace(/^#{1,6}\s+/gm, '')
        .replace(/\*\*(.*?)\*\*/g, '$1')
        .replace(/\*(.*?)\*/g, '$1')
        .replace(/__(.*?)__/g, '$1')
        .replace(/_(.*?)_/g, '$1');

    // Simple formatting: preserve line breaks, convert to paragraphs
    // Escape HTML to prevent XSS
    const escaped = escapeHtml(cleaned);
    // Replace double newlines with paragraph breaks
    const paragraphs = escaped.split(/\n\s*\n/).filter(p => p.trim());
    return paragraphs.map(p => `<p>${p.replace(/\n/g, '<br>')}</p>`).join('');
}

// ==================== AUTH UI HANDLERS ====================

// Check if user is logged in
async function checkAuth() {
    try {
        const response = await fetch('/auth/check');
        if (response.ok) {
            const data = await response.json();
            if (data.authenticated) {
                showUserMenu(data.user);
                // Load full profile to get avatar and other details
                loadUserProfile();
            } else {
                // Not authenticated - redirect to auth page
                window.location.href = '/auth';
            }
        } else {
            // Not authenticated
            window.location.href = '/auth';
        }
    } catch (error) {
        console.error('Auth check failed:', error);
    }
}

function showUserMenu(user) {
    if (userName) userName.textContent = user.name || 'User';
    if (userEmail) userEmail.textContent = user.email;
    userMenu.style.display = 'block';
}

function hideUserMenu() {
    if (userDropdown) userDropdown.style.display = 'none';
}

function toggleUserDropdown() {
    if (!userDropdown) return;
    if (userDropdown.style.display === 'none' || userDropdown.style.display === '') {
        userDropdown.style.display = 'block';
    } else {
        userDropdown.style.display = 'none';
    }
}

function handleDocumentClick(e) {
    // Close dropdown if clicking outside of user menu
    if (userMenu && userDropdown && !userMenu.contains(e.target)) {
        hideUserMenu();
    }
}

// ==================== SIDE DRAWER FUNCTIONS ====================

// Global profile state
let userProfile = null;
let userDocuments = [];

function openDrawer(initialTab = 'profile') {
    if (!sideDrawer || !drawerOverlay) return;

    // Show drawer and overlay
    sideDrawer.classList.add('active');
    drawerOverlay.classList.add('active');

    // Switch to initial tab
    switchDrawerTab(initialTab);
}

function closeDrawer() {
    if (sideDrawer && drawerOverlay) {
        sideDrawer.classList.remove('active');
        drawerOverlay.classList.remove('active');
    }
}

function switchDrawerTab(tabName) {
    // Update tab buttons
    drawerTabs.forEach(tab => {
        tab.classList.toggle('active', tab.dataset.drawerTab === tabName);
    });

    // Update tab content
    drawerProfileTab.classList.toggle('drawer-content-active', tabName === 'profile');
    drawerHistoryTab.classList.toggle('drawer-content-active', tabName === 'history');

    // If switching to history, reload documents
    if (tabName === 'history') {
        loadUserDocuments();
    }
}

async function loadUserProfile() {
    try {
        const response = await fetch('/profile');
        if (response.ok) {
            const data = await response.json();
            userProfile = data;
            renderUserProfile(data);
            updateUserAvatarInHeader(data);
        } else {
            console.error('Failed to load profile');
            showDrawerMessage(drawerProfileMessage, 'Failed to load profile', 'error');
        }
    } catch (error) {
        console.error('Profile fetch error:', error);
        showDrawerMessage(drawerProfileMessage, 'Error loading profile', 'error');
    }
}

function renderUserProfile(profile) {
    if (!drawerDisplayName || !drawerAvatarImg) return;

    // Set display name
    drawerDisplayName.value = profile.display_name || '';

    // Set avatar (with cache bust)
    if (profile.avatar_url) {
        drawerAvatarImg.src = profile.avatar_url + '?t=' + Date.now();
        drawerAvatarImg.style.display = 'block';
        drawerAvatarPlaceholder.style.display = 'none';
    } else {
        drawerAvatarImg.style.display = 'none';
        drawerAvatarPlaceholder.style.display = 'flex';
        drawerAvatarPlaceholder.textContent = (profile.display_name || '?')[0].toUpperCase();
    }
}

function updateUserAvatarInHeader(profile) {
    if (!userAvatarImg || !userAvatarPlaceholder) return;

    if (profile.avatar_url) {
        userAvatarImg.src = profile.avatar_url + '?t=' + Date.now();
        userAvatarImg.style.display = 'block';
        userAvatarPlaceholder.style.display = 'none';
    } else {
        userAvatarImg.style.display = 'none';
        userAvatarPlaceholder.style.display = 'flex';
        userAvatarPlaceholder.textContent = (profile.display_name || '?')[0].toUpperCase();
    }
}

async function handleAvatarUpload(file) {
    if (!file) return;

    // Validate file type
    const allowedTypes = ['image/png', 'image/jpeg', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
        alert('Only PNG, JPG, GIF, and WebP images are allowed.');
        return;
    }

    // Validate file size (2MB)
    if (file.size > 2 * 1024 * 1024) {
        alert('Avatar must be less than 2MB.');
        return;
    }

    const formData = new FormData();
    formData.append('avatar', file);

    try {
        const response = await fetch('/profile/avatar', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            // Update avatar preview
            drawerAvatarImg.src = data.avatar_url + '?t=' + Date.now(); // Cache bust
            drawerAvatarImg.style.display = 'block';
            drawerAvatarPlaceholder.style.display = 'none';
            showDrawerMessage(drawerProfileMessage, 'Avatar updated successfully!', 'success');

            // Update header avatar
            if (userAvatarImg) {
                userAvatarImg.src = data.avatar_url + '?t=' + Date.now();
                userAvatarImg.style.display = 'block';
                userAvatarPlaceholder.style.display = 'none';
            }
        } else {
            showDrawerMessage(drawerProfileMessage, data.error || 'Failed to upload avatar', 'error');
        }
    } catch (error) {
        console.error('Avatar upload error:', error);
        showDrawerMessage(drawerProfileMessage, 'Upload failed', 'error');
    }
}

async function saveProfile() {
    if (!drawerDisplayName) return;

    const displayName = drawerDisplayName.value.trim();
    if (!displayName) {
        showDrawerMessage(drawerProfileMessage, 'Display name is required', 'error');
        return;
    }

    try {
        const response = await fetch('/profile/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ display_name: displayName })
        });

        const data = await response.json();

        if (response.ok) {
            userProfile.display_name = displayName;
            showDrawerMessage(drawerProfileMessage, 'Profile updated successfully!', 'success');

            // Update header display
            if (userName) userName.textContent = displayName;
            updateUserAvatarInHeader(userProfile);
        } else {
            showDrawerMessage(drawerProfileMessage, data.error || 'Failed to update profile', 'error');
        }
    } catch (error) {
        console.error('Profile update error:', error);
        showDrawerMessage(drawerProfileMessage, 'Update failed', 'error');
    }
}

async function loadUserDocuments() {
    try {
        const response = await fetch('/history/documents');
        if (response.ok) {
            const data = await response.json();
            userDocuments = data.documents || [];
            renderDocumentList(userDocuments);
        } else {
            console.error('Failed to load document history');
            renderDocumentList([]);
        }
    } catch (error) {
        console.error('Document history error:', error);
        renderDocumentList([]);
    }
}

function formatDocumentDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function renderDocumentList(documents) {
    if (!drawerDocumentList) return;

    if (documents.length === 0) {
        drawerDocumentList.innerHTML = '<p class="drawer-empty">No documents yet. Upload your first document to get started!</p>';
        return;
    }

    const html = documents.map(doc => `
        <div class="drawer-document-card" data-doc-id="${doc.id}">
            <div class="drawer-doc-header">
                <span class="drawer-doc-name">${escapeHtml(doc.filename)}</span>
            </div>
            <div class="drawer-doc-meta">
                ${formatDocumentDate(doc.upload_date)} • ${formatFileSize(doc.file_size || 0)} • ${doc.file_type.toUpperCase()}
            </div>
            <div class="drawer-doc-actions">
                <button class="drawer-btn-small load-btn">Load</button>
                <button class="drawer-btn-small view-chat-btn">View Chat</button>
                <button class="drawer-btn-small danger delete-btn">Delete</button>
            </div>
        </div>
    `).join('');

    drawerDocumentList.innerHTML = html;
}

async function loadDocumentFromHistory(docId) {
    try {
        const response = await fetch('/documents/load', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ doc_id: docId })
        });

        const data = await response.json();

        if (response.ok) {
            currentDocId = docId;
            // Clear chat and show document
            chatMessages.innerHTML = '';
            const filename = data.filename;
            docName.textContent = filename;
            uploadSection.style.display = 'none';
            chatSection.style.display = 'flex';
            messageInput.disabled = false;
            sendButton.disabled = false;

            // Close drawer
            closeDrawer();

            // Show success message
            showMessage('File loaded from history. You can continue where you left off!');
        } else {
            alert('Failed to load document: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Load document error:', error);
        alert('Failed to load document');
    }
}

async function viewChatHistory(docId) {
    try {
        const response = await fetch(`/history/chat/${docId}`);
        if (response.ok) {
            const data = await response.json();
            renderChatHistoryView(data.messages, data.documents?.find(d => d.id === docId)?.filename || 'Document');
        } else {
            alert('Failed to load chat history');
        }
    } catch (error) {
        console.error('Chat history error:', error);
        alert('Failed to load chat history');
    }
}

function renderChatHistoryView(messages, filename) {
    if (!drawerChatMessages || !drawerChatDocName) return;

    drawerChatDocName.textContent = filename;
    drawerChatHistory.style.display = 'flex';

    if (!messages || messages.length === 0) {
        drawerChatMessages.innerHTML = '<p class="drawer-empty">No chat history for this document yet.</p>';
        return;
    }

    const html = messages.map(msg => {
        const role = msg.role === 'user' ? 'user' : 'assistant';
        const time = new Date(msg.timestamp).toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
        return `
            <div class="drawer-chat-message ${role}">
                ${formatMessage(msg.content)}
                <span class="drawer-chat-time">${time}</span>
            </div>
        `;
    }).join('');

    drawerChatMessages.innerHTML = html;
    drawerChatMessages.scrollTop = drawerChatMessages.scrollHeight;
}

async function deleteDocument(docId) {
    if (!confirm('Are you sure you want to delete this document and its chat history? This action cannot be undone.')) {
        return;
    }

    try {
        const response = await fetch('/documents/delete?doc_id=' + encodeURIComponent(docId), {
            method: 'DELETE'
        });

        if (response.ok) {
            // Remove from local array and re-render
            userDocuments = userDocuments.filter(d => d.id !== docId);
            renderDocumentList(userDocuments);

            // If this was the currently loaded doc, clear chat
            if (currentDocId === docId) {
                currentDocId = null;
                uploadSection.style.display = 'flex';
                chatSection.style.display = 'none';
                fileInput.value = '';
                hideFileInfo();
                hideError();
                messageInput.value = '';
                chatMessages.innerHTML = '';
                addMessage("Hey there! 👋 I've finished reading your document and I'm ready to help! Feel free to ask me anything about it - I'm here to make understanding it easy and enjoyable. What would you like to know first?", 'assistant');
                if (generateQuiz) generateQuiz.style.display = 'none';
                if (quizSection) quizSection.style.display = 'none';
            }
        } else {
            const error = await response.json();
            alert('Failed to delete document: ' + (error.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Delete document error:', error);
        alert('Failed to delete document');
    }
}

function showDrawerMessage(element, message, type) {
    if (!element) return;
    element.textContent = message;
    element.className = 'drawer-message ' + type;
    setTimeout(() => {
        element.className = 'drawer-message';
        element.textContent = '';
    }, 3000);
}

// Toast notification for general messages
function showMessage(message) {
    const toast = document.createElement('div');
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: var(--surface);
        color: var(--text-primary);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 12px 20px;
        box-shadow: var(--shadow-lg);
        z-index: 10000;
        max-width: 300px;
        animation: fadeIn 0.3s ease;
    `;
    document.body.appendChild(toast);

    // Add animation keyframes if not already present
    if (!document.getElementById('toast-styles')) {
        const style = document.createElement('style');
        style.id = 'toast-styles';
        style.textContent = `
            @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
            @keyframes fadeOut { from { opacity: 1; } to { opacity: 0; } }
        `;
        document.head.appendChild(style);
    }

    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s ease forwards';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
