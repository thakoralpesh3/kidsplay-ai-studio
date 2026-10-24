/**
 * KidsPlay AI Modular 2D Game Engine
 * Provides canvas rendering, retro audio synthesis, physics, particles, input, and hot-reloading.
 */

class RetroAudioSynth {
  constructor() {
    this.ctx = null;
    this.muted = false;
  }

  init() {
    if (!this.ctx) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (AudioContext) {
        this.ctx = new AudioContext();
      }
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  playSound(type) {
    if (this.muted) return;
    this.init();
    if (!this.ctx) return;

    const now = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.connect(gain);
    gain.connect(this.ctx.destination);

    if (type === 'jump') {
      osc.type = 'square';
      osc.frequency.setValueAtTime(150, now);
      osc.frequency.exponentialRampToValueAtTime(450, now + 0.15);
      gain.gain.setValueAtTime(0.2, now);
      gain.gain.linearRampToValueAtTime(0.01, now + 0.15);
      osc.start(now);
      osc.stop(now + 0.15);
    } else if (type === 'coin') {
      osc.type = 'sine';
      osc.frequency.setValueAtTime(987.77, now); // B5
      osc.frequency.setValueAtTime(1318.51, now + 0.08); // E6
      gain.gain.setValueAtTime(0.25, now);
      gain.gain.linearRampToValueAtTime(0.01, now + 0.25);
      osc.start(now);
      osc.stop(now + 0.25);
    } else if (type === 'powerup') {
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(300, now);
      osc.frequency.exponentialRampToValueAtTime(800, now + 0.25);
      gain.gain.setValueAtTime(0.3, now);
      gain.gain.linearRampToValueAtTime(0.01, now + 0.3);
      osc.start(now);
      osc.stop(now + 0.3);
    } else if (type === 'hit') {
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(220, now);
      osc.frequency.exponentialRampToValueAtTime(60, now + 0.2);
      gain.gain.setValueAtTime(0.3, now);
      gain.gain.linearRampToValueAtTime(0.01, now + 0.2);
      osc.start(now);
      osc.stop(now + 0.2);
    } else if (type === 'laser') {
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(900, now);
      osc.frequency.exponentialRampToValueAtTime(100, now + 0.12);
      gain.gain.setValueAtTime(0.2, now);
      gain.gain.linearRampToValueAtTime(0.01, now + 0.12);
      osc.start(now);
      osc.stop(now + 0.12);
    } else if (type === 'win') {
      const notes = [523.25, 659.25, 783.99, 1046.50]; // C5, E5, G5, C6
      notes.forEach((freq, idx) => {
        const o = this.ctx.createOscillator();
        const g = this.ctx.createGain();
        o.connect(g);
        g.connect(this.ctx.destination);
        o.type = 'triangle';
        o.frequency.setValueAtTime(freq, now + idx * 0.1);
        g.gain.setValueAtTime(0.25, now + idx * 0.1);
        g.gain.linearRampToValueAtTime(0.01, now + idx * 0.1 + 0.2);
        o.start(now + idx * 0.1);
        o.stop(now + idx * 0.1 + 0.2);
      });
    }
  }
}

class GameEngine {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext('2d');
    this.width = 800;
    this.height = 500;
    this.canvas.width = this.width;
    this.canvas.height = this.height;

    this.audio = new RetroAudioSynth();
    this.running = false;
    this.lastTime = 0;
    this.currentGame = null;
    this.currentCode = "";
    this.currentMeta = null;

    // Juice FX
    this.particles = [];
    this.scorePopups = [];
    this.shakeIntensity = 0;
    this.shakeDuration = 0;

    // Input state
    this.input = {
      keys: {
        left: false,
        right: false,
        up: false,
        down: false,
        space: false,
        action: false
      },
      pointer: {
        x: 0,
        y: 0,
        isDown: false
      }
    };

    this._bindEvents();
  }

