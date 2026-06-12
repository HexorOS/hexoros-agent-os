(function() {
    console.log("HexorOS Widget: Initializing...");
    // Config
    const scriptTag = document.currentScript || document.querySelector('script[src*="hexor-widget.js"]');
    if (!scriptTag) {
        console.error("HexorOS Widget: Could not find script tag!");
        return;
    }
    const businessName = scriptTag.getAttribute('data-business-name') || 'HexorOS Agent';
    const businessContext = scriptTag.getAttribute('data-context') || '';
    const apiEndpoint = scriptTag.getAttribute('data-api-endpoint') || 'http://localhost:8000/api/widget/chat';
    const primaryColor = scriptTag.getAttribute('data-color') || '#00f2ff';
    
    console.log("HexorOS Widget: Config loaded for", businessName);

    // CSS
    const style = document.createElement('style');
    style.innerHTML = `
        :root { --hexor-primary: ${primaryColor}; --hexor-bg: #0a0a0a; --hexor-text: #e0e0e0; }
        #hexor-widget-container { 
            position: fixed; bottom: 20px; right: 20px; z-index: 999999; 
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            pointer-events: none; /* Allow clicks to pass through transparent areas */
        }
        #hexor-widget-container.open {
            pointer-events: auto; /* Capture events on full overlay if active */
        }
        
        #hexor-chat-button {
            width: 60px; height: 60px; border-radius: 50%; background: var(--hexor-bg);
            border: 2px solid var(--hexor-primary); display: flex; align-items: center; justify-content: center;
            cursor: pointer; box-shadow: 0 0 15px var(--hexor-primary); transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            pointer-events: auto;
        }
        #hexor-chat-button:hover { transform: scale(1.1); }
        #hexor-chat-button svg { width: 30px; height: 30px; fill: var(--hexor-primary); }

        #hexor-chat-window {
            position: absolute; bottom: 80px; right: 0; width: 350px; height: 500px;
            background: rgba(10, 10, 10, 0.95); border: 1px solid rgba(0, 242, 255, 0.2);
            border-radius: 16px; display: none; flex-direction: column; overflow: hidden;
            box-shadow: 0 10px 40px rgba(0,0,0,0.5); backdrop-filter: blur(10px);
            pointer-events: auto;
        }
        #hexor-chat-window.open { display: flex; animation: hexor-fade-in 0.3s ease; }

        @keyframes hexor-fade-in { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

        #hexor-chat-header {
            padding: 15px; background: rgba(0, 242, 255, 0.1); border-bottom: 1px solid rgba(0, 242, 255, 0.2);
            display: flex; align-items: center; justify-content: space-between;
        }
        #hexor-chat-header h3 { margin: 0; font-size: 16px; color: var(--hexor-primary); font-weight: 600; }
        
        #hexor-chat-messages { flex: 1; overflow-y: auto; padding: 15px; display: flex; flex-direction: column; gap: 10px; }
        .hexor-msg { max-width: 80%; padding: 10px 14px; border-radius: 12px; font-size: 14px; line-height: 1.4; }
        .hexor-msg.agent { align-self: flex-start; background: rgba(255,255,255,0.05); color: var(--hexor-text); border: 1px solid rgba(255,255,255,0.1); }
        .hexor-msg.user { align-self: flex-end; background: var(--hexor-primary); color: #000; font-weight: 500; }

        #hexor-chat-input-area { padding: 15px; background: rgba(255,255,255,0.02); border-top: 1px solid rgba(255,255,255,0.1); display: flex; gap: 10px; }
        #hexor-chat-input {
            flex: 1; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
            border-radius: 8px; padding: 8px 12px; color: #fff; outline: none; font-size: 16px; /* 16px prevents iOS Safari auto-zoom */
        }
        #hexor-chat-input:focus { border-color: var(--hexor-primary); }
        #hexor-send-btn { background: none; border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; }
        #hexor-send-btn svg { width: 20px; height: 20px; fill: var(--hexor-primary); }

        .hexor-typing { display: flex; gap: 4px; padding: 10px; opacity: 0.7; }
        .hexor-dot { width: 4px; height: 4px; background: var(--hexor-primary); border-radius: 50%; animation: hexor-bounce 1.4s infinite ease-in-out; }
        .hexor-dot:nth-child(1) { animation-delay: -0.32s; }
        .hexor-dot:nth-child(2) { animation-delay: -0.16s; }
        @keyframes hexor-bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }

        /* Responsive Mobile Layout (Full Screen Chat for pristine mobile typing experience) */
        @media (max-width: 768px) {
            #hexor-widget-container {
                bottom: 0 !important;
                right: 0 !important;
                left: 0 !important;
                top: 0 !important;
                width: 100% !important;
                height: 100% !important;
            }
            #hexor-widget-container.open {
                pointer-events: auto !important;
            }
            #hexor-chat-window {
                position: fixed !important;
                bottom: 0 !important;
                right: 0 !important;
                left: 0 !important;
                top: 0 !important;
                width: 100% !important;
                height: 100% !important;
                border-radius: 0 !important;
                border: none !important;
                max-height: 100% !important;
            }
            #hexor-chat-button {
                position: fixed !important;
                bottom: 20px !important;
                right: 20px !important;
                z-index: 1000000 !important;
                pointer-events: auto !important;
            }
            #hexor-widget-container.open #hexor-chat-button {
                display: none !important;
            }
        }
    `;
    document.head.appendChild(style);

    // Detect Language
    let lang = 'en'; // default
    const docLang = document.documentElement.lang ? document.documentElement.lang.toLowerCase() : '';
    const path = window.location.pathname.toLowerCase();
    
    if (docLang.startsWith('de') || path.includes('/de') || path.includes('_de.html') || path.includes('impressum_de') || path.includes('privacy_de') || path.includes('terms_de')) {
        lang = 'de';
    } else if (docLang.startsWith('es') || path.includes('/es') || path.includes('_es.html') || path.includes('impressum_es') || path.includes('privacy_es') || path.includes('terms_es')) {
        lang = 'es';
    }

    const greetings = {
        en: `Hi! How can I help you with <b>${businessName}</b> today?`,
        de: `Hallo! Wie kann ich Ihnen heute bei <b>${businessName}</b> behilflich sein?`,
        es: `¡Hola! ¿Cómo puedo ayudarte con <b>${businessName}</b> hoy?`
    };
    
    const placeholders = {
        en: "Write a message...",
        de: "Nachricht schreiben...",
        es: "Escribir mensaje..."
    };

    const errorMessages = {
        en: "Sorry, there was a connection issue. Please try again later.",
        de: "Entschuldigung, es gab ein Verbindungsproblem. Bitte versuchen Sie es später erneut.",
        es: "Lo siento, hubo un problema de conexión. Por favor, inténtelo de nuevo más tarde."
    };

    const greetingText = greetings[lang] || greetings.en;
    const placeholderText = placeholders[lang] || placeholders.en;
    const errorMessageText = errorMessages[lang] || errorMessages.en;

    // Load History from sessionStorage
    const storageKey = `hexor_chat_history_${businessName.replace(/[^a-zA-Z0-9]/g, '_')}`;
    let messageHistory = [];
    try {
        const stored = sessionStorage.getItem(storageKey);
        if (stored) {
            messageHistory = JSON.parse(stored);
        }
    } catch (e) {
        console.error("Failed to load chat history:", e);
    }

    function saveHistory() {
        try {
            sessionStorage.setItem(storageKey, JSON.stringify(messageHistory));
        } catch (e) {
            console.error("Failed to save chat history:", e);
        }
    }

    // DOM
    const container = document.createElement('div');
    container.id = 'hexor-widget-container';
    container.innerHTML = `
        <div id="hexor-chat-window">
            <div id="hexor-chat-header">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <img src="/assets/logo_icon.png?v=29" alt="HexorOS" style="width: 20px; height: 20px; object-fit: contain;">
                    <h3>${businessName}</h3>
                </div>
                <button id="hexor-close-btn" style="background:none; border:none; color:rgba(255,255,255,0.5); cursor:pointer;">✕</button>
            </div>
            <div id="hexor-chat-messages">
                <!-- Messages populated dynamically -->
            </div>
            <div id="hexor-chat-input-area">
                <input type="text" id="hexor-chat-input" placeholder="${placeholderText}" autocomplete="off">
                <button id="hexor-send-btn">
                    <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
                </button>
            </div>
        </div>
        <div id="hexor-chat-button">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/></svg>
        </div>
    `;
    document.body.appendChild(container);

    const chatWindow = document.getElementById('hexor-chat-window');
    const chatButton = document.getElementById('hexor-chat-button');
    const closeBtn = document.getElementById('hexor-close-btn');
    const chatInput = document.getElementById('hexor-chat-input');
    const sendBtn = document.getElementById('hexor-send-btn');
    const messagesContainer = document.getElementById('hexor-chat-messages');

    // Populate Messages from History or add Greeting
    if (messageHistory.length === 0) {
        addMessage(greetingText, 'agent');
        messageHistory.push({ text: greetingText, side: 'agent' });
        saveHistory();
    } else {
        messageHistory.forEach(msg => {
            const div = document.createElement('div');
            div.className = `hexor-msg ${msg.side}`;
            div.innerHTML = msg.side === 'agent' ? mdToHtml(msg.text) : msg.text;
            messagesContainer.appendChild(div);
        });
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Toggle
    chatButton.onclick = () => {
        chatWindow.classList.toggle('open');
        container.classList.toggle('open');
    };
    closeBtn.onclick = () => {
        chatWindow.classList.remove('open');
        container.classList.remove('open');
    };

    // Send Message
    async function sendMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        // Add User Message
        addMessage(text, 'user');
        messageHistory.push({ text: text, side: 'user' });
        saveHistory();
        chatInput.value = '';

        // Add Typing Indicator
        const typingId = addTypingIndicator();
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        try {
            const response = await fetch(apiEndpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: text,
                    business_name: businessName,
                    context: businessContext
                })
            });

            if (!response.ok) {
                throw new Error('HTTP ' + response.status);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let agentMsgId = addMessage('', 'agent');
            removeTypingIndicator(typingId);

            let fullText = '';
            let incompleteBuffer = '';  // Buffer for partial NDJSON lines across chunks

            while (true) {
                const { done, value } = await reader.read();
                if (done) {
                    // Flush any remaining buffer content
                    if (incompleteBuffer.trim()) {
                        try {
                            const data = JSON.parse(incompleteBuffer);
                            if (data.response) {
                                fullText += data.response;
                                updateMessage(agentMsgId, fullText);
                            }
                        } catch (e) { /* ignore incomplete final line */ }
                    }
                    break;
                }

                // Prepend any previously incomplete line to the new chunk
                const combined = incompleteBuffer + decoder.decode(value, { stream: true });
                const lines = combined.split('\n');

                // The last element may be an incomplete line — save for next iteration
                incompleteBuffer = lines.pop();

                for (const line of lines) {
                    if (!line.trim()) continue;
                    try {
                        const data = JSON.parse(line);
                        if (data.response) {
                            fullText += data.response;
                            updateMessage(agentMsgId, fullText);
                        }
                        if (data.error) {
                            console.error("Widget API error:", data.error);
                        }
                    } catch (e) {
                        // Silently skip lines that still can't be parsed
                    }
                }
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }

            // Save completed agent response to history
            if (fullText) {
                messageHistory.push({ text: fullText, side: 'agent' });
                saveHistory();
            }
        } catch (err) {
            console.error("Widget Chat Error:", err);
            removeTypingIndicator(typingId);
            addMessage(errorMessageText, 'agent');
            messageHistory.push({ text: errorMessageText, side: 'agent' });
            saveHistory();
        }
    }

    // Lightweight markdown → HTML for agent messages (no external dependency)
    function mdToHtml(text) {
        if (!text) return '';

        // Step 1: Escape HTML to prevent XSS
        text = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

        // Step 2: Horizontal rules ---
        text = text.replace(/^---$/gm, '<hr style="border:none;border-top:1px solid rgba(255,255,255,0.15);margin:12px 0">');

        // Step 3: Markdown tables — convert before other inline formatting
        // Match table blocks: lines starting with |, separated by newlines
        text = text.replace(/(^\|.+\n)(\|[-| :]+\|\n)?((?:^\|.+\n?)*)/gm, function(match) {
            var lines = match.trim().split('\n').map(function(l) { return l.trim(); });
            if (lines.length < 2) return match;
            // Check if second line is a separator (contains only | - : spaces)
            var sepLine = lines[1] || '';
            var hasSeparator = /^\|[-| :]+\|?$/.test(sepLine);
            var dataLines = hasSeparator ? lines.slice(2) : lines.slice(1);
            var headerLine = lines[0];

            var html = '<table style="width:100%;border-collapse:collapse;margin:8px 0;font-size:13px">';

            // Header row
            var cells = headerLine.split('|').filter(function(c) { return c.trim(); });
            html += '<thead><tr>';
            cells.forEach(function(c) {
                html += '<th style="border:1px solid rgba(255,255,255,0.15);padding:6px 10px;text-align:left;background:rgba(0,242,255,0.08);color:var(--hexor-primary);font-weight:700">' + c.trim() + '</th>';
            });
            html += '</tr></thead>';

            // Data rows
            html += '<tbody>';
            dataLines.forEach(function(line) {
                if (!line.trim() || !line.startsWith('|')) return;
                var rowCells = line.split('|').filter(function(c) { return c.trim(); });
                html += '<tr>';
                rowCells.forEach(function(c) {
                    html += '<td style="border:1px solid rgba(255,255,255,0.08);padding:5px 10px;color:var(--hexor-text)">' + c.trim() + '</td>';
                });
                html += '</tr>';
            });
            html += '</tbody></table>';

            return html;
        });

        // Step 4: Headers ###
        text = text.replace(/^### (.+)$/gm, '<h4 style="color:var(--hexor-primary);font-size:14px;font-weight:700;margin:12px 0 4px 0;text-transform:uppercase;letter-spacing:0.05em">$1</h4>');

        // Step 5: Inline formatting (safe to do now, inside non-table HTML)
        // Inline code
        text = text.replace(/`([^`]+)`/g, '<code style="background:rgba(255,255,255,0.1);padding:1px 5px;border-radius:3px;font-size:12px">$1</code>');
        // Bold
        text = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        // Italic
        text = text.replace(/\*([^*]+)\*/g, '<em>$1</em>');

        // Step 6: Numbered lists (lines starting with digit.)
        text = text.replace(/^\d+\.\s+(.+)$/gm, '<li style="margin-left:18px;list-style:decimal">$1</li>');
        text = text.replace(/((?:<li style="margin-left:18px;list-style:decimal">.*<\/li>\n?)+)/g, '<ol style="margin:4px 0;padding:0 0 0 8px">$1</ol>');

        // Step 7: Bullet lists
        text = text.replace(/^[-*]\s+(.+)$/gm, '<li style="margin-left:12px;list-style:disc">$1</li>');
        // Wrap consecutive <li> in <ul> (avoid double-wrapping)
        text = text.replace(/((?:<li style="margin-left:12px;list-style:disc">.*<\/li>\n?)+)/g, '<ul style="margin:4px 0;padding:0 0 0 8px">$1</ul>');

        // Step 8: Paragraphs — double newlines become <p>, single newlines become <br>
        // But avoid wrapping block-level elements already generated
        var blockTags = ['<table', '<h4 ', '<ul ', '<ol ', '<hr ', '<li '];
        var blocks = text.split(/\n{2,}/);
        var result = [];
        for (var i = 0; i < blocks.length; i++) {
            var block = blocks[i].trim();
            if (!block) continue;
            var isBlock = false;
            for (var j = 0; j < blockTags.length; j++) {
                if (block.indexOf(blockTags[j]) === 0) { isBlock = true; break; }
            }
            if (isBlock) {
                result.push(block);
            } else {
                // Replace single newlines with <br> inside paragraph text
                var withBreaks = block.replace(/\n/g, '<br>');
                result.push('<p style="margin:8px 0;line-height:1.6">' + withBreaks + '</p>');
            }
        }
        return result.join('\n');
    }

    function addMessage(text, side) {
        const id = 'msg-' + Date.now();
        const div = document.createElement('div');
        div.id = id;
        div.className = `hexor-msg ${side}`;
        div.innerHTML = side === 'agent' ? mdToHtml(text) : text;
        messagesContainer.appendChild(div);
        return id;
    }

    function updateMessage(id, text) {
        const div = document.getElementById(id);
        if (div) div.innerHTML = mdToHtml(text);
    }

    function addTypingIndicator() {
        const id = 'typing-' + Date.now();
        const div = document.createElement('div');
        div.id = id;
        div.className = 'hexor-typing';
        div.innerHTML = '<div class="hexor-dot"></div><div class="hexor-dot"></div><div class="hexor-dot"></div>';
        messagesContainer.appendChild(div);
        return id;
    }

    function removeTypingIndicator(id) {
        const div = document.getElementById(id);
        if (div) div.remove();
    }

    sendBtn.onclick = sendMessage;
    chatInput.onkeypress = (e) => { if (e.key === 'Enter') sendMessage(); };

})();
