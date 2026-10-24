/**
 * Universal Multilingual Voice Assistant Engine
 * 100% Compatible with ALL Browsers (Firefox, Chrome, Safari, Edge, Brave, Opera)
 * Features:
 * 1. Direct Web Audio MediaRecorder + Gemini Multimodal Speech Transcription.
 * 2. Real-time Audio Level VU Meter (animates sound bars based on actual mic volume).
 * 3. Text-to-Speech with Autoplay Unlock & Mascot Lip-Sync.
 * 4. Graceful Fallback if microphone hardware is unavailable.
 */

class VoiceAssistant {
  constructor() {
    this.currentLanguage = 'gu-IN'; // Default: Gujarati
    this.mediaRecorder = null;
    this.audioChunks = [];
    this.mediaStream = null;
    this.audioContext = null;
    this.analyser = null;
    this.animFrameId = null;
    this.isRecording = false;
    this.synth = window.speechSynthesis || null;
    this.onResultCallback = null;
    this.onStatusChangeCallback = null;
    this.recordingTimeout = null;

    this.languageNames = {
      'gu-IN': 'ગુજરાતી (Gujarati)',
      'hi-IN': 'हिन्दी (Hindi)',
      'en-US': 'English (US)',
      'en-GB': 'English (UK)',
      'es-ES': 'Español (Spanish)',
      'fr-FR': 'Français (French)',
      'de-DE': 'Deutsch (German)',
      'ja-JP': '日本語 (Japanese)',
      'zh-CN': '中文 (Mandarin)',
      'pt-BR': 'Português (Portuguese)',
      'ar-SA': 'العربية (Arabic)'
    };

    // Preload speech synthesis voices
    if (this.synth) {
      this.synth.getVoices();
      if (typeof this.synth.onvoiceschanged !== 'undefined') {
        this.synth.onvoiceschanged = () => {
          if (this.synth) this.synth.getVoices();
        };
      }
    }
  }

  setLanguage(langCode) {
    if (this.languageNames[langCode]) {
      this.currentLanguage = langCode;
      console.log(`🌍 Voice Assistant language switched to: ${this.languageNames[langCode]} (${langCode})`);
      return true;
    }
    return false;
  }

  _checkVoiceLanguageCommand(text) {
    const lower = text.toLowerCase();
    
    // Gujarati check
    if (lower.includes("switch to gujarati") || lower.includes("speak in gujarati") || lower.includes("ગુજરાતીમાં બોલો") || lower.includes("ગુજરાતી")) {
      this.setLanguage('gu-IN');
      const select = document.getElementById('language-select');
      if (select) select.value = 'gu-IN';
      this.speak("નમસ્તે! હવે હું તમારી સાથે ગુજરાતીમાં વાત કરીશ. તમારે કઈ નવી ગેમ બનાવવી છે?", 'gu-IN');
      return true;
    }

    // Hindi check
    if (lower.includes("switch to hindi") || lower.includes("speak in hindi") || lower.includes("hindi me bolo") || lower.includes("हिन्दी")) {
      this.setLanguage('hi-IN');
      const select = document.getElementById('language-select');
      if (select) select.value = 'hi-IN';
      this.speak("नमस्ते! अब मैं हिन्दी में बात करूँगा। आप कैसा गेम बनाना चाहते हैं?", 'hi-IN');
      return true;
    }

    // Spanish check
    if (lower.includes("switch to spanish") || lower.includes("speak spanish") || lower.includes("habla español") || lower.includes("español")) {
      this.setLanguage('es-ES');
      const select = document.getElementById('language-select');
      if (select) select.value = 'es-ES';
      this.speak("¡Hola amigo! ¡Ahora hablaré en español! ¿Qué juego quieres crear?", 'es-ES');
      return true;
    }

    // French check
    if (lower.includes("switch to french") || lower.includes("speak french") || lower.includes("parle français") || lower.includes("français")) {
      this.setLanguage('fr-FR');
      const select = document.getElementById('language-select');
      if (select) select.value = 'fr-FR';
      this.speak("Bonjour ami! Je parle maintenant en français! Quel jeu veux-tu créer?", 'fr-FR');
      return true;
    }

    // German check
    if (lower.includes("switch to german") || lower.includes("speak german") || lower.includes("deutsch")) {
      this.setLanguage('de-DE');
      const select = document.getElementById('language-select');
      if (select) select.value = 'de-DE';
      this.speak("Hallo Freund! Ich spreche jetzt Deutsch! Welches Spiel möchtest du erschaffen?", 'de-DE');
      return true;
    }

    // English check
    if (lower.includes("switch to english") || lower.includes("speak in english") || lower.includes("અંગ્રેજી")) {
      this.setLanguage('en-US');
      const select = document.getElementById('language-select');
      if (select) select.value = 'en-US';
      this.speak("Awesome! Switched back to English! What game shall we build next?", 'en-US');
      return true;
    }

    return false;
  }