  _bindEvents() {
    window.addEventListener('keydown', (e) => {
      this.audio.init();
      if (['ArrowLeft', 'KeyA'].includes(e.code)) this.input.keys.left = true;
      if (['ArrowRight', 'KeyD'].includes(e.code)) this.input.keys.right = true;
      if (['ArrowUp', 'KeyW'].includes(e.code)) this.input.keys.up = true;
      if (['ArrowDown', 'KeyS'].includes(e.code)) this.input.keys.down = true;
      if (e.code === 'Space') {
        this.input.keys.space = true;
        e.preventDefault();
      }
      if (['Enter', 'KeyZ', 'KeyX'].includes(e.code)) this.input.keys.action = true;
    });

    window.addEventListener('keyup', (e) => {
      if (['ArrowLeft', 'KeyA'].includes(e.code)) this.input.keys.left = false;
      if (['ArrowRight', 'KeyD'].includes(e.code)) this.input.keys.right = false;
      if (['ArrowUp', 'KeyW'].includes(e.code)) this.input.keys.up = false;
      if (['ArrowDown', 'KeyS'].includes(e.code)) this.input.keys.down = false;
      if (e.code === 'Space') this.input.keys.space = false;
      if (['Enter', 'KeyZ', 'KeyX'].includes(e.code)) this.input.keys.action = false;
    });

    const updatePointer = (e) => {
      const rect = this.canvas.getBoundingClientRect();
      const scaleX = this.canvas.width / rect.width;
      const scaleY = this.canvas.height / rect.height;
      this.input.pointer.x = (e.clientX - rect.left) * scaleX;
      this.input.pointer.y = (e.clientY - rect.top) * scaleY;
    };

    this.canvas.addEventListener('mousemove', updatePointer);
    this.canvas.addEventListener('mousedown', (e) => {
      this.audio.init();
      this.input.pointer.isDown = true;
      updatePointer(e);
    });
    window.addEventListener('mouseup', () => {
      this.input.pointer.isDown = false;
    });

    // Canvas click/tap handler for clicker & bubble popper games
    this.canvas.addEventListener('click', (e) => {
      this.audio.init();
      const rect = this.canvas.getBoundingClientRect();
      const scaleX = this.canvas.width / rect.width;
      const scaleY = this.canvas.height / rect.height;
      const clickX = (e.clientX - rect.left) * scaleX;
      const clickY = (e.clientY - rect.top) * scaleY;
      if (this.currentGame) {
        if (typeof this.currentGame.onClick === 'function') {
          this.currentGame.onClick(this, clickX, clickY);
        } else if (typeof this.currentGame.popAt === 'function') {
          this.currentGame.popAt(this, clickX, clickY, 35);
        }
      }
    });

    // Touch controls (supports full 4-way directional steering)
    const bindTouch = (id, keyName) => {
      const el = document.getElementById(id);
      if (!el) return;
      el.addEventListener('touchstart', (e) => {
        e.preventDefault();
        this.audio.init();
        this.input.keys[keyName] = true;
      });
      el.addEventListener('touchend', (e) => {
        e.preventDefault();
        this.input.keys[keyName] = false;
      });
    };

    bindTouch('btn-touch-left', 'left');
    bindTouch('btn-touch-right', 'right');
    bindTouch('btn-touch-up', 'up');
    bindTouch('btn-touch-down', 'down');
    bindTouch('btn-touch-jump', 'space');
    bindTouch('btn-touch-action', 'action');
  }

  updateHUD(hudData) {
    if (!hudData) return;
    this.hud = Object.assign(this.hud || {}, hudData);

    if (hudData.score !== undefined) {
      const el = document.getElementById('hud-score');
      if (el) el.textContent = hudData.score;
    }
    if (hudData.lives !== undefined) {
      const el = document.getElementById('hud-lives');
      if (el) {
        if (typeof hudData.lives === 'number') {
          el.textContent = '💖'.repeat(Math.max(0, hudData.lives)) || '💀';
        } else {
          el.textContent = hudData.lives;
        }
      }
    }
    if (hudData.combo !== undefined) {
      const el = document.getElementById('hud-combo');
      if (el) {
        el.textContent = hudData.combo;
        if (el.parentElement) {
          el.parentElement.classList.remove('pop-anim');
          void el.parentElement.offsetWidth;
          el.parentElement.classList.add('pop-anim');
        }
      }
    }
    if (hudData.magic !== undefined) {
      const el = document.getElementById('hud-magic-fill');
      if (el) {
        const pct = Math.min(100, Math.max(0, hudData.magic));
        el.style.width = pct + '%';
      }
    }
    if (hudData.bossHp !== undefined && hudData.bossMaxHp !== undefined) {
      const bossContainer = document.getElementById('hud-boss-chip');
      const bossFill = document.getElementById('hud-boss-fill');
      const bossTitle = document.getElementById('hud-boss-title');
      if (bossContainer && bossFill) {
        if (hudData.bossHp > 0) {
          bossContainer.style.display = 'inline-flex';
          const pct = Math.min(100, Math.max(0, (hudData.bossHp / hudData.bossMaxHp) * 100));
          bossFill.style.width = pct + '%';
          if (bossTitle && hudData.bossName) {
            bossTitle.textContent = hudData.bossName;
          }
        } else {
          bossContainer.style.display = 'none';
        }
      }
    }
    if (hudData.activePowerup !== undefined) {
      const powerupChip = document.getElementById('hud-powerup-chip');
      const powerupEmoji = document.getElementById('hud-powerup-emoji');
      const powerupVal = document.getElementById('hud-powerup-timer');
      if (powerupChip) {
        if (hudData.activePowerup) {
          powerupChip.style.display = 'inline-flex';
          if (powerupEmoji) powerupEmoji.textContent = hudData.activePowerup.emoji || '⚡';
          if (powerupVal) powerupVal.textContent = hudData.activePowerup.text || 'ACTIVE';
        } else {
          powerupChip.style.display = 'none';
        }
      }
    }
  }

