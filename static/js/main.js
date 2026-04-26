document.addEventListener('DOMContentLoaded', () => {

    // DOM Elements
    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');
    const chatContainer = document.getElementById('chatContainer');
    const micBtn = document.getElementById('micBtn');
    const sendBtn = document.getElementById('sendBtn');
    const newChatBtn = document.getElementById('newChatBtn');
    const optionsBtn = document.getElementById('optionsBtn');
    const quickOptions = document.getElementById('quickOptions');
    const presetBtns = document.querySelectorAll('.preset-btn');
    
    // Toggle active state on send button when there is text
    chatInput.addEventListener('input', () => {
        if (chatInput.value.trim().length > 0) {
            sendBtn.classList.add('active');
        } else {
            sendBtn.classList.remove('active');
        }
    });

    // Simple markdown parsing to render **bold** texts
    const parseText = (text) => {
        let parsed = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        // Globally transform EcoAI into the beautiful gradient text
        parsed = parsed.replace(/EcoAI/g, '<span class="eco-brand-text">Eco-AI</span>');
        return parsed;
    };

    // Chat History State
    let chatHistory = JSON.parse(localStorage.getItem('eco_chats')) || [];
    let currentChatId = null;
    let selectMode = false;
    let selectedChatIds = new Set();

    const saveChats = () => {
        localStorage.setItem('eco_chats', JSON.stringify(chatHistory));
        renderSidebar();
    };

    // ── Context menu singleton ──────────────────────────────────────────────
    let activeCtxMenu = null;

    function closeContextMenu() {
        if (activeCtxMenu) {
            activeCtxMenu.remove();
            activeCtxMenu = null;
        }
    }

    document.addEventListener('click', closeContextMenu);
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeContextMenu(); });

    function showContextMenu(x, y, chat, titleSpan) {
        closeContextMenu();

        const menu = document.createElement('div');
        menu.className = 'history-context-menu';

        // ── Edit button ──────────────────────────────
        const editBtn = document.createElement('button');
        editBtn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg> Rename`;
        editBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            closeContextMenu();
            // Make title editable
            titleSpan.contentEditable = 'true';
            titleSpan.style.backgroundColor = 'rgba(255,255,255,0.1)';
            titleSpan.style.borderRadius = '4px';
            titleSpan.focus();
            const sel = window.getSelection();
            const range = document.createRange();
            range.selectNodeContents(titleSpan);
            sel.removeAllRanges();
            sel.addRange(range);
        });

        // ── Divider ──────────────────────────────────
        const divider = document.createElement('div');
        divider.className = 'ctx-divider';

        // ── Delete button ─────────────────────────────
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'ctx-delete';
        deleteBtn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4h6v2"/></svg> Delete`;
        deleteBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            closeContextMenu();
            if (confirm('Delete this chat?')) {
                chatHistory = chatHistory.filter(c => c.id !== chat.id);
                saveChats();
                if (currentChatId === chat.id) {
                    initNewChat();
                } else {
                    renderSidebar();
                }
            }
        });

        // ── Select Multiple button ───────────────────
        const selectBtn = document.createElement('button');
        selectBtn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14"/><path d="M12 5v14"/></svg> Select Multiple`;
        selectBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            closeContextMenu();
            selectMode = true;
            selectedChatIds.clear();
            selectedChatIds.add(chat.id);
            document.getElementById('bulkActions').classList.remove('hidden');
            renderSidebar();
        });

        menu.appendChild(editBtn);
        menu.appendChild(selectBtn);
        menu.appendChild(divider);
        menu.appendChild(deleteBtn);
        document.body.appendChild(menu);
        activeCtxMenu = menu;

        // Position — keep inside viewport
        const menuW = 170, menuH = 90;
        const left = Math.min(x, window.innerWidth  - menuW - 8);
        const top  = Math.min(y, window.innerHeight - menuH - 8);
        menu.style.left = left + 'px';
        menu.style.top  = top  + 'px';
    }

    const renderSidebar = () => {
        try {
            const sidebar = document.getElementById('sidebarHistory');
            if (!sidebar) return;

            console.log("Rendering sidebar with history length:", chatHistory.length);
            if (chatHistory.length === 0) {
                sidebar.innerHTML = '<p class="history-label">Previous Chats</p>';
                sidebar.innerHTML += '<p style="padding:10px; color:rgba(255,255,255,0.2); font-size:0.8rem;">No recent chats</p>';
                return;
            }

            sidebar.innerHTML = '<p class="history-label">Previous Chats</p>';
            [...chatHistory].reverse().forEach(chat => {
                if (!chat || !chat.id) return;

            const div = document.createElement('div');
            div.className = `history-item ${chat.id === currentChatId ? 'active' : ''} ${selectedChatIds.has(chat.id) ? 'selected' : ''}`;

            if (selectMode) {
                const cb = document.createElement('input');
                cb.type = 'checkbox';
                cb.checked = selectedChatIds.has(chat.id);
                cb.style.marginRight = '10px';
                cb.addEventListener('click', (e) => {
                    e.stopPropagation(); // prevent loading chat
                    if (cb.checked) selectedChatIds.add(chat.id);
                    else selectedChatIds.delete(chat.id);
                    renderSidebar();
                });
                div.appendChild(cb);
            }

            const titleSpan = document.createElement('span');
            titleSpan.textContent = chat.title;
            titleSpan.style.cssText = 'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;flex:1;outline:none;padding:2px 4px;border-radius:4px;';

            // Finish inline editing
            const finishEditing = () => {
                if (titleSpan.isContentEditable) {
                    titleSpan.contentEditable = 'false';
                    titleSpan.style.backgroundColor = 'transparent';
                    const newTitle = titleSpan.textContent.trim();
                    if (newTitle && newTitle !== chat.title) {
                        chat.title = newTitle;
                        saveChats();
                    } else {
                        titleSpan.textContent = chat.title;
                    }
                }
            };

            titleSpan.addEventListener('blur', finishEditing);
            titleSpan.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') { 
                    e.preventDefault(); 
                    e.stopPropagation();
                    titleSpan.blur(); 
                }
            });
            
            div.addEventListener('click', (e) => {
                if (selectMode) {
                    if (selectedChatIds.has(chat.id)) selectedChatIds.delete(chat.id);
                    else selectedChatIds.add(chat.id);
                    renderSidebar();
                    return;
                }
                if (titleSpan.contentEditable !== 'true') loadChat(chat.id);
            });

            div.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                if (!selectMode) showContextMenu(e.clientX, e.clientY, chat, titleSpan);
            });

            div.appendChild(titleSpan);
            sidebar.appendChild(div);
        });
        } catch (err) {
            console.error("Error rendering sidebar:", err);
        }
    };


    // Bulk Action Handlers
    document.getElementById('selectAllBtn')?.addEventListener('click', () => {
        if (selectedChatIds.size === chatHistory.length) {
            selectedChatIds.clear();
        } else {
            chatHistory.forEach(c => selectedChatIds.add(c.id));
        }
        renderSidebar();
    });

    document.getElementById('cancelSelectBtn')?.addEventListener('click', () => {
        selectMode = false;
        selectedChatIds.clear();
        document.getElementById('bulkActions').classList.add('hidden');
        renderSidebar();
    });

    document.getElementById('deleteSelectedBtn')?.addEventListener('click', () => {
        if (selectedChatIds.size === 0) return;
        if (confirm(`Delete ${selectedChatIds.size} selected chats?`)) {
            chatHistory = chatHistory.filter(c => !selectedChatIds.has(c.id));
            const activeDeleted = selectedChatIds.has(currentChatId);
            selectMode = false;
            selectedChatIds.clear();
            document.getElementById('bulkActions').classList.add('hidden');
            saveChats();
            if (activeDeleted) initNewChat();
            else renderSidebar();
        }
    });

    const initNewChat = () => {
        // If there's already an empty chat, just use it
        const existingEmpty = chatHistory.find(c => c.messages.length === 0);
        if (existingEmpty) {
            loadChat(existingEmpty.id);
            return;
        }

        currentChatId = 'chat_' + Date.now();
        sessionStorage.setItem('last_chat_id', currentChatId);
        chatHistory.push({
            id: currentChatId,
            title: 'New Chat',
            messages: []
        });
        saveChats();

        
        // Clear UI
        chatContainer.innerHTML = '';
        const welcome = document.getElementById('welcomeScreen');
        if (welcome) welcome.classList.remove('chat-active');
        
        // Restore buttons on a fresh chat
        const fuzzyContainer = document.querySelector('.fuzzy-options-container');
        if (fuzzyContainer) fuzzyContainer.classList.remove('hidden');
        
        renderSidebar();
    };


    const loadChat = (id) => {
        const chat = chatHistory.find(c => c.id === id);
        if (!chat) {
            console.warn("Chat not found, starting new session.");
            initNewChat();
            return;
        }

        currentChatId = id;
        sessionStorage.setItem('last_chat_id', id); 
        
        // Clear UI
        chatContainer.innerHTML = '';


        
        const welcome = document.getElementById('welcomeScreen');
        const fuzzyContainer = document.querySelector('.fuzzy-options-container');
        
        if (chat.messages && chat.messages.length > 0) {
            if (welcome) welcome.classList.add('chat-active');
            if (fuzzyContainer) fuzzyContainer.classList.add('hidden');
        } else {
            if (welcome) welcome.classList.remove('chat-active');
            if (fuzzyContainer) fuzzyContainer.classList.remove('hidden');
        }


        // Repopulate
        chat.messages.forEach(m => {
            appendMessageUI(m.text, m.sender);
        });
        renderSidebar();
    };

    // Initialize App: Always start with a fresh New Chat experience unless specifically returning from a result
    try {
        const lastSessionId = sessionStorage.getItem('last_chat_id');
        console.log("Initializing App. Last Session ID:", lastSessionId);
        if (lastSessionId && chatHistory.some(c => c && c.id === lastSessionId)) {
            loadChat(lastSessionId);
        } else {
            initNewChat();
        }
    } catch (initErr) {
        console.error("Initialization error:", initErr);
        initNewChat();
    }








    const appendMessageUI = (text, sender = 'user') => {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}`;
        
        // Polished User and Bot Icons
        const avatarSvg = sender === 'user' 
            ? '<svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>'
            : '<span class="golden-leaf">🌿</span>';
            
        let imgHtml = '';
        if (sender === 'bot') {
            const lowerText = text.toLowerCase();
            let keyword = '';
            if (lowerText.includes('solar')) keyword = 'solar panels';
            else if (lowerText.includes('wind')) keyword = 'wind turbines';
            else if (lowerText.includes('geothermal')) keyword = 'geothermal energy';
            else if (lowerText.includes('hydro')) keyword = 'hydroelectric plant';
            
            if (keyword && !text.includes('chat-result-card') && text !== 'Thinking...') {
                // Evergreen logic: Restoring impactful local images
                let imgFile = 'solar.png';
                if      (keyword.includes('solar'))      imgFile = 'solar.png';
                else if (keyword.includes('wind'))       imgFile = 'wind.png';
                else if (keyword.includes('hydro'))      imgFile = 'hydro.png';
                else if (keyword.includes('geothermal')) imgFile = 'geothermal.png';
                
                imgHtml = `<br><img src="/static/img/${imgFile}" alt="Energy concept" style="border-radius:12px; border:1px solid rgba(255,255,255,0.2); box-shadow: 0 4px 12px rgba(0,0,0,0.1); width:100%; max-height:220px; object-fit:cover;" />`;
            }
        }
            
        msgDiv.innerHTML = `
            <div class="avatar">${avatarSvg}</div>
            <div class="message-content" style="width: 100%; max-width: 800px;">
                ${(typeof text === 'string' && (text.includes('chat-result-card') || text.includes('chat-result-preview'))) ? text : parseText(String(text || ''))}
                ${imgHtml}
            </div>
        `;


        
        chatContainer.appendChild(msgDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    };

    const appendMessage = (text, sender = 'user') => {
        appendMessageUI(text, sender);
        
        // Save state
        const chat = chatHistory.find(c => c.id === currentChatId);
        if (chat) {
            chat.messages.push({ text, sender });
            saveChats();
        }
    };

    // Chatbot text-to-speech
    const speakText = (text) => {
        if (!window.speechSynthesis) return;

        // Cancel any pending speech
        window.speechSynthesis.cancel();
        
        // Remove markdown formatting
        const cleanText = text.replace(/\*\*(.*?)\*\*/g, '$1');
        const utterance = new SpeechSynthesisUtterance(cleanText);
        window.speechSynthesis.speak(utterance);
    };

    // ── Logic status check (Local fallback) ──────────────────────────
    let aiEnabled = true; 
    // We keep this to avoid breaking UI assumptions, but set to false.


    const sendChat = async (message) => {
        // Trigger welcome transition
        const welcome = document.getElementById('welcomeScreen');
        if (welcome) welcome.classList.add('chat-active');
        
        appendMessage(message, 'user');
        chatInput.value = '';
        sendBtn.classList.remove('active');
        chatInput.disabled = true;

        // Note: We no longer hide the fuzzy buttons immediately here.
        // They stay until a definitive result is found.

        // Step 1: Check with Python fuzzy inference first (to detect energy query)
        const loadingId = 'loading-' + Date.now();
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message bot';
        loadingDiv.id = loadingId;
        loadingDiv.innerHTML = `
            <div class="avatar">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M12 3L4 9v12h16V9l-8-6zm0 2.84l5 3.75v8.41h-10v-8.41l5-3.75zM12 10a3 3 0 100 6 3 3 0 000-6z"/></svg>
            </div>
            <div class="message-content">
                <span class="typing-dots"><span></span><span></span><span></span></span>
            </div>`;
        chatContainer.appendChild(loadingDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });

            const data = await res.json();
            document.getElementById(loadingId)?.remove();

            if (data.error) throw new Error(data.error);

            // ── ENERGY RESULT PATH ─────────────────────────────────────
            if (data.is_result) {
                // Now we hide the fuzzy buttons because the result is appearing
                const fuzzyContainer = document.querySelector('.fuzzy-options-container');
                if (fuzzyContainer) fuzzyContainer.classList.add('hidden');

                const pd   = data.prediction_data;
                const best = pd.best;
                const rnd  = Math.floor(Math.random() * 99999);

                const previewHtml = `
                    <div class="chat-result-preview">
                        <div class="preview-header">
                            <span class="preview-badge">Analysis Complete</span>
                        </div>
                        <div class="preview-content">
                            <p>Based on your conditions, the best renewable energy source for you is:</p>
                            <h3 class="preview-name">${best.name}</h3>
                            <button class="btn-view-more" id="btn-view-${rnd}">
                                View Full Analysis
                            </button>
                        </div>
                    </div>`;

                appendMessage(previewHtml, 'bot');

                // Auto-Redirection logic: Automatically opening result page for the user
                const resultData = {
                    energy_type:           best.type,
                    title:                 best.name             || best.type,
                    sub_type:              best.sub_type         || '',
                    description:           best.advantage        || '',
                    estimated_cost:        best.estimated_cost   || '—',
                    payback_period:        best.payback_duration || '—',
                    environmental_impact:  best.environmental_impact || '—',
                    precaution:            best.precaution       || '—',
                    care:                  best.care             || '—',
                    installation_location: best.installation_location || '—',
                    area_required:         best.area_required    || '—',
                    roi:                   best.roi              || '—',
                    confidence:            best.confidence       || '',
                    all_scores:            pd.all_scores         || {},
                    installation_guide:    best.installation_guide || '',
                    safety_plan:           best.safety_plan      || '',
                    detailed_impact:       best.detailed_impact  || '',
                    financial_roi:         best.financial_roi    || '',
                    government_subsidy:    best.government_subsidy || '',
                    government_subsidy_detailed: best.government_subsidy_detailed || '',
                    temperature:           data.temperature
                };
                sessionStorage.setItem('eco_ai_result', JSON.stringify(resultData));

                // Manual Redirection logic: The user must click the button to see the result
                const viewBtn = document.getElementById(`btn-view-${rnd}`);
                if (viewBtn) {
                    viewBtn.addEventListener('click', () => {
                        sessionStorage.setItem('last_chat_id', currentChatId);
                        window.location.href = '/result';
                    });
                }



                const currentSession = chatHistory.find(c => c.id === currentChatId);
                if (currentSession && currentSession.title === 'New Chat') {
                    currentSession.title = `${best.type} Analysis`;
                    saveChats();
                }
                speakText(`Analysis complete. Top recommendation: ${best.name}. Click View Full Analysis for complete details.`);
                return;
            }

            // ── CONVERSATIONAL PATH ──────────────────────────────────────
            const currentSession = chatHistory.find(c => c.id === currentChatId);
            if (currentSession && currentSession.title === 'New Chat') {
                // Generate a short title from the first message
                let newTitle = message.charAt(0).toUpperCase() + message.slice(1);
                if (newTitle.length > 20) newTitle = newTitle.substring(0, 20) + '...';
                currentSession.title = newTitle;
                saveChats();
            }


            // Local synchronous response handler
            const reply = data.reply || "I'm processing your request locally...";
            appendMessage(reply, 'bot');
            speakText(reply);

        } catch (err) {
            console.error(err);
            document.getElementById(loadingId)?.remove();
            appendMessage('Sorry, I encountered an error. Please check server logs.', 'bot');
        } finally {
            chatInput.disabled = false;
            chatInput.focus();
        }
    };

    chatForm.addEventListener('submit', (e) => {

        e.preventDefault();
        const msg = chatInput.value.trim();
        if (msg) {
            sendChat(msg);
        }
    });

    /* ── Voice Assistant / Web Speech API ──────────────── */
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition = null;
    let isRecording = false;

    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            isRecording = true;
            micBtn.classList.add('recording');
            chatInput.placeholder = "Listening...";
            // stop synthetic speech if it's currently talking
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
            }
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            chatInput.value = transcript;
            sendBtn.classList.add('active');
            // Auto submit if spoken
            if (transcript) sendChat(transcript);
        };

        recognition.onend = () => {
            isRecording = false;
            micBtn.classList.remove('recording');
            chatInput.placeholder = "Message EcoAI...";
        };

        recognition.onerror = (event) => {
            console.error("Speech recognition error", event.error);
            isRecording = false;
            micBtn.classList.remove('recording');
            chatInput.placeholder = "Message EcoAI...";
        };

        micBtn.addEventListener('click', () => {
            if (isRecording) {
                recognition.stop();
            } else {
                recognition.start();
            }
        });
    } else {
        micBtn.style.display = 'none'; // Hide if not supported
        console.warn("Speech Recognition API not supported in this browser.");
    }
    
    // Stop any ongoing speech if user types or sends new chat
    chatInput.addEventListener('keydown', () => {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
        }
    });

    /* ── New Chat Logic ─────────────────────────── */
    newChatBtn.addEventListener('click', () => {
        initNewChat();
    });

    /* ── Quick Options Logic ────────────────────── */
    optionsBtn.addEventListener('click', () => {
        quickOptions.classList.toggle('hidden');
    });

    presetBtns.forEach(btn => {
        if (btn.classList.contains('fuzzy-btn')) return; // handled separately
        btn.addEventListener('click', (e) => {
            const val = e.target.textContent;
            chatInput.value = val;
            quickOptions.classList.add('hidden');
            sendBtn.classList.add('active');
            chatInput.focus();
        });
    });

    /* ── Fuzzy Value Generation Logic ──────────────────────────── */
    const fuzzyBtns = document.querySelectorAll('.fuzzy-btn');
    fuzzyBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const target = e.currentTarget;
            const type   = target.getAttribute('data-type');
            const val    = target.getAttribute('data-val') || '';
            const min    = parseFloat(target.getAttribute('data-min') || '0');
            const max    = parseFloat(target.getAttribute('data-max') || '0');

            let txt = '';
            if (type === 'temp') {
                const randomVal = Math.floor(Math.random() * (max - min + 1)) + min;
                txt = `Temperature: ${randomVal}°C`;
            } else if (type === 'hum') {
                const randomVal = Math.floor(Math.random() * (max - min + 1)) + min;
                txt = `Humidity: ${randomVal}%`;
            } else if (type === 'wind') {
                const randomVal = (Math.random() * (max - min) + min).toFixed(1);
                txt = `Wind speed: ${randomVal} m/s`;
            } else if (type === 'budget') {
                const randomVal = Math.floor(Math.random() * (max - min + 1)) + min;
                const isUSD = document.getElementById('currencyToggle')?.checked;
                const symbol = isUSD ? '$' : '₹';
                txt = `Budget: ${symbol}${randomVal.toLocaleString()}`;
            } else if (type === 'loc') {
                txt = val;
            }

            if (txt) {
                if (chatInput.value.length > 0 && !chatInput.value.endsWith(' ')) {
                    chatInput.value += ', ' + txt;
                } else {
                    chatInput.value += txt;
                }
                sendBtn.classList.add('active');
                chatInput.focus();
            }

            if (quickOptions) quickOptions.classList.add('hidden');
        });
    });


    /* ── Geolocation Logic ────────────────────────────── */
    const locationBtn = document.getElementById('locationBtn');
    if (locationBtn) {
        locationBtn.addEventListener('click', () => {
            if (navigator.geolocation) {
                locationBtn.classList.add('recording'); // Re-use recording class for pulse
                chatInput.placeholder = "Getting location...";
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        locationBtn.classList.remove('recording');
                        chatInput.placeholder = "Message Eco-AI...";
                        const lat = position.coords.latitude.toFixed(4);
                        const lon = position.coords.longitude.toFixed(4);
                        const text = `Latitude: ${lat}, Longitude: ${lon}. `;
                        chatInput.value = chatInput.value ? chatInput.value + " " + text : text;
                        sendBtn.classList.add('active');
                        chatInput.focus();
                    },
                    (error) => {
                        locationBtn.classList.remove('recording');
                        chatInput.placeholder = "Message Eco-AI...";
                        // Force a beautiful fallback if GPS is blocked/times out
                        const text = `Latitude: 34.05, Longitude: -118.24 (Fallback). `;
                        chatInput.value = chatInput.value ? chatInput.value + " " + text : text;
                        sendBtn.classList.add('active');
                        chatInput.focus();
                        alert("Unable to natively retrieve your precision coordinates (timeout or permission denied). A fallback location has been appended instead.");
                    },
                    { timeout: 4000 } // Force a break after 4 seconds
                );
            } else {
                alert("Geolocation is not supported by your browser.");
            }
        });
    }

    /* ── Render User Authentication State Context ─────────────────────────── */
    const activeUser = sessionStorage.getItem('active_user');
    const loginBtn = document.getElementById('topLoginBtn');
    const profileContainer = document.getElementById('topProfileContainer');
    const userNameDisplay = document.getElementById('userNameDisplay');
    const logoutBtn = document.getElementById('logoutBtn');
    
    if (activeUser && loginBtn && profileContainer) {
        // Toggle UI
        loginBtn.classList.add('hidden');
        profileContainer.classList.remove('hidden');

        // Manage Display Name (defaults to the literal username mapping)
        const displayNames = JSON.parse(localStorage.getItem('eco_display_names')) || {};
        const cachedName = displayNames[activeUser] || activeUser;
        
        userNameDisplay.textContent = cachedName;

        // Save inline display name edits natively
        const saveDisplayName = () => {
            const newName = userNameDisplay.textContent.trim();
            if (newName) {
                const namesDb = JSON.parse(localStorage.getItem('eco_display_names')) || {};
                namesDb[activeUser] = newName;
                localStorage.setItem('eco_display_names', JSON.stringify(namesDb));
            } else {
                userNameDisplay.textContent = displayNames[activeUser] || activeUser;
            }
            userNameDisplay.blur();
        };

        userNameDisplay.addEventListener('blur', saveDisplayName);
        userNameDisplay.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                saveDisplayName();
            }
        });

        // Independent Secure Logout Workflow
        logoutBtn.addEventListener('click', () => {
            if (confirm(`Log out out of ${activeUser}'s account?`)) {
                sessionStorage.removeItem('active_user');
                window.location.reload();
            }
        });
    }
});
