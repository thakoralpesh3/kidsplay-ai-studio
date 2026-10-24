/**
 * Client-Side Self-Healing Diagnostic Boundary
 * Detects runtime game glitches, calls Gemini repair backend, and hotfixes the game dynamically.
 */

class SelfHealingManager {
  constructor(engine) {
    this.engine = engine;
    this.isRepairing = false;
    this.errorDebounceTimer = null;
    this.toastEl = document.getElementById('healing-toast');
  }

  handleRuntimeError(errorMessage, brokenCode, errorStack = "") {
    if (this.isRepairing) return; // Prevent cascade loops

    console.warn("🛡️ Self-Healing Boundary trapped error:", errorMessage);

    if (this.errorDebounceTimer) clearTimeout(this.errorDebounceTimer);
    this.errorDebounceTimer = setTimeout(() => {
      this.triggerAutoRepair(errorMessage, brokenCode, errorStack);
    }, 300);
  }

  async triggerAutoRepair(errorMessage, brokenCode, errorStack) {
    this.isRepairing = true;
    this._showHealingToast("🛡️ Sparky's Self-Healing Brain: Diagnosing and fixing glitch...");

    try {
      const response = await fetch('/api/game/heal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          error: errorMessage,
          code: brokenCode,
          stack: errorStack
        })
      });

      if (!response.ok) {
        throw new Error(`Healing API error: ${response.statusText}`);
      }

      const data = await response.json();
      const healResult = data.result;

      if (healResult && healResult.fixed_game_code) {
        console.log("✨ Self-Healing successfully generated patch:", healResult.diagnosis);
        this._showHealingToast(`✨ Glitch Fixed: ${healResult.diagnosis || 'Game repaired!'}`, 4000);
        
        // Hot-reload fixed game into engine
        this.engine.loadGameFromCode(healResult.fixed_game_code, this.engine.currentMeta);

        // Mascot speaks repair confirmation
        if (window.appVoice && healResult.spoken_response) {
          window.appVoice.speak(healResult.spoken_response);
        }

        // Update skills counter
        if (window.appInstance) {
          window.appInstance.refreshMemoryStats();
        }
      }
    } catch (err) {
      console.error("Failed to auto-repair:", err);
      this._showHealingToast("⚠️ Could not auto-repair. Resetting to safe game...", 3000);
      this.engine.loadGameFromCode(window.DEFAULT_STARTER_GAME_CODE);
    } finally {
      this.isRepairing = false;
    }
  }

  _showHealingToast(message, duration = 3000) {
    if (!this.toastEl) return;
    this.toastEl.innerHTML = `<span>${message}</span>`;
    this.toastEl.classList.remove('hidden');

    setTimeout(() => {
      this.toastEl.classList.add('hidden');
    }, duration);
  }
}

window.SelfHealingManager = SelfHealingManager;