  spawnParticles(x, y, colors = ['#ff007a', '#00f0ff', '#ffe600', '#fff'], count = 12) {
    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = Math.random() * 4 + 2;
      this.particles.push({
        x,
        y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed - 1.5,
        color: colors[Math.floor(Math.random() * colors.length)],
        radius: Math.random() * 4 + 3,
        alpha: 1,
        life: 1,
        decay: Math.random() * 0.03 + 0.02
      });
    }
  }

  spawnScorePopup(x, y, text, color = '#ffe600') {
    this.scorePopups.push({
      x,
      y,
      text,
      color,
      vy: -2,
      alpha: 1,
      life: 1,
      decay: 0.025
    });
  }

  triggerScreenShake(intensity = 6, durationMs = 200) {
    this.shakeIntensity = intensity;
    this.shakeDuration = durationMs;
  }

  loadGameFromCode(jsCode, meta = null) {
    try {
      this.currentCode = jsCode;
      this.currentMeta = meta;
      
      // Clean previous instance
      delete window.createGameInstance;

      // Secure Sandbox Execution
      const secureSandbox = new Function(
        'window', 'document', 'localStorage', 'sessionStorage', 'fetch', 'XMLHttpRequest',
        `"use strict";\n${jsCode}`
      );
      
      // Execute in isolated sandbox scope
      secureSandbox(window, document, {}, {}, undefined, undefined);

      if (typeof window.createGameInstance !== 'function') {
        throw new Error("Game code must define window.createGameInstance() function!");
      }

      this.currentGame = window.createGameInstance();
      if (typeof this.currentGame.init === 'function') {
        this.currentGame.init(this);
      }

      this.particles = [];
      this.scorePopups = [];
      this.start();
      return true;
    } catch (err) {
      console.error("Game engine error loading script:", err);
      if (window.SelfHealingManager) {
        window.SelfHealingManager.handleRuntimeError(err.message, jsCode, err.stack);
      }
      return false;
    }
  }

  restart() {
    if (this.currentGame && typeof this.currentGame.init === 'function') {
      this.particles = [];
      this.scorePopups = [];
      this.currentGame.init(this);
    }
  }

  start() {
    if (!this.running) {
      this.running = true;
      this.lastTime = performance.now();
      requestAnimationFrame(this._loop.bind(this));
    }
  }

  _loop(timestamp) {
    if (!this.running) return;

    const dt = Math.min((timestamp - this.lastTime) / 1000, 0.1);
    this.lastTime = timestamp;

    try {
      // Update Game
      if (this.currentGame && typeof this.currentGame.update === 'function') {
        this.currentGame.update(this, dt);
      }

      // Update Particles
      for (let i = this.particles.length - 1; i >= 0; i--) {
        const p = this.particles[i];
        p.x += p.vx;
        p.y += p.vy;
        p.vy += 0.1; // gravity
        p.alpha -= p.decay;
        if (p.alpha <= 0) this.particles.splice(i, 1);
      }

      // Update Score Popups
      for (let i = this.scorePopups.length - 1; i >= 0; i--) {
        const pop = this.scorePopups[i];
        pop.y += pop.vy;
        pop.alpha -= pop.decay;
        if (pop.alpha <= 0) this.scorePopups.splice(i, 1);
      }

      // Update Screen Shake
      if (this.shakeDuration > 0) {
        this.shakeDuration -= dt * 1000;
      } else {
        this.shakeIntensity = 0;
      }

      // Render
      this.ctx.save();
      if (this.shakeIntensity > 0) {
        const ox = (Math.random() - 0.5) * this.shakeIntensity * 2;
        const oy = (Math.random() - 0.5) * this.shakeIntensity * 2;
        this.ctx.translate(ox, oy);
      }

      if (this.currentGame && typeof this.currentGame.draw === 'function') {
        this.currentGame.draw(this, this.ctx);
      } else {
        this._drawDefaultBackdrop();
      }

      // Draw Particles
      this.particles.forEach(p => {
        this.ctx.save();
        this.ctx.globalAlpha = Math.max(0, p.alpha);
        this.ctx.fillStyle = p.color;
        this.ctx.beginPath();
        this.ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        this.ctx.fill();
        this.ctx.restore();
      });

      // Draw Popups
      this.scorePopups.forEach(pop => {
        this.ctx.save();
        this.ctx.globalAlpha = Math.max(0, pop.alpha);
        this.ctx.fillStyle = pop.color;
        this.ctx.font = 'bold 20px Fredoka, sans-serif';
        this.ctx.textAlign = 'center';
        this.ctx.fillText(pop.text, pop.x, pop.y);
        this.ctx.restore();
      });

      this.ctx.restore();

    } catch (err) {
      console.error("Runtime exception inside game loop:", err);
      if (window.SelfHealingManager) {
        window.SelfHealingManager.handleRuntimeError(err.message, this.currentCode, err.stack);
      }
    }

    requestAnimationFrame(this._loop.bind(this));
  }

  _drawDefaultBackdrop() {
    this.ctx.fillStyle = '#14152e';
    this.ctx.fillRect(0, 0, this.width, this.height);
    this.ctx.fillStyle = '#ffe600';
    this.ctx.font = 'bold 24px Fredoka, sans-serif';
    this.ctx.textAlign = 'center';
    this.ctx.fillText('🎮 Sparky Game Studio Ready!', this.width / 2, this.height / 2);
  }
}

