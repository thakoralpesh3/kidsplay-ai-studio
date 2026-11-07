/**
 * KidsPlay AI Studio - Master App Controller (Default: Gujarati)
 * Interactive Conversational Voice Copilot, Autonomous Self-Evolution & Surprise Idea Engine
 */

class KidsPlayStudioApp {
  constructor() {
    this.engine = new GameEngine('game-canvas');
    this.voice = new VoiceAssistant();
    this.selfHealer = new SelfHealingManager(this.engine);
    this.resilience = new ResilienceManagerClient(this);

    // Global expose
    window.appInstance = this;
    window.appVoice = this.voice;
    window.SelfHealingManager = this.selfHealer;

    this.currentGameData = null;
    this.isGenerating = false;
    this.activeSurprise = null;
    this.conversationHistory = [];
    this.difficulty = 'normal'; // 'easy' | 'normal' | 'superstar'
    this.favorites = this._loadFavorites();

    this._initUI();
    this._bindEvents();
    this._updateFavCount();
    this._loadStarterGame();
    this.refreshMemoryStats();
    this._startProactiveSurpriseTimer();
  }

  _initUI() {
    this.elements = {
      langSelect: document.getElementById('language-select'),
      btnMic: document.getElementById('btn-voice-mic'),
      micLabel: document.getElementById('mic-label'),
      voiceWaveBars: document.getElementById('voice-wave-bars'),
      btnReplaySpeech: document.getElementById('btn-replay-speech'),
      btnSurpriseMe: document.getElementById('btn-surprise-me'),
      btnAskIdea: document.getElementById('btn-ask-idea'),
      btnHowToPlay: document.getElementById('btn-how-to-play'),
      promptInput: document.getElementById('prompt-input'),
      btnSendPrompt: document.getElementById('btn-send-prompt'),
      speechText: document.getElementById('assistant-speech-text'),
      choicesTray: document.getElementById('interactive-choices-tray'),
      gameTitle: document.getElementById('current-game-title'),
      gameIcon: document.getElementById('game-badge-icon'),
      gameInstructions: document.getElementById('game-instructions-text'),
      genOverlay: document.getElementById('generation-overlay'),
      genTitle: document.getElementById('gen-status-title'),
      genDesc: document.getElementById('gen-status-desc'),
      btnRestart: document.getElementById('btn-restart-game'),
      btnDifficulty: document.getElementById('btn-difficulty-toggle'),
      btnSaveFavorite: document.getElementById('btn-save-favorite'),
      btnMyGames: document.getElementById('btn-my-games'),
      btnExportGame: document.getElementById('btn-export-game'),
      favCount: document.getElementById('fav-count'),
      favoritesModal: document.getElementById('favorites-modal'),
      btnCloseFavModal: document.getElementById('btn-close-fav-modal'),
      favListContainer: document.getElementById('favorites-list-container'),
      btnMute: document.getElementById('btn-mute-audio'),
      btnFullscreen: document.getElementById('btn-fullscreen'),
      canvasWrapper: document.getElementById('canvas-wrapper'),
      gameHudOverlay: document.getElementById('game-hud-overlay'),
      surpriseBanner: document.getElementById('surprise-banner'),
      surpriseTitle: document.getElementById('surprise-title'),
      surpriseDesc: document.getElementById('surprise-desc'),
      surpriseBadge: document.getElementById('surprise-badge'),
      btnApplySurprise: document.getElementById('btn-apply-surprise'),
      btnRerollSurprise: document.getElementById('btn-reroll-surprise'),
      btnCloseSurprise: document.getElementById('btn-close-surprise'),
      skillsModal: document.getElementById('skills-modal'),
      btnSkillsMatrix: document.getElementById('btn-skills-matrix'),
      btnCloseModal: document.getElementById('btn-close-modal'),
      skillsBadgeCount: document.getElementById('skills-badge-count'),
      skillsListContainer: document.getElementById('skills-list-container'),
      lessonsListContainer: document.getElementById('lessons-list-container'),
      statGamesCreated: document.getElementById('stat-games-created'),
      statModifications: document.getElementById('stat-modifications'),
      statSelfHealed: document.getElementById('stat-self-healed'),
      statSkillsLearned: document.getElementById('stat-skills-learned'),
      statEvolutionTitle: document.getElementById('stat-evolution-title'),
      btnSelfEvolve: document.getElementById('btn-self-evolve-game'),
      btnMobileAccess: document.getElementById('btn-mobile-access'),
      mobileModal: document.getElementById('mobile-modal'),
      btnCloseMobileModal: document.getElementById('btn-close-mobile-modal'),
      kidsplayQrImg: document.getElementById('kidsplay-qr-img'),
      kidsplayMobileUrlText: document.getElementById('kidsplay-mobile-url-text'),
      btnOpenKidsplayMobile: document.getElementById('btn-open-kidsplay-mobile'),
      chamundaMobileUrlText: document.getElementById('chamunda-mobile-url-text'),
      btnOpenChamundaMobile: document.getElementById('btn-open-chamunda-mobile')
    };
  }