  async toggleListening() {
    if (this.isRecording) {
      this.stopRecording();
    } else {
      await this.startRecording();
    }
  }

  async startRecording() {
    // Unlock speech synthesis immediately on user click
    if (this.synth) {
      this.synth.resume();
    }

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      this._handleMicFallback("માઇક્રોફોન સપોર્ટ નથી, પણ તમે બટન પર ક્લિક કરીને ગેમ બનાવી શકો છો!");
      return;
    }

    try {
      this.mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.audioChunks = [];

      let mimeType = 'audio/webm';
      if (typeof MediaRecorder !== 'undefined') {
        if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
          mimeType = 'audio/webm;codecs=opus';
        } else if (MediaRecorder.isTypeSupported('audio/ogg;codecs=opus')) {
          mimeType = 'audio/ogg;codecs=opus';
        } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
          mimeType = 'audio/mp4';
        }
      }

      this.mediaRecorder = new MediaRecorder(this.mediaStream);
      
      this.mediaRecorder.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) {
          this.audioChunks.push(e.data);
        }
      };

      this.mediaRecorder.onstop = async () => {
        this.isRecording = false;
        this._stopAudioMeter();
        if (this.onStatusChangeCallback) this.onStatusChangeCallback('processing');

        if (this.mediaStream) {
          this.mediaStream.getTracks().forEach(t => t.stop());
          this.mediaStream = null;
        }

        const audioBlob = new Blob(this.audioChunks, { type: mimeType });
        await this._transcribeAudioBlob(audioBlob, mimeType);
      };

      this.mediaRecorder.start(250);
      this.isRecording = true;

      // Start live audio visualizer
      this._startAudioMeter(this.mediaStream);

      if (this.onStatusChangeCallback) {
        this.onStatusChangeCallback('listening');
      }

      // Auto-stop after 8 seconds if user forgets to tap again
      if (this.recordingTimeout) clearTimeout(this.recordingTimeout);
      this.recordingTimeout = setTimeout(() => {
        if (this.isRecording) {
          this.stopRecording();
        }
      }, 8000);

    } catch (err) {
      console.warn("Microphone access unavailable or denied:", err);
      this.isRecording = false;
      this._stopAudioMeter();
      if (this.onStatusChangeCallback) this.onStatusChangeCallback('idle');
      this._handleMicFallback("માઇક્રોફોન શરૂ નથી થયું, ચાલો આમાંથી પસંદ કરો કે તમારે કેવી ગેમ બનાવવી છે!");
    }
  }

  _handleMicFallback(message) {
    if (window.appInstance) {
      window.appInstance.updateAssistantSpeech(message);
      this.speak(message);
      window.appInstance.renderInteractiveOptions([
        "🦄 યુનિકોર્ન ડોનટ્સ ગેમ બનાવો",
        "🚀 સ્પેસ રોકેટ ગેમ બનાવો",
        "🏎️ ટર્બો કાર રેસિંગ બનાવો",
        "💡 મને એક નવો મસ્ત આઈડિયા આપો"
      ]);
    }
  }

  _startAudioMeter(stream) {
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!AudioContext) return;
      this.audioContext = new AudioContext();
      const source = this.audioContext.createMediaStreamSource(stream);
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 64;
      source.connect(this.analyser);

      const bufferLength = this.analyser.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);

      const updateMeter = () => {
        if (!this.isRecording) return;
        this.analyser.getByteFrequencyData(dataArray);
        
        let sum = 0;
        for (let i = 0; i < bufferLength; i++) {
          sum += dataArray[i];
        }
        const avg = sum / bufferLength; // 0 to 255
        const scale = Math.max(6, (avg / 255) * 36);

        for (let i = 1; i <= 5; i++) {
          const bar = document.getElementById(`bar-${i}`);
          if (bar) {
            const h = Math.max(6, scale * (0.6 + (i % 3) * 0.3));
            bar.style.height = `${h}px`;
          }
        }

        this.animFrameId = requestAnimationFrame(updateMeter);
      };

      updateMeter();
    } catch (e) {
      console.warn("Audio meter init error:", e);
    }
  }

  _stopAudioMeter() {
    if (this.animFrameId) {
      cancelAnimationFrame(this.animFrameId);
      this.animFrameId = null;
    }
    if (this.audioContext && this.audioContext.state !== 'closed') {
      try {
        this.audioContext.close();
      } catch (e) {}
    }
  }

  stopRecording() {
    if (this.recordingTimeout) clearTimeout(this.recordingTimeout);
    if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
      try {
        this.mediaRecorder.stop();
      } catch (e) {
        console.warn("MediaRecorder stop error:", e);
      }
    }
    this.isRecording = false;
  }

  async _transcribeAudioBlob(audioBlob, mimeType) {
    try {
      const reader = new FileReader();
      reader.readAsDataURL(audioBlob);
      reader.onloadend = async () => {
        const base64Audio = reader.result;

        try {
          const resp = await fetch('/api/voice/transcribe', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              audio_base64: base64Audio,
              mime_type: mimeType,
              language: this.currentLanguage
            })
          });

          if (this.onStatusChangeCallback) this.onStatusChangeCallback('idle');

          if (!resp.ok) {
            throw new Error(`Transcribe HTTP ${resp.status}`);
          }

          const data = await resp.json();
          const transcript = (data.transcript || "").trim();

          if (transcript) {
            console.log("🎙️ Universal Voice Transcribed:", transcript);
            
            if (this._checkVoiceLanguageCommand(transcript)) {
              return;
            }

            if (this.onResultCallback) {
              this.onResultCallback(transcript, this.currentLanguage);
            }
          } else {
            console.warn("Empty transcription received, asking prompt.");
            if (this.onResultCallback) {
              this.onResultCallback("મને એક મસ્ત નવી ગેમનો આઈડિયા આપો!", this.currentLanguage);
            }
          }

        } catch (err) {
          console.error("Voice transcription error:", err);
          if (this.onStatusChangeCallback) this.onStatusChangeCallback('idle');
        }
      };
    } catch (err) {
      console.error("Audio conversion error:", err);
      if (this.onStatusChangeCallback) this.onStatusChangeCallback('idle');
    }
  }

  speak(text, lang = null) {
    if (!this.synth) return;
    
    try {
      this.synth.cancel();
      this.synth.resume();

      const targetLang = lang || this.currentLanguage;
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = targetLang;
      utterance.rate = 1.0;
      utterance.pitch = 1.2;

      const voices = this.synth.getVoices();
      const matchingVoice = voices.find(v => v.lang === targetLang || v.lang.startsWith(targetLang.split('-')[0]));
      if (matchingVoice) {
        utterance.voice = matchingVoice;
      }

      const mouth = document.getElementById('mascot-mouth');
      utterance.onstart = () => {
        if (mouth) mouth.classList.add('talking');
      };

      utterance.onend = () => {
        if (mouth) mouth.classList.remove('talking');
      };

      utterance.onerror = () => {
        if (mouth) mouth.classList.remove('talking');
      };

      this.synth.speak(utterance);
    } catch (e) {
      console.warn("Speech synthesis error:", e);
    }
  }
}

window.VoiceAssistant = VoiceAssistant;
