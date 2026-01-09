document.addEventListener("DOMContentLoaded", () => {
    // --- Seleção de Elementos do DOM ---
    const chatBox = document.getElementById("chat-box");
    const chatForm = document.getElementById("chat-form");
    const messageInput = document.getElementById("message-input");
    const attachmentButton = document.getElementById("attachment-button");
    const fileInput = document.getElementById("file-input");
    const attachmentPreviewContainer = document.getElementById("attachment-preview-container");
    const attachmentPreview = document.getElementById("attachment-preview");
    const removeAttachmentBtn = document.getElementById("remove-attachment-btn");
    const micButton = document.getElementById("mic-button");
    const recordingTimer = document.getElementById("recording-timer");

    // --- Seleção dos Templates ---
    const messageTemplate = document.getElementById("message-template");
    const movieCardTemplate = document.getElementById("movie-card-template");
    const recommendationsTemplate = document.getElementById("recommendations-template");

    // --- Estado da Aplicação ---
    let attachedFile = null;
    let mediaRecorder;
    let audioChunks = [];
    let recordingInterval;
    let secondsRecorded = 0;
    const originalPlaceholder = messageInput.placeholder;

    // --- Funções de Renderização ---

    function renderMessage(sender, contentGenerator) {
        const messageClone = messageTemplate.content.cloneNode(true);
        const wrapper = messageClone.querySelector('.message-wrapper');
        const messageDiv = messageClone.querySelector('.message');

        wrapper.classList.add(sender);
        messageDiv.classList.add(sender);
        
        // A função contentGenerator é responsável por criar o conteúdo interno
        contentGenerator(messageDiv);

        chatBox.appendChild(wrapper);
        scrollToBottom();
        return wrapper;
    }

    function renderTextMessage(container, text) {
        // Limpa o container primeiro
        container.innerHTML = '';
        const textNode = document.createTextNode(text || '');
        container.appendChild(textNode);
    }

    function renderUserMessage(text, file) {
        renderMessage('user', (messageDiv) => {
            if (file) {
                const fileURL = URL.createObjectURL(file);
                let attachmentElement;
                if (file.type.startsWith('image/')) {
                    attachmentElement = document.createElement('img');
                } else if (file.type.startsWith('video/')) {
                    attachmentElement = document.createElement('video');
                    attachmentElement.controls = true;
                } else if (file.type.startsWith('audio/')) {
                    attachmentElement = document.createElement('audio');
                    attachmentElement.controls = true;
                }
                if (attachmentElement) {
                    attachmentElement.src = fileURL;
                    attachmentElement.classList.add('user-attachment');
                    messageDiv.appendChild(attachmentElement);
                }
            }
            if (text) {
                const textElement = document.createElement('p');
                textElement.textContent = text;
                messageDiv.appendChild(textElement);
            }
        });
    }

    function renderMovieCard(container, movie) {
        container.classList.add("movie-card-bubble");
        const cardClone = movieCardTemplate.content.cloneNode(true);

        const posterImg = cardClone.querySelector('.poster-img');
        
        console.log('🎬 Renderizando filme:', movie.title);
        console.log('📦 Objeto movie completo:', JSON.stringify(movie, null, 2));
        console.log('🔍 Tipo de movie.poster_url:', typeof movie.poster_url);
        console.log('🔍 Valor de movie.poster_url:', movie.poster_url);
        
        let posterUrl = movie.poster_url;
        
        // Verifica se poster_url existe e é válido
        if (!posterUrl || posterUrl === 'null' || posterUrl === 'None' || posterUrl === null || posterUrl === undefined) {
            console.warn('⚠️ Poster URL não disponível ou inválido');
            posterUrl = 'https://via.placeholder.com/120x180?text=Sem+Pôster';
        } else {
            // Verifica se é uma URL válida
            if (!posterUrl.startsWith('http://') && !posterUrl.startsWith('https://')) {
                console.warn('⚠️ Poster URL não é uma URL válida:', posterUrl);
                posterUrl = 'https://via.placeholder.com/120x180?text=URL+Inválida';
            }
        }
        
        console.log('🖼️ Poster URL final que será usada:', posterUrl);
        
        // Limpa qualquer src anterior
        posterImg.src = '';
        posterImg.alt = `Pôster de ${movie.title}`;
        
        // Força o carregamento da imagem
        const img = new Image();
        img.crossOrigin = 'anonymous'; // Tenta resolver problemas de CORS
        
        img.onload = function() {
            console.log('✅ Imagem carregada com sucesso:', posterUrl);
            console.log('✅ Dimensões:', this.naturalWidth, 'x', this.naturalHeight);
            posterImg.src = posterUrl;
            posterImg.style.display = 'block';
        };
        
        img.onerror = function() {
            console.error('❌ Erro ao carregar imagem. URL tentada:', posterUrl);
            console.error('❌ Tentando sem crossOrigin...');
            // Tenta sem crossOrigin
            posterImg.crossOrigin = null;
            posterImg.src = posterUrl;
            posterImg.onerror = function() {
                console.error('❌ Erro persistente ao carregar imagem');
                this.style.display = 'none';
            };
        };
        
        // Inicia o carregamento
        img.src = posterUrl;
        cardClone.querySelector('.title-text').textContent = movie.title;
        cardClone.querySelector('.movie-year').textContent = `(${movie.year})`;
        cardClone.querySelector('.genres-text').textContent = movie.genres;
        cardClone.querySelector('.rating-text').textContent = movie.rating;
        cardClone.querySelector('.movie-overview').textContent = movie.overview;

        const actionsContainer = cardClone.querySelector('.movie-actions');
        
        // Botão de Assistir
        if (movie.imdb_id) {
            const vastParam = '?&vast=https://pubads.g.doubleclick.net/gampad/ads?iu=/21775744923/external/vmap_ad_samples&sz=640x480&cust_params=sample_ar%3Dpreonly&ciu_szs=300x250&gdfp_req=1&output=vmap&unviewed_position_start=1&env=vp&impl=s&correlator';
            const watchUrl = movie.media_type === 'movie'
                ? `https://vidsrc.xyz/embed/movie/${movie.imdb_id}`
                : `https://vidsrc.xyz/embed/tv/${movie.imdb_id}`;
            
            const watchButton = document.createElement('a');
            watchButton.href = watchUrl;
            watchButton.target = "_blank";
            watchButton.className = "action-btn watch-now";
            watchButton.innerHTML = "▶️ Assistir Agora";
            actionsContainer.appendChild(watchButton);
        }

        // Botão de Recomendações
        const recommendButton = document.createElement('button');
        recommendButton.className = "action-btn recommend";
        recommendButton.textContent = "🌟 Recomendações";
        recommendButton.addEventListener('click', () => fetchAndRenderRecommendations(movie.id, container.closest('.message-wrapper')));
        actionsContainer.appendChild(recommendButton);

        container.appendChild(cardClone);
    }
    
    function renderRecommendations(container, recommendations) {
        const recsClone = recommendationsTemplate.content.cloneNode(true);
        const grid = recsClone.querySelector('.recommendations-grid');

        recommendations.forEach(movie => {
            const item = document.createElement('div');
            item.className = 'recommendation-item';
            item.innerHTML = `
                <img src="${movie.poster_url || 'https://via.placeholder.com/120x180?text=Sem+Pôster'}" alt="${movie.title}" class="recommendation-poster">
                <div class="recommendation-title">${movie.title} (${movie.year})</div>
            `;
            item.addEventListener('click', () => {
                const recommendationsMessageWrapper = container.closest('.message-wrapper');
                fetchAndRenderMovie(movie.id, recommendationsMessageWrapper);
            });
            grid.appendChild(item);
        });

        container.appendChild(recsClone);
    }

    // --- Funções de Lógica e Eventos ---

    async function handleFormSubmit(event) {
        event.preventDefault();
        const userMessageText = messageInput.value.trim();

        if (!userMessageText && !attachedFile) return;
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
            return;
        }

        renderUserMessage(userMessageText, attachedFile);

        const formData = new FormData();
        formData.append('message', userMessageText);
        if (attachedFile) {
            formData.append('file', attachedFile);
        }

        messageInput.value = "";
        clearAttachment();

        try {
            const response = await fetch("/chat", { method: "POST", body: formData });
            const aiResponse = await response.json();

            if (!response.ok) {
                throw new Error(aiResponse.content || `HTTP error! status: ${response.status}`);
            }

            // Renderiza a resposta da IA
            renderMessage('ai', (messageDiv) => {
                if (aiResponse.type === 'movie' && aiResponse.content) {
                    renderMovieCard(messageDiv, aiResponse.content);
                } else if (aiResponse.type === 'recommendations' && aiResponse.content) {
                    renderRecommendations(messageDiv, aiResponse.content);
                } else if (aiResponse.content) {
                    renderTextMessage(messageDiv, aiResponse.content);
                } else {
                    renderTextMessage(messageDiv, "Desculpe, não consegui processar sua mensagem.");
                }
            });

        } catch (error) {
            console.error("Error sending message:", error);
            renderMessage('ai', (messageDiv) => renderTextMessage(messageDiv, `Desculpe, ocorreu um erro: ${error.message}`));
        }
    }

    async function fetchAndRenderRecommendations(movieId, currentMessageWrapper) {
        try {
            const response = await fetch(`/recommendations/${movieId}`);
            const data = await response.json();
            if (data.type === 'recommendations' && data.content.length > 0) {
                const recWrapper = renderMessage('ai', (messageDiv) => renderRecommendations(messageDiv, data.content));
                currentMessageWrapper.parentNode.insertBefore(recWrapper, currentMessageWrapper.nextSibling);
            }
        } catch (error) {
            console.error("Error fetching recommendations:", error);
        }
    }

    async function fetchAndRenderMovie(movieId, recommendationsWrapper) {
        try {
            const response = await fetch(`/movie/${movieId}`);
            const data = await response.json();
            if (data.type === 'movie') {
                const movieWrapper = renderMessage('ai', (messageDiv) => renderMovieCard(messageDiv, data.content));
                recommendationsWrapper.parentNode.insertBefore(movieWrapper, recommendationsWrapper.nextSibling);
                recommendationsWrapper.remove(); // Remove o card de recomendações após o clique
            }
        } catch (error) {
            console.error("Error fetching movie details:", error);
        }
    }
    
    // ... (As funções handleFileSelection, clearAttachment, handleMicClick, startRecordingUI, etc., continuam as mesmas) ...
    // ... (Elas não precisam de alteração, pois não lidam com a renderização de mensagens) ...
    
    function showAttachmentPreview(file) {
        attachmentPreview.innerHTML = '';
        const fileURL = URL.createObjectURL(file);
        let previewElement;
        if (file.type.startsWith('image/')) {
            previewElement = document.createElement('img');
            previewElement.src = fileURL;
        } else if (file.type.startsWith('video/')) {
            previewElement = document.createElement('video');
            previewElement.src = fileURL;
            previewElement.muted = true;
        } else {
            previewElement = document.createElement('p');
            previewElement.textContent = `Arquivo: ${file.name}`;
        }
        attachmentPreview.appendChild(previewElement);
        attachmentPreviewContainer.style.display = 'block';
    }

    function clearAttachment() {
        attachedFile = null;
        fileInput.value = '';
        attachmentPreviewContainer.style.display = 'none';
    }

    async function handleMicClick() {
        if (!mediaRecorder || mediaRecorder.state === 'inactive') {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
                audioChunks = [];
                mediaRecorder.ondataavailable = event => audioChunks.push(event.data);
                mediaRecorder.onstop = () => {
                    stopRecordingUI();
                    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                    attachedFile = new File([audioBlob], "recording.webm", { type: "audio/webm" });
                    chatForm.requestSubmit();
                    stream.getTracks().forEach(track => track.stop());
                };
                mediaRecorder.start();
                startRecordingUI();
            } catch (err) {
                alert("Não foi possível acessar seu microfone. Por favor, verifique as permissões.");
            }
        } else {
            mediaRecorder.stop();
        }
    }

    function startRecordingUI() {
        secondsRecorded = 0;
        recordingTimer.textContent = formatTime(secondsRecorded);
        recordingTimer.classList.remove('hidden');
        messageInput.placeholder = "Gravando...";
        messageInput.disabled = true;
        micButton.classList.add('is-recording');
        micButton.title = "Parar gravação";
        recordingInterval = setInterval(() => {
            secondsRecorded++;
            recordingTimer.textContent = formatTime(secondsRecorded);
        }, 1000);
    }

    function stopRecordingUI() {
        clearInterval(recordingInterval);
        recordingTimer.classList.add('hidden');
        messageInput.placeholder = originalPlaceholder;
        messageInput.disabled = false;
        micButton.classList.remove('is-recording');
        micButton.title = "Gravar áudio";
    }

    function formatTime(seconds) {
        const m = Math.floor(seconds / 60).toString().padStart(2, '0');
        const s = (seconds % 60).toString().padStart(2, '0');
        return `${m}:${s}`;
    }

    function scrollToBottom() {
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // --- Inicialização ---
    function init() {
        // Verifica se todos os elementos necessários existem
        if (!chatBox || !chatForm || !messageInput) {
            console.error("❌ Elementos essenciais do DOM não encontrados!");
            return;
        }
        
        // Event Listeners
        if (attachmentButton) {
            attachmentButton.addEventListener('click', () => fileInput.click());
        }
        if (fileInput) {
            fileInput.addEventListener('change', (e) => { 
                if(e.target.files.length > 0) { 
                    attachedFile = e.target.files[0]; 
                    showAttachmentPreview(attachedFile); 
                }
            });
        }
        if (removeAttachmentBtn) {
            removeAttachmentBtn.addEventListener('click', clearAttachment);
        }
        if (micButton) {
            micButton.addEventListener('click', handleMicClick);
        }
        chatForm.addEventListener("submit", handleFormSubmit);

        // Mensagem inicial
        renderMessage('ai', (messageDiv) => {
            renderTextMessage(messageDiv, 'Olá! Sou o ChatCine 🍿. Diga o nome de um filme, descreva uma cena ou me envie uma imagem/áudio para eu adivinhar!');
        });
        
        console.log("✅ ChatCine inicializado com sucesso!");
    }

    init();
});