// Starter Default Game: "Magical Unicorn Donut Adventure"
const DEFAULT_STARTER_GAME_CODE = `
window.createGameInstance = function() {
  let player = {
    x: 100,
    y: 360,
    w: 50,
    h: 50,
    vy: 0,
    isJumping: false,
    speed: 300,
    emoji: '🦄',
    hasShield: true,
    score: 0,
    lives: 3
  };

  let donuts = [];
  let stars = [];
  let clouds = [];
  let groundY = 410;
  let spawnTimer = 0;
  let gameOver = false;
  let winEffectTimer = 0;

  return {
    init: function(engine) {
      player.x = 100;
      player.y = groundY - 50;
      player.vy = 0;
      player.isJumping = false;
      player.score = 0;
      player.lives = 3;
      gameOver = false;
      donuts = [];
      stars = [];
      clouds = [
        { x: 100, y: 80, s: 0.8 },
        { x: 350, y: 120, s: 1.2 },
        { x: 650, y: 70, s: 0.9 }
      ];

      // Spawn initial donuts
      for (let i = 0; i < 5; i++) {
        donuts.push({
          x: 250 + i * 120,
          y: groundY - 50 - Math.sin(i) * 80,
          emoji: '🍩',
          bob: Math.random() * Math.PI
        });
      }

      if (engine.updateHUD) {
        engine.updateHUD({ score: 0, lives: 3, combo: 'x1' });
      }
    },

    update: function(engine, dt) {
      if (gameOver) {
        if (engine.input.keys.space || engine.input.keys.action) {
          this.init(engine);
        }
        return;
      }

      // Movement
      if (engine.input.keys.left) player.x -= player.speed * dt;
      if (engine.input.keys.right) player.x += player.speed * dt;
      player.x = Math.max(20, Math.min(engine.width - 70, player.x));

      // Jump
      if ((engine.input.keys.space || engine.input.keys.up) && !player.isJumping) {
        player.vy = -560;
        player.isJumping = true;
        engine.audio.playSound('jump');
        engine.spawnParticles(player.x + 25, player.y + 45, ['#ff007a', '#ffe600', '#00f0ff'], 10);
      }

      // Gravity
      player.vy += 1200 * dt;
      player.y += player.vy * dt;

      if (player.y >= groundY - player.h) {
        player.y = groundY - player.h;
        player.vy = 0;
        player.isJumping = false;
      }

      // Spawn items
      spawnTimer += dt;
      if (spawnTimer > 1.8) {
        spawnTimer = 0;
        donuts.push({
          x: engine.width + 20,
          y: groundY - 40 - Math.random() * 120,
          emoji: Math.random() > 0.3 ? '🍩' : '⭐',
          bob: 0
        });
      }

      // Update clouds
      clouds.forEach(c => {
        c.x -= 20 * dt;
        if (c.x < -100) c.x = engine.width + 50;
      });

      // Update and collect donuts
      for (let i = donuts.length - 1; i >= 0; i--) {
        const d = donuts[i];
        d.x -= 140 * dt;
        d.bob += dt * 4;

        // Collision
        const dist = Math.hypot((player.x + 25) - d.x, (player.y + 25) - (d.y + Math.sin(d.bob) * 6));
        if (dist < 40) {
          const pts = d.emoji === '⭐' ? 200 : 100;
          player.score += pts;
          engine.audio.playSound(d.emoji === '⭐' ? 'powerup' : 'coin');
          engine.spawnParticles(d.x, d.y, ['#ff4d4d', '#ffb84d', '#ffff4d', '#4da6ff', '#b84dff'], 15);
          engine.spawnScorePopup(d.x, d.y, '+' + pts, '#ffe600');
          donuts.splice(i, 1);
          if (engine.updateHUD) {
            engine.updateHUD({ score: player.score, combo: 'x' + Math.min(5, Math.floor(player.score / 300) + 1) });
          }
        } else if (d.x < -40) {
          donuts.splice(i, 1);
        }
      }
    },

    draw: function(engine, ctx) {
      // Sky gradient
      const grad = ctx.createLinearGradient(0, 0, 0, engine.height);
      grad.addColorStop(0, '#2d124d');
      grad.addColorStop(0.7, '#6b117b');
      grad.addColorStop(1, '#ff4d88');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, engine.width, engine.height);

      // Rainbow Arc
      ctx.save();
      ctx.lineWidth = 12;
      const rainbowColors = ['#ff0000', '#ff7700', '#ffff00', '#00ff00', '#0099ff', '#9900ff'];
      rainbowColors.forEach((col, idx) => {
        ctx.strokeStyle = col;
        ctx.beginPath();
        ctx.arc(engine.width / 2, 450, 320 - idx * 12, Math.PI, 0, false);
        ctx.stroke();
      });
      ctx.restore();

      // Clouds
      ctx.font = '40px serif';
      clouds.forEach(c => {
        ctx.fillText('☁️', c.x, c.y);
      });

      // Ground (Magical Candyland Grass)
      ctx.fillStyle = '#00e676';
      ctx.fillRect(0, groundY, engine.width, engine.height - groundY);
      ctx.fillStyle = '#ff007a';
      ctx.fillRect(0, groundY + 10, engine.width, 6);

      // Donuts & Stars
      donuts.forEach(d => {
        const curY = d.y + Math.sin(d.bob) * 6;
        ctx.font = '36px serif';
        ctx.textAlign = 'center';
        ctx.fillText(d.emoji, d.x, curY);
      });

      // Player Unicorn
      ctx.save();
      ctx.font = '44px serif';
      ctx.textAlign = 'center';
      
      // Magic Shield Aura
      if (player.hasShield) {
        ctx.beginPath();
        ctx.arc(player.x + 25, player.y + 25, 32, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(0, 240, 255, 0.6)';
        ctx.lineWidth = 4;
        ctx.stroke();
      }

      ctx.fillText(player.emoji, player.x + 25, player.y + 38);
      ctx.restore();

      // HUD Score & Hearts
      ctx.fillStyle = '#fff';
      ctx.font = 'bold 22px Fredoka, sans-serif';
      ctx.textAlign = 'left';
      ctx.fillText('⭐ Score: ' + player.score, 24, 40);

      ctx.textAlign = 'right';
      ctx.fillText('💖💖💖', engine.width - 24, 40);
    }
  };
};
`;

window.GameEngine = GameEngine;
window.DEFAULT_STARTER_GAME_CODE = DEFAULT_STARTER_GAME_CODE;