  _bindEvents() {
    // Language dropdown change
    this.elements.langSelect.addEventListener('change', (e) => {
      const newLang = e.target.value;
      this.voice.setLanguage(newLang);
      const greeting = this._getLanguageGreeting(newLang);
      this.updateAssistantSpeech(greeting);
      this.voice.speak(greeting, newLang);
    });

    // Voice recognition status change
    this.voice.onStatusChangeCallback = (status) => {
      if (status === 'listening') {
        this.elements.btnMic.classList.add('listening');
        this.elements.micLabel.textContent = this.voice.currentLanguage === 'gu-IN' 
          ? "🔴 બોલો... (પૂરું થાય એટલે ફરી ટેપ કરો)" 
          : "🔴 Recording... (Tap to finish)";
        this.elements.voiceWaveBars.classList.remove('hidden');
      } else if (status === 'processing') {
        this.elements.btnMic.classList.add('listening');
        this.elements.micLabel.textContent = this.voice.currentLanguage === 'gu-IN'
          ? "⏳ અવાજ સમજી રહ્યો છું..."
          : "⏳ Understanding voice...";
        this.elements.voiceWaveBars.classList.remove('hidden');
      } else {
        this.elements.btnMic.classList.remove('listening');
        this.elements.micLabel.textContent = this.voice.currentLanguage === 'gu-IN' 
          ? "બોલવા માટે ટેપ કરો (Tap to Talk & Ask Ideas)" 
          : "Tap to Talk & Ask Ideas";
        this.elements.voiceWaveBars.classList.add('hidden');
      }
    };

    // Voice recognized result -> automatically handle
    this.voice.onResultCallback = (spokenText, lang) => {
      this.elements.promptInput.value = spokenText;
      const lower = spokenText.toLowerCase();
      if (lower.includes("surprise") || lower.includes("સરપ્રાઇઝ") || lower.includes("કંઈક નવું") || lower.includes("નવો વિચાર")) {
        this.triggerSurpriseIdea();
      } else {
        this.handleUserPrompt(spokenText);
      }
    };

    // Replay Speech button
    if (this.elements.btnReplaySpeech) {
      this.elements.btnReplaySpeech.addEventListener('click', () => {
        const text = this.elements.speechText.innerText.replace(/"/g, '');
        this.voice.speak(text, this.elements.langSelect.value);
      });
    }

    // Surprise Me Button
    if (this.elements.btnSurpriseMe) {
      this.elements.btnSurpriseMe.addEventListener('click', () => {
        this.triggerSurpriseIdea();
      });
    }

    // Apply Surprise
    if (this.elements.btnApplySurprise) {
      this.elements.btnApplySurprise.addEventListener('click', () => {
        if (this.activeSurprise && this.activeSurprise.action_prompt) {
          if (this.elements.surpriseBanner) this.elements.surpriseBanner.classList.add('hidden');
          this.handleUserPrompt(this.activeSurprise.action_prompt, 'modify');
        }
      });
    }

    // Reroll Surprise
    if (this.elements.btnRerollSurprise) {
      this.elements.btnRerollSurprise.addEventListener('click', () => {
        this.triggerSurpriseIdea();
      });
    }

    // Close Surprise
    if (this.elements.btnCloseSurprise) {
      this.elements.btnCloseSurprise.addEventListener('click', () => {
        if (this.elements.surpriseBanner) this.elements.surpriseBanner.classList.add('hidden');
      });
    }

    // Ask Idea shortcut
    if (this.elements.btnAskIdea) {
      this.elements.btnAskIdea.addEventListener('click', () => {
        const ideaQuestion = this.elements.langSelect.value === 'gu-IN'
          ? "નમસ્તે દોસ્ત! આજે તમારે કેવી ગેમ બનાવવી છે? શું આપણે આકાશમાં ઉડતી યુનિકોર્ન બનાવીએ કે સ્પેસ રોકેટ?"
          : "Hello friend! What game shall we build today? A flying unicorn or a space rocket?";
        this.updateAssistantSpeech(ideaQuestion);
        this.voice.speak(ideaQuestion, this.elements.langSelect.value);
        this.renderInteractiveOptions([
          "🦄 યુનિકોર્ન ડોનટ્સ ગેમ",
          "🚀 સ્પેસ રોકેટ ગેમ",
          "🏎️ ટર્બો કાર રેસિંગ",
          "🎁 મને સરપ્રાઇઝ આપો!"
        ]);
      });
    }

    // How to Play shortcut
    if (this.elements.btnHowToPlay) {
      this.elements.btnHowToPlay.addEventListener('click', () => {
        const inst = this.elements.gameInstructions.innerText;
        this.updateAssistantSpeech(inst);
        this.voice.speak(inst, this.elements.langSelect.value);
      });
    }

    // Mic click
    this.elements.btnMic.addEventListener('click', () => {
      this.engine.audio.init();
      this.voice.toggleListening();
    });

    // Prompt submit
    this.elements.btnSendPrompt.addEventListener('click', () => {
      const prompt = this.elements.promptInput.value.trim();
      if (prompt) {
        this.handleUserPrompt(prompt);
      }
    });

    this.elements.promptInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const prompt = this.elements.promptInput.value.trim();
        if (prompt) {
          this.handleUserPrompt(prompt);
        }
      }
    });

    // Interactive Choice Tray delegate
    if (this.elements.choicesTray) {
      this.elements.choicesTray.addEventListener('click', (e) => {
        const chip = e.target.closest('.choice-chip');
        if (chip) {
          const choice = chip.getAttribute('data-choice');
          if (choice.includes("સરપ્રાઇઝ") || choice.includes("Surprise")) {
            this.triggerSurpriseIdea();
          } else {
            this.elements.promptInput.value = choice;
            this.handleUserPrompt(choice);
          }
        }
      });
    }

    // Quick Starter Tags
    document.querySelectorAll('.chip-tag').forEach(btn => {
      btn.addEventListener('click', () => {
        const prompt = btn.getAttribute('data-prompt');
        this.elements.promptInput.value = prompt;
        this.handleUserPrompt(prompt, 'create');
      });
    });

    // Quick Modification Chips
    document.querySelectorAll('.chip-modify').forEach(btn => {
      btn.addEventListener('click', () => {
        const mod = btn.getAttribute('data-mod');
        this.elements.promptInput.value = mod;
        this.handleUserPrompt(mod, 'modify');
      });
    });

    // Autonomous Self-Evolve Button
    if (this.elements.btnSelfEvolve) {
      this.elements.btnSelfEvolve.addEventListener('click', () => {
        this.triggerSurpriseIdea();
      });
    }

    // Game tools
    this.elements.btnRestart.addEventListener('click', () => {
      this.engine.restart();
    });

    if (this.elements.btnDifficulty) {
      this.elements.btnDifficulty.addEventListener('click', () => {
        this.toggleDifficulty();
      });
    }

    if (this.elements.btnSaveFavorite) {
      this.elements.btnSaveFavorite.addEventListener('click', () => {
        this.saveCurrentToFavorites();
      });
    }

    if (this.elements.btnMyGames) {
      this.elements.btnMyGames.addEventListener('click', () => {
        this.openFavoritesModal();
      });
    }

    if (this.elements.btnExportGame) {
      this.elements.btnExportGame.addEventListener('click', () => {
        this.exportCurrentGameAsHtml();
      });
    }

    if (this.elements.btnCloseFavModal) {
      this.elements.btnCloseFavModal.addEventListener('click', () => {
        if (this.elements.favoritesModal) this.elements.favoritesModal.classList.add('hidden');
      });
    }

    if (this.elements.favoritesModal) {
      this.elements.favoritesModal.addEventListener('click', (e) => {
        if (e.target === this.elements.favoritesModal) {
          this.elements.favoritesModal.classList.add('hidden');
        }
      });
    }

    this.elements.btnMute.addEventListener('click', () => {
      this.engine.audio.muted = !this.engine.audio.muted;
      this.elements.btnMute.textContent = this.engine.audio.muted ? '🔇 Muted' : '🔊 Audio';
    });

    this.elements.btnFullscreen.addEventListener('click', () => {
      if (!document.fullscreenElement) {
        this.elements.canvasWrapper.requestFullscreen().catch(err => {
          console.warn("Fullscreen request failed:", err);
        });
      } else {
        document.exitFullscreen();
      }
    });

    // Skills & Memory Modal
    this.elements.btnSkillsMatrix.addEventListener('click', () => {
      this.refreshMemoryStats();
      this.elements.skillsModal.classList.remove('hidden');
    });

    this.elements.btnCloseModal.addEventListener('click', () => {
      this.elements.skillsModal.classList.add('hidden');
    });

    this.elements.skillsModal.addEventListener('click', (e) => {
      if (e.target === this.elements.skillsModal) {
        this.elements.skillsModal.classList.add('hidden');
      }
    });

    // Mobile Access Modal
    if (this.elements.btnMobileAccess) {
      this.elements.btnMobileAccess.addEventListener('click', async () => {
        try {
          const resp = await fetch('/api/mobile/status');
          if (resp.ok) {
            const data = await resp.json();
            if (this.elements.kidsplayMobileUrlText) {
              this.elements.kidsplayMobileUrlText.textContent = data.kidsplay_mobile_url;
            }
            if (this.elements.btnOpenKidsplayMobile) {
              this.elements.btnOpenKidsplayMobile.href = data.kidsplay_mobile_url;
            }
            if (this.elements.chamundaMobileUrlText) {
              this.elements.chamundaMobileUrlText.textContent = data.chamunda_chhaya_url;
            }
            if (this.elements.btnOpenChamundaMobile) {
              this.elements.btnOpenChamundaMobile.href = data.chamunda_chhaya_url;
            }
            if (this.elements.kidsplayQrImg) {
              this.elements.kidsplayQrImg.src = `/kidsplay_mobile_qr.png?t=${Date.now()}`;
              this.elements.kidsplayQrImg.style.display = 'block';
            }
          }
        } catch (e) {
          console.warn("Could not fetch mobile status:", e);
        }
        if (this.elements.mobileModal) {
          this.elements.mobileModal.classList.remove('hidden');
        }
      });
    }

    if (this.elements.btnCloseMobileModal) {
      this.elements.btnCloseMobileModal.addEventListener('click', () => {
        if (this.elements.mobileModal) this.elements.mobileModal.classList.add('hidden');
      });
    }

    if (this.elements.mobileModal) {
      this.elements.mobileModal.addEventListener('click', (e) => {
        if (e.target === this.elements.mobileModal) {
          this.elements.mobileModal.classList.add('hidden');
        }
      });
    }
  }

  async triggerSurpriseIdea() {
    const lang = this.elements.langSelect.value || 'gu-IN';
    const waitingText = lang === 'gu-IN' 
      ? "🎁 સ્પાર્કી જાદુઈ સરપ્રાઇઝ આઈડિયા વિચારી રહ્યો છે..." 
      : "🎁 Sparky is brewing a magical surprise idea...";
    this.updateAssistantSpeech(waitingText);
    
    if (this._isStaticPages() && window.ClientGameSynthesizer) {
      const surprise = window.ClientGameSynthesizer.getFallbackSurpriseIdea(this.currentGameData, lang);
      this._displaySurprise(surprise, lang);
      return;
    }

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2000);
      const resp = await fetch('/api/evolution/surprise', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: controller.signal,
        body: JSON.stringify({
          current_game: this.currentGameData,
          language: lang
        })
      });
      clearTimeout(timeoutId);

      if (resp.ok) {
        const data = await resp.json();
        const surprise = data.surprise;
        if (surprise) {
          this._displaySurprise(surprise, lang);
          return;
        }
      }
    } catch (err) {
      console.warn("Surprise request timed out or unavailable, using client synthesizer:", err);
    }

    if (window.ClientGameSynthesizer) {
      const surprise = window.ClientGameSynthesizer.getFallbackSurpriseIdea(this.currentGameData, lang);
      this._displaySurprise(surprise, lang);
    }
  }

  _displaySurprise(surprise, lang) {
    if (!surprise) return;
    this.activeSurprise = surprise;
    if (this.elements.surpriseTitle) {
      this.elements.surpriseTitle.textContent = surprise.surprise_title || "સ્પાર્કીનો સરપ્રાઇઝ આઈડિયા! ✨";
    }
    if (this.elements.surpriseDesc) {
      this.elements.surpriseDesc.textContent = surprise.description || surprise.spoken_announcement;
    }
    if (this.elements.surpriseBadge && surprise.badge) {
      this.elements.surpriseBadge.textContent = surprise.badge;
    }
    if (this.elements.surpriseBanner) {
      this.elements.surpriseBanner.classList.remove('hidden');
    }

    const spoken = surprise.spoken_announcement || surprise.description;
    this.updateAssistantSpeech(spoken);
    this.voice.speak(spoken, lang);
    if (this.engine && this.engine.audio) {
      this.engine.audio.playSound('powerup');
    }
  }

  _startProactiveSurpriseTimer() {
    // Every 90 seconds of active play, Sparky proactively suggests a surprise evolution idea!
    setInterval(() => {
      if (!this.isGenerating && this.engine.running && Math.random() > 0.4) {
        console.log("💡 Sparky Proactive Eureka Surprise triggered!");
        this.triggerSurpriseIdea();
      }
    }, 90000);
  }

  _loadStarterGame() {
    this.currentGameData = {
      title: "જાદુઈ યુનિકોર્ન એડવેન્ચર",
      genre: "platformer",
      game_code: window.DEFAULT_STARTER_GAME_CODE,
      theme: {
        player_emoji: "🦄",
        css_class: "theme-forest"
      },
      instructions: "ખસવા માટે એરો કી (◀ ▶) વાપરો, કૂદવા માટે સ્પેસબાર દબાવો! ડોનટ્સ અને તારા પકડો!"
    };
    if (this.elements.canvasWrapper) {
      this.elements.canvasWrapper.classList.add('theme-forest');
    }
    this.engine.loadGameFromCode(window.DEFAULT_STARTER_GAME_CODE, this.currentGameData);
  }

  _getLanguageGreeting(lang) {
    const greetings = {
      'gu-IN': "નમસ્તે દોસ્ત! હું સ્પાર્કી છું! આજે તમારે કેવી ગેમ બનાવવી છે? શું આપણે યુનિકોર્ન વાળી રમત બનાવીએ, સ્પેસ રોકેટ વાળી કે કાર રેસિંગ?",
      'hi-IN': "नमस्ते दोस्त! मैं स्पार्की हूँ! आज आप कैसा गेम बनाना चाहते हैं? यूनिकॉर्न, स्पेस रॉकेट या कार रेसिंग?",
      'en-US': "Hi friend! I'm Sparky! What game shall we build today? A flying unicorn, a space rocket, or cartoon racing?",
      'en-GB': "Hello there! Ready to create a fun game? What theme would you like?",
      'es-ES': "¡Hola amigo! ¡Soy Sparky! ¿Qué juego creamos hoy? ¿Unicornios, cohetes o carreras?",
      'fr-FR': "Salut mon ami! Je suis Sparky! Quel jeu veux-tu créer aujourd'hui?",
      'de-DE': "Hallo mein Freund! Lass uns ein tolles neues Spiel programmieren! Was möchtest du bauen?",
      'ja-JP': "こんにちは！スパーキーだよ！ユニコーン、宇宙、レース、どんなゲームをつくろうか？",
      'zh-CN': "你好朋友！我是 Sparky！今天想创造什么游戏？独角兽、火箭还是赛车？",
      'pt-BR': "Olá amigo! Eu sou o Sparky! Que jogo incrível vamos criar agora?",
      'ar-SA': "مرحباً يا صديقي! أنا سباركي، ما نوع اللعبة التي تحب أن نصنعها اليوم؟"
    };
    return greetings[lang] || greetings['gu-IN'];
  }

  updateAssistantSpeech(text) {
    this.elements.speechText.innerHTML = `"${text}"`;
  }

  renderInteractiveOptions(options) {
    if (!this.elements.choicesTray || !options || !options.length) return;
    this.elements.choicesTray.innerHTML = options.map(opt => `
      <button class="choice-chip" data-choice="${opt}">${opt}</button>
    `).join('');
  }

  async handleUserPrompt(prompt, forceType = null) {
    if (this.isGenerating) return;
    const lang = this.elements.langSelect.value || 'gu-IN';

    this.conversationHistory.push({ role: 'user', content: prompt });

    // Static GitHub Pages or Direct Offline Mode
    if (this._isStaticPages()) {
      if (!forceType && this._isInteractiveChat(prompt)) {
        const reply = lang === 'gu-IN' 
          ? "નમસ્તે દોસ્ત! હું સ્પાર્કી છું! ચાલો એક મસ્ત ગેમ બનાવીએ!" 
          : "Hi friend! I'm Sparky! Let's build an awesome game!";
        const q = lang === 'gu-IN' ? "તમારે કઈ રમત બનાવવી છે?" : "What kind of game would you like?";
        const opts = lang === 'gu-IN' 
          ? ["🦄 યુનિકોર્ન ગેમ", "🚀 સ્પેસ રોકેટ", "🏎️ કાર રેસિંગ"]
          : ["🦄 Unicorn Adventure", "🚀 Space Rocket Titan", "🏎️ Turbo Highway Racer"];
        this.updateAssistantSpeech(`${reply} ${q}`);
        this.voice.speak(`${reply} ${q}`, lang);
        this.renderInteractiveOptions(opts);
        return;
      }

      this.isGenerating = true;
      const isModify = forceType === 'modify' || (this.currentGameData && this._isModificationIntent(prompt));
      const overlayTitle = lang === 'gu-IN' 
        ? (isModify ? "✨ સ્પાર્કી તમારી ગેમમાં ફેરફાર કરી રહ્યો છે..." : "🪄 સ્પાર્કી નવી જાદુઈ ગેમ બનાવી રહ્યો છે...")
        : (isModify ? "✨ Sparky is Modifying Your Game..." : "🪄 Sparky is Weaving Game Magic...");
      const overlayDesc = lang === 'gu-IN'
        ? `"${prompt}" લાગુ થઈ રહ્યું છે!`
        : `Applying "${prompt}"!`;
      this.showGenerationOverlay(overlayTitle, overlayDesc);

      setTimeout(() => {
        if (window.ClientGameSynthesizer) {
          const clientResult = window.ClientGameSynthesizer.synthesizeGame(prompt, lang);
          this.applyGameResult(clientResult);
        }
        this.isGenerating = false;
      }, 400);
      return;
    }

    // 1. Check if conversational copilot mode
    if (!forceType && this._isInteractiveChat(prompt)) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 2000);
        const chatResp = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          signal: controller.signal,
          body: JSON.stringify({
            message: prompt,
            language: lang,
            conversation_history: this.conversationHistory,
            current_game: this.currentGameData
          })
        });
        clearTimeout(timeoutId);

        if (chatResp.ok) {
          const chatData = await chatResp.json();
          if (chatData.action === 'CONVERSE') {
            const speech = `${chatData.spoken_response || ''} ${chatData.question_for_kid || ''}`.trim();
            this.updateAssistantSpeech(speech);
            this.voice.speak(speech, lang);
            if (chatData.suggested_options) {
              this.renderInteractiveOptions(chatData.suggested_options);
            }
            return;
          }
        }
      } catch (e) {
        console.warn("Copilot chat failed, falling back to game generator:", e);
      }
    }

    // 2. Otherwise proceed to create or modify game
    this.isGenerating = true;
    const isModify = forceType === 'modify' || (this.currentGameData && this._isModificationIntent(prompt));
    const endpoint = isModify ? '/api/game/modify' : '/api/game/create';

    const overlayTitle = lang === 'gu-IN' 
      ? (isModify ? "✨ સ્પાર્કી તમારી ગેમમાં ફેરફાર કરી રહ્યો છે..." : "🪄 સ્પાર્કી નવી જાદુઈ ગેમ બનાવી રહ્યો છે...")
      : (isModify ? "✨ Sparky is Modifying Your Game..." : "🪄 Sparky is Weaving Game Magic...");

    const overlayDesc = lang === 'gu-IN'
      ? `Gemini AI સાથે "${prompt}" લાગુ થઈ રહ્યું છે!`
      : `Applying "${prompt}" with Gemini AI!`;

    this.showGenerationOverlay(overlayTitle, overlayDesc);

    try {
      const payload = isModify
        ? { prompt, current_game: this.currentGameData, language: lang }
        : { prompt, language: lang };

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2500);

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: controller.signal,
        body: JSON.stringify(payload)
      });
      clearTimeout(timeoutId);

      const data = await response.json();

      if (data && data.job_id) {
        this.resilience.savePendingJob(data.job_id, prompt, isModify ? 'modify' : 'create');
      }

      if (response.status === 202 && data.status === 'PAUSED_OFFLINE') {
        this.hideGenerationOverlay();
        this.resilience.showToast('🐻 વિનંતી સેવ થઈ ગઈ છે (Offline)', data.message, '💤');
        this.updateAssistantSpeech(lang === 'gu-IN' 
          ? "અત્યારે નેટવર્ક બંધ છે, પણ ચિંતા ન કરો! નેટ આવતાની સાથે જ હું ગેમ આપોઆપ તૈયાર કરી દઈશ!"
          : "No internet right now, but I will build your game automatically the instant we reconnect!");
        return;
      }

      if (!response.ok) {
        throw new Error(data.detail || `Server error: ${response.statusText}`);
      }

      if (data.result) {
        this.resilience.clearSavedJob();
        this.applyGameResult(data.result);
      }

    } catch (err) {
      console.warn("Backend fetch failed/timed out. Falling back to Client-Side Synthesizer:", err);
      if (window.ClientGameSynthesizer) {
        const clientResult = window.ClientGameSynthesizer.synthesizeGame(prompt, lang);
        if (clientResult) {
          this.resilience.clearSavedJob();
          this.applyGameResult(clientResult);
          return;
        }
      }
      this.hideGenerationOverlay();
      const errMsg = lang === 'gu-IN' ? "અરેરે! કંઈક ભૂલ થઈ, ચાલો ફરીથી બીજો આઈડિયા ટ્રાય કરીએ!" : "Oops! Let's try again with another prompt!";
      this.updateAssistantSpeech(errMsg);
      this.voice.speak(errMsg, lang);
    } finally {
      this.isGenerating = false;
    }
  }

  _isInteractiveChat(prompt) {
    const chatKeywords = [
      "hello", "hi", "hey", "who are you", "what is your name", "joke", "help", "idea",
      "કેમ છો", "નમસ્તે", "હેલો", "તારું નામ", "કોણ છો", "જોક", "મજાક", "વાર્તા", "મદદ", "કેવી રીતે", "આઈડિયા", "વિચાર"
    ];
    const p = prompt.toLowerCase().trim();
    const hasChat = chatKeywords.some(k => p.includes(k));
    const hasCreate = p.includes("બનાવો") || p.includes("create") || p.includes("make") || p.includes("રમત");
    return hasChat && !hasCreate;
  }

  _isModificationIntent(prompt) {
    const modKeywords = ["make", "add", "change", "turn", "speed", "faster", "slower", "jump higher", "more", "easier", "harder", "give", "color", "background", "shield", "dragon", "laser", "બનાવો", "ઉમેરો", "બદલો", "કૂદકો", "ઝડપી", "ધીમું", "સરળ", "રંગ", "સરપ્રાઇઝ"];
    const p = prompt.toLowerCase();
    return modKeywords.some(k => p.includes(k));
  }

  applyGameResult(gameResult) {
    this.hideGenerationOverlay();
    this.currentGameData = gameResult;

    if (gameResult.title) {
      this.elements.gameTitle.textContent = gameResult.title;
    }
    if (gameResult.theme && gameResult.theme.player_emoji) {
      this.elements.gameIcon.textContent = gameResult.theme.player_emoji;
    }
    if (gameResult.instructions) {
      this.elements.gameInstructions.textContent = gameResult.instructions;
    }

    // Apply dynamic CSS theme classes & variables to canvasWrapper
    if (this.elements.canvasWrapper) {
      const themeClasses = ['theme-space', 'theme-candy', 'theme-racer', 'theme-arcade', 'theme-bubble', 'theme-forest'];
      themeClasses.forEach(c => this.elements.canvasWrapper.classList.remove(c));
      if (gameResult.theme && gameResult.theme.css_class) {
        this.elements.canvasWrapper.classList.add(gameResult.theme.css_class);
      }
      if (gameResult.theme && gameResult.theme.accent_color) {
        this.elements.canvasWrapper.style.setProperty('--game-accent', gameResult.theme.accent_color);
      }
    }

    // Update dynamic HTML HUD Overlay
    if (this.elements.gameHudOverlay && gameResult.theme && gameResult.theme.hud_html) {
      this.elements.gameHudOverlay.innerHTML = gameResult.theme.hud_html;
    }
    if (this.engine.updateHUD) {
      this.engine.updateHUD({ score: 0, lives: 3, combo: 'x1' });
    }

    const spoken = gameResult.spoken_response || (this.elements.langSelect.value === 'gu-IN' ? "આ રહી તમારી નવી ગેમ! રમવાની ખૂબ મજા માણો!" : "Here is your game! Have super fun playing!");
    this.updateAssistantSpeech(spoken);
    this.voice.speak(spoken, this.elements.langSelect.value);

    // Genre-specific interactive tweak chips
    const genre = gameResult.genre || 'platformer';
    const genreChips = {
      'space_shooter': ["🚀 ટર્બો લેઝર ગન", "👾 એલિયન બોસ લાવો", "🛡️ સ્પેસ શીલ્ડ", "🎁 મને સરપ્રાઇઝ આપો!"],
      'cartoon_racer': ["⚡ સુપર નાઇટ્રો સ્પીડ", "🚚 મોન્સ્ટર ટ્રક બનાવો", "🪙 સોનાના સિક્કાનો વરસાદ", "🎁 મને સરપ્રાઇઝ આપો!"],
      'candy_catcher': ["🧁 મેગા કેક સ્ટોર્મ", "🧲 સુપર મેગ્નેટ આપો", "🌈 રેઇન્બો કેન્ડી", "🎁 મને સરપ્રાઇઝ આપો!"],
      'maze_adventure': ["🔦 જાદુઈ ટોર્ચ આપો", "🗝️ સોનેરી ચાવી લાવો", "⚡ સુપર સ્પીડ દોડો", "🎁 મને સરપ્રાઇઝ આપો!"],
      'bubble_pop': ["🌊 મેગા શોકવેવ", "🔮 જાદુઈ ક્રિસ્ટલ બોલ", "✨ સ્પાર્કલિંગ વિસ્ફોટ", "🎁 મને સરપ્રાઇઝ આપો!"],
      'platformer': ["🦘 સુપર હાઇ જમ્પ", "🌈 મેઘધનુષની પૂંછડી", "🛡️ જાદુઈ શિલ્ડ", "🎁 મને સરપ્રાઇઝ આપો!"]
    };
    this.renderInteractiveOptions(genreChips[genre] || genreChips['platformer']);

    if (gameResult.game_code) {
      this.engine.loadGameFromCode(gameResult.game_code, gameResult);
    }

    this.refreshMemoryStats();
  }

  showGenerationOverlay(title, desc) {
    this.elements.genTitle.textContent = title;
    this.elements.genDesc.textContent = desc;
    this.elements.genOverlay.classList.remove('hidden');
  }

  _isStaticPages() {
    return window.location.protocol === 'file:' || 
           window.location.hostname.endsWith('github.io') || 
           window.location.hostname.endsWith('pages.dev') ||
           (window.location.hostname === 'localhost' && window.location.port !== '8899');
  }

  toggleDifficulty() {
    const modes = ['normal', 'superstar', 'easy'];
    const next = modes[(modes.indexOf(this.difficulty) + 1) % modes.length];
    this.difficulty = next;
    const labels = {
      'easy': '🧸 Easy',
      'normal': '⭐ Normal',
      'superstar': '⚡ Super Star'
    };
    if (this.elements.btnDifficulty) {
      this.elements.btnDifficulty.textContent = labels[next];
    }
    if (this.engine) {
      this.engine.difficulty = next;
      if (next === 'easy') {
        this.engine.lives = 5;
      } else if (next === 'superstar') {
        this.engine.lives = 2;
      } else {
        this.engine.lives = 3;
      }
      if (this.engine.hudLives) this.engine.hudLives.textContent = this.engine.lives;
    }
    const msg = this.elements.langSelect.value === 'gu-IN'
      ? `મુશ્કેલી સ્તર બદલાયું: ${labels[next]}`
      : `Difficulty set to: ${labels[next]}`;
    this.updateAssistantSpeech(msg);
  }

  _loadFavorites() {
    try {
      return JSON.parse(localStorage.getItem('kidsplay_favorites') || '[]');
    } catch (e) {
      return [];
    }
  }

  saveCurrentToFavorites() {
    if (!this.currentGameData) return;
    const item = {
      id: 'fav_' + Date.now(),
      title: this.currentGameData.title || 'Kids Game',
      genre: this.currentGameData.genre || 'arcade',
      icon: (this.currentGameData.theme && this.currentGameData.theme.player_emoji) || '🎮',
      savedAt: new Date().toLocaleDateString(),
      gameData: this.currentGameData
    };
    this.favorites.unshift(item);
    if (this.favorites.length > 20) this.favorites.pop();
    try {
      localStorage.setItem('kidsplay_favorites', JSON.stringify(this.favorites));
    } catch (e) {}
    this._updateFavCount();
    const msg = this.elements.langSelect.value === 'gu-IN'
      ? `❤️ "${item.title}" તમારી મનપસંદ યાદીમાં સાચવી લીધી છે!`
      : `❤️ "${item.title}" saved to your favorites!`;
    this.updateAssistantSpeech(msg);
    if (this.engine && this.engine.audio) this.engine.audio.playSound('win');
  }

  _updateFavCount() {
    if (this.elements.favCount) {
      this.elements.favCount.textContent = this.favorites.length;
    }
  }

  openFavoritesModal() {
    if (!this.elements.favoritesModal || !this.elements.favListContainer) return;
    if (!this.favorites.length) {
      this.elements.favListContainer.innerHTML = `
        <div style="text-align:center;padding:24px;color:#a0a6d0;">
          <span style="font-size:36px;display:block;margin-bottom:8px;">🎈</span>
          <p>હજી સુધી કોઈ રમત સાચવેલી નથી. નવી ગેમ બનાવીને "❤️ સાચવો" બટન દબાવો!</p>
        </div>`;
    } else {
      this.elements.favListContainer.innerHTML = this.favorites.map((fav, idx) => `
        <div class="fav-card" style="display:flex;align-items:center;justify-content:space-between;background:rgba(255,255,255,0.06);padding:10px 14px;border-radius:12px;border:1px solid rgba(255,255,255,0.1);">
          <div style="display:flex;align-items:center;gap:10px;">
            <span style="font-size:24px;">${fav.icon}</span>
            <div>
              <h4 style="margin:0;font-size:15px;color:#fff;">${fav.title}</h4>
              <span style="font-size:11px;color:#8890ba;">${fav.genre.toUpperCase()} • ${fav.savedAt}</span>
            </div>
          </div>
          <div style="display:flex;gap:6px;">
            <button class="choice-chip btn-load-fav" data-idx="${idx}" style="padding:6px 12px;font-size:12px;">🎮 રમો</button>
            <button class="choice-chip btn-export-fav" data-idx="${idx}" style="padding:6px 10px;font-size:12px;">💾</button>
            <button class="btn-game-tool btn-del-fav" data-idx="${idx}" style="padding:6px 10px;font-size:12px;color:#ff5577;">🗑️</button>
          </div>
        </div>
      `).join('');

      this.elements.favListContainer.querySelectorAll('.btn-load-fav').forEach(btn => {
        btn.addEventListener('click', () => {
          const idx = parseInt(btn.getAttribute('data-idx'), 10);
          const fav = this.favorites[idx];
          if (fav && fav.gameData) {
            this.applyGameResult(fav.gameData);
            this.elements.favoritesModal.classList.add('hidden');
          }
        });
      });

      this.elements.favListContainer.querySelectorAll('.btn-export-fav').forEach(btn => {
        btn.addEventListener('click', () => {
          const idx = parseInt(btn.getAttribute('data-idx'), 10);
          const fav = this.favorites[idx];
          if (fav && fav.gameData) {
            this.exportCurrentGameAsHtml(fav.gameData);
          }
        });
      });

      this.elements.favListContainer.querySelectorAll('.btn-del-fav').forEach(btn => {
        btn.addEventListener('click', () => {
          const idx = parseInt(btn.getAttribute('data-idx'), 10);
          this.favorites.splice(idx, 1);
          localStorage.setItem('kidsplay_favorites', JSON.stringify(this.favorites));
          this._updateFavCount();
          this.openFavoritesModal();
        });
      });
    }
    this.elements.favoritesModal.classList.remove('hidden');
  }

  exportCurrentGameAsHtml(data = null) {
    const game = data || this.currentGameData;
    if (!game) return;
    const title = game.title || 'KidsPlay Game';
    const code = game.game_code || '';
    const icon = (game.theme && game.theme.player_emoji) || '🎮';
    const instructions = game.instructions || 'ખસવા માટે એરો કી અથવા ઓનસ્ક્રીન બટન વાપરો!';

    const htmlContent = `<!DOCTYPE html>
<html lang="gu">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
  <title>${title} - KidsPlay Offline Game</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: #0f1026; color: #fff; font-family: system-ui, sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; overflow: hidden; touch-action: manipulation; }
    header { padding: 10px; display: flex; align-items: center; justify-content: space-between; width: 100%; max-width: 800px; }
    h1 { font-size: 18px; font-weight: bold; }
    #stage { position: relative; width: 100%; max-width: 800px; aspect-ratio: 16/10; background: #161836; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    canvas { width: 100%; height: 100%; display: block; }
    #hud { position: absolute; top: 10px; left: 10px; right: 10px; display: flex; gap: 10px; pointer-events: none; }
    .chip { background: rgba(0,0,0,0.6); padding: 6px 12px; border-radius: 20px; font-weight: bold; font-size: 14px; }
    #instructions { padding: 8px 12px; font-size: 12px; color: #a0a6d0; text-align: center; max-width: 800px; }
    #touch-bar { display: flex; justify-content: space-between; width: 100%; max-width: 800px; padding: 10px; }
    .touch-btn { background: #ff007a; border: none; color: #fff; padding: 12px 20px; font-size: 16px; font-weight: bold; border-radius: 12px; cursor: pointer; user-select: none; }
  </style>
</head>
<body>
  <header>
    <h1>${icon} ${title}</h1>
    <button class="touch-btn" onclick="location.reload()" style="background:#20244e;padding:6px 12px;font-size:12px;">🔄 ફરી શરૂ કરો</button>
  </header>
  <div id="stage">
    <div id="hud">
      <div class="chip">💖 <span id="lives">3</span></div>
      <div class="chip">⭐ <span id="score">0</span></div>
      <div class="chip">⚡ <span id="combo">x1</span></div>
    </div>
    <canvas id="c" width="800" height="500"></canvas>
  </div>
  <div id="instructions">💡 ${instructions}</div>
  <div id="touch-bar">
    <div style="display:flex;gap:8px;">
      <button class="touch-btn" id="btn-left">◀</button>
      <button class="touch-btn" id="btn-up">▲</button>
      <button class="touch-btn" id="btn-down">▼</button>
      <button class="touch-btn" id="btn-right">▶</button>
    </div>
    <div style="display:flex;gap:8px;">
      <button class="touch-btn" id="btn-jump" style="background:#00f0ff;color:#000;">કૂદો 🦘</button>
      <button class="touch-btn" id="btn-action" style="background:#ffe600;color:#000;">જાદુ ✨</button>
    </div>
  </div>
  <script>
    const canvas = document.getElementById('c');
    const ctx = canvas.getContext('2d');
    const hudLives = document.getElementById('lives');
    const hudScore = document.getElementById('score');
    const hudCombo = document.getElementById('combo');
    
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    function playBeep(freq, type, duration) {
      try {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = type; osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
        gain.gain.setValueAtTime(0.15, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + duration);
        osc.connect(gain); gain.connect(audioCtx.destination);
        osc.start(); osc.stop(audioCtx.currentTime + duration);
      } catch(e) {}
    }
    const audio = {
      playSound(name) {
        if (name === 'jump') playBeep(320, 'sine', 0.15);
        else if (name === 'coin') playBeep(880, 'triangle', 0.2);
        else if (name === 'powerup') playBeep(580, 'triangle', 0.35);
        else if (name === 'laser') playBeep(900, 'sawtooth', 0.1);
        else if (name === 'hit') playBeep(120, 'square', 0.25);
        else if (name === 'win') playBeep(523, 'triangle', 0.4);
      }
    };

    const engine = {
      width: 800, height: 500, score: 0, lives: 3, combo: 1, running: true, audio,
      keys: { left: false, right: false, up: false, down: false, space: false, action: false },
      pointer: { x: 400, y: 250, isDown: false },
      particles: [],
      updateHUD(data) {
        if (data.score !== undefined) hudScore.textContent = data.score;
        if (data.lives !== undefined) hudLives.textContent = data.lives;
        if (data.combo !== undefined) hudCombo.textContent = 'x' + data.combo;
      },
      triggerScreenShake() {},
      spawnParticles(x, y, colors, count) {
        for (let i = 0; i < (count || 8); i++) {
          engine.particles.push({
            x, y,
            vx: (Math.random() - 0.5) * 6,
            vy: (Math.random() - 0.5) * 6,
            color: colors[Math.floor(Math.random() * colors.length)] || '#fff',
            alpha: 1.0,
            life: 30
          });
        }
      },
      spawnScorePopup() {}
    };

    window.addEventListener('keydown', e => {
      if (e.key === 'ArrowLeft' || e.key === 'a') engine.keys.left = true;
      if (e.key === 'ArrowRight' || e.key === 'd') engine.keys.right = true;
      if (e.key === 'ArrowUp' || e.key === 'w') engine.keys.up = true;
      if (e.key === 'ArrowDown' || e.key === 's') engine.keys.down = true;
      if (e.key === ' ' || e.key === 'Spacebar') { engine.keys.space = true; engine.keys.action = true; }
    });
    window.addEventListener('keyup', e => {
      if (e.key === 'ArrowLeft' || e.key === 'a') engine.keys.left = false;
      if (e.key === 'ArrowRight' || e.key === 'd') engine.keys.right = false;
      if (e.key === 'ArrowUp' || e.key === 'w') engine.keys.up = false;
      if (e.key === 'ArrowDown' || e.key === 's') engine.keys.down = false;
      if (e.key === ' ' || e.key === 'Spacebar') { engine.keys.space = false; engine.keys.action = false; }
    });

    function bindTouch(id, key) {
      const el = document.getElementById(id);
      if (!el) return;
      el.addEventListener('touchstart', e => { e.preventDefault(); engine.keys[key] = true; });
      el.addEventListener('touchend', e => { e.preventDefault(); engine.keys[key] = false; });
      el.addEventListener('mousedown', () => { engine.keys[key] = true; });
      el.addEventListener('mouseup', () => { engine.keys[key] = false; });
    }
    bindTouch('btn-left', 'left');
    bindTouch('btn-right', 'right');
    bindTouch('btn-up', 'up');
    bindTouch('btn-down', 'down');
    bindTouch('btn-jump', 'space');
    bindTouch('btn-action', 'action');

    // Inject Game Code
    ${code}

    const gameInstance = window.createGameInstance();
    if (gameInstance && gameInstance.init) gameInstance.init(engine);

    let lastTime = performance.now();
    function loop(now) {
      const dt = Math.min((now - lastTime) / 1000, 0.1);
      lastTime = now;
      ctx.clearRect(0, 0, 800, 500);
      if (gameInstance && gameInstance.update) gameInstance.update(engine, dt);
      if (gameInstance && gameInstance.draw) gameInstance.draw(engine, ctx);

      for (let i = engine.particles.length - 1; i >= 0; i--) {
        const p = engine.particles[i];
        p.x += p.vx; p.y += p.vy; p.life--; p.alpha = Math.max(0, p.life / 30);
        ctx.save(); ctx.globalAlpha = p.alpha; ctx.fillStyle = p.color;
        ctx.beginPath(); ctx.arc(p.x, p.y, 4, 0, Math.PI * 2); ctx.fill();
        ctx.restore();
        if (p.life <= 0) engine.particles.splice(i, 1);
      }
      requestAnimationFrame(loop);
    }
    requestAnimationFrame(loop);
  </script>
</body>
</html>`;

    const blob = new Blob([htmlContent], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const cleanName = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '') || 'kidsplay-game';
    a.download = `${cleanName}.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    const msg = this.elements.langSelect.value === 'gu-IN'
      ? `💾 "${title}" રમત સફળતાપૂર્વક ડાઉનલોડ થઈ ગઈ છે! કોઈપણ ઉપકરણમાં ઑફલાઇન રમો!`
      : `💾 "${title}" exported! Play offline anywhere!`;
    this.updateAssistantSpeech(msg);
  }

  hideGenerationOverlay() {
    this.elements.genOverlay.classList.add('hidden');
  }

  async refreshMemoryStats() {
    try {
      const [resHealth, resSkills, resMem] = await Promise.all([
        fetch('/api/health').then(r => r.json()).catch(() => null),
        fetch('/api/skills').then(r => r.json()).catch(() => null),
        fetch('/api/memory').then(r => r.json()).catch(() => null)
      ]);

      if (resHealth && resHealth.model) {
        const badge = document.getElementById('badge-gemini-model');
        if (badge) {
          badge.textContent = resHealth.model.includes('argon') 
            ? '⚡ Powered by Gemini 4 Argon' 
            : `⚡ Powered by ${resHealth.model}`;
        }
      }

      if (resSkills && resSkills.skills) {
        const skills = resSkills.skills;
        const count = Object.keys(skills).length;
        this.elements.skillsBadgeCount.textContent = count;
        this.elements.statSkillsLearned.textContent = count;

        this.elements.skillsListContainer.innerHTML = Object.values(skills).map(s => `
          <div class="skill-item">
            <h4>✨ ${s.name}</h4>
            <p>${s.description}</p>
          </div>
        `).join('');
      }

      if (resMem && resMem.memory) {
        const mem = resMem.memory;
        this.elements.statGamesCreated.textContent = mem.total_games_created || 0;
        this.elements.statModifications.textContent = mem.total_modifications || 0;
        this.elements.statSelfHealed.textContent = mem.bugs_self_healed || 0;

        if (mem.evolution_title && this.elements.statEvolutionTitle) {
          this.elements.statEvolutionTitle.textContent = mem.evolution_title;
        }

        if (mem.lessons_learned) {
          this.elements.lessonsListContainer.innerHTML = mem.lessons_learned.map(l => `
            <li>${l}</li>
          `).join('');
        }
      }
    } catch (err) {
      console.warn("Could not refresh memory stats:", err);
    }
  }
}

// Initialize on DOM load
window.addEventListener('DOMContentLoaded', () => {
  new KidsPlayStudioApp();
});
