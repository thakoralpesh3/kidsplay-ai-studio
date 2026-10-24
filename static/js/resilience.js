/**
 * Network Resilience and Process Interruption Auto-Resume Manager (Client-side)
 * Handles automatic recovery from network cuts, browser reloads, server crashes, and power restarts.
 */

class ResilienceManagerClient {
  constructor(app) {
    this.app = app;
    this.isOnline = navigator.onLine;
    this.socket = null;
    this.toast = document.getElementById('resilience-banner');
    this.toastTitle = document.getElementById('toast-title');
    this.toastMessage = document.getElementById('toast-message');
    this.toastIcon = document.getElementById('toast-icon');
    this.toastSpinner = document.getElementById('toast-spinner');
    this.networkBadge = document.getElementById('network-badge');
    this.networkText = document.getElementById('network-status-text');

    this._bindEvents();
    this._initWebSocket();
    this.checkAndRecoverPendingJob();
  }

  _bindEvents() {
    window.addEventListener('online', () => {
      this.isOnline = true;
      this._updateNetworkUI(true);
      this.showToast('🌐 નેટવર્ક શરૂ થયું (Online)!', 'કનેક્શન મળ્યું છે, સેવ થયેલી પ્રક્રિયા આપોઆપ શરૂ થઈ રહી છે...', '⚡', false, 3500);
      this.checkAndRecoverPendingJob();
    });

    window.addEventListener('offline', () => {
      this.isOnline = false;
      this._updateNetworkUI(false);
      this.showToast('🐻 નેટવર્ક બંધ છે (Paused)', 'ઇન્ટરનેટ બંધ થયું છે. તમારી વિનંતી સેવ છે અને નેટ આવતા આપોઆપ ચાલુ થઈ જશે!', '📡', false);
    });
  }

  _updateNetworkUI(online) {
    if (this.networkBadge && this.networkText) {
      if (online) {
        this.networkBadge.className = 'network-badge online';
        this.networkText.textContent = 'ઓનલાઇન (Online)';
      } else {
        this.networkBadge.className = 'network-badge offline';
        this.networkText.textContent = 'ઓફલાઇન (Auto-Resume Ready)';
      }
    }
  }

  _initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;

    try {
      this.socket = new WebSocket(wsUrl);

      this.socket.onopen = () => {
        console.log("⚡ Resilience WebSocket connected to AI Studio backend");
        this.checkAndRecoverPendingJob();
      };

      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this._handleWsMessage(data);
        } catch (e) {
          console.error("Error parsing WS message:", e);
        }
      };

      this.socket.onclose = () => {
        setTimeout(() => this._initWebSocket(), 3000);
      };
    } catch (err) {
      console.warn("WebSocket init error:", err);
    }
  }

  _handleWsMessage(data) {
    if (data.type === 'resilience_status') {
      if (data.status === 'resuming') {
        this.showToast('✨ પ્રક્રિયા આપોઆપ શરૂ થઈ રહી છે!', data.message || 'Auto-resuming in-flight game...', '🪄', true);
      } else if (data.status === 'paused_offline') {
        this.showToast('🐻 વિનંતી સેવ છે!', data.message, '💤', false);
      }
    } else if (data.type === 'job_completed') {
      this.clearSavedJob();
      this.showToast('🎉 ગેમ તૈયાર થઈ ગઈ છે!', 'તમારી વિનંતી સફળતાપૂર્વક પૂર્ણ થઈ ગઈ છે!', '🌟', false, 4000);
      if (this.app && data.result) {
        this.app.applyGameResult(data.result);
      }
    }
  }

  savePendingJob(jobId, prompt, type = 'create') {
    try {
      localStorage.setItem('kidsplay_active_job', JSON.stringify({
        jobId,
        prompt,
        type,
        timestamp: Date.now()
      }));
    } catch (e) {}
  }

  clearSavedJob() {
    try {
      localStorage.removeItem('kidsplay_active_job');
    } catch (e) {}
  }

  async checkAndRecoverPendingJob() {
    try {
      const raw = localStorage.getItem('kidsplay_active_job');
      if (!raw) return;
      const job = JSON.parse(raw);
      if (!job || !job.jobId) return;

      // Only check if within 24 hours
      if (Date.now() - job.timestamp > 24 * 60 * 60 * 1000) {
        this.clearSavedJob();
        return;
      }

      console.log(`🔍 Checking crash recovery for interrupted job: ${job.jobId} ('${job.prompt}')`);
      const resp = await fetch(`/api/job/${job.jobId}`).catch(() => null);
      if (!resp || !resp.ok) return;

      const data = await resp.json();
      if (data.status === 'COMPLETED' && data.result) {
        console.log("✨ Found completed result for interrupted job! Restoring...");
        this.showToast('🎉 ગેમ રીકવર થઈ ગઈ છે!', 'ક્રેશ પછી સેવ થયેલી ગેમ આપોઆપ લોડ થઈ ગઈ!', '🌟', false, 4000);
        this.clearSavedJob();
        if (this.app) {
          this.app.applyGameResult(data.result);
        }
      } else if (data.status === 'PROCESSING' || data.status === 'RECOVERING' || data.status === 'PAUSED_OFFLINE') {
        this.showToast('🔄 પ્રક્રિયા આપોઆપ ચાલુ છે...', `તમારો પ્રોમ્પ્ટ '${job.prompt}' જ્યાંથી અટક્યો હતો ત્યાંથી ચાલુ છે!`, '⏳', true);
      }
    } catch (err) {
      console.warn("Could not check recovery status:", err);
    }
  }

  showToast(title, message, icon = '🐻', showSpinner = false, autoHideMs = 0) {
    if (!this.toast) return;
    this.toastTitle.textContent = title;
    this.toastMessage.textContent = message;
    this.toastIcon.textContent = icon;
    
    if (showSpinner) {
      this.toastSpinner.classList.remove('hidden');
    } else {
      this.toastSpinner.classList.add('hidden');
    }

    this.toast.classList.remove('hidden');

    if (autoHideMs > 0) {
      setTimeout(() => {
        this.toast.classList.add('hidden');
      }, autoHideMs);
    }
  }

  hideToast() {
    if (this.toast) this.toast.classList.add('hidden');
  }
}

window.ResilienceManagerClient = ResilienceManagerClient;
