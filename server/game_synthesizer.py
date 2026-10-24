"""
KidsPlay AI Studio - Universal Multi-Genre HTML/CSS/JS Game Synthesizer
Generates complete, responsive, kid-friendly 60fps games across 6 core genres
with rich HTML overlays, CSS theme classes, retro audio hooks, and juice FX.
"""

import re
import json
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger("GameSynthesizer")

GENRE_SPACE_SHOOTER = "space_shooter"
GENRE_CANDY_CATCHER = "candy_catcher"
GENRE_CARTOON_RACER = "cartoon_racer"
GENRE_MAZE_ADVENTURE = "maze_adventure"
GENRE_BUBBLE_POPPER = "bubble_pop"
GENRE_PLATFORMER = "platformer"

def classify_genre(prompt: str) -> str:
    p = prompt.lower()
    space_kw = [
        "સ્પેસ", "રોકેટ", "ઉલ્કા", "એલિયન", "લેઝર", "શૂટર", "શૂટ", "અંતરિક્ષ", "તારાઓ",
        "space", "rocket", "alien", "meteor", "laser", "shoot", "shooter", "galaxy", "ufo",
        "अंतरिक्ष", "रॉकेट", "निशाना"
    ]
    if any(k in p for k in space_kw):
        return GENRE_SPACE_SHOOTER

    racer_kw = [
        "કાર", "રેસિંગ", "ગાડી", "ડ્રાઇવ", "હાઇવે", "ટર્બો", "ટ્રાફિક", "મોટર",
        "car", "racing", "racer", "drive", "highway", "traffic", "turbo", "speed", "vehicle",
        "गाड़ी", "कार", "रेस", "दौड़"
    ]
    if any(k in p for k in racer_kw):
        return GENRE_CARTOON_RACER

    catcher_kw = [
        "કેન્ડી", "ડોનટ", "ફળ", "ટોપલી", "પકડવા", "પકડો", "આકાશમાંથી", "ચોકલેટ", "કેક",
        "catch", "catcher", "candy", "donut", "fruit", "basket", "drop", "falling", "sweets",
        "पकड़ना", "कैंडी", "फल", "टोकरी"
    ]
    if any(k in p for k in catcher_kw):
        return GENRE_CANDY_CATCHER

    maze_kw = [
        "મેઇઝ", "ભૂલભુલામણી", "ચાવી", "દરવાજો", "ખજાનો", "રૂમ", "દિવાલ",
        "maze", "labyrinth", "dungeon", "key", "door", "treasure", "quest", "explore",
        "भूलभुलैया", "चाबी", "खजाना", "कमरा"
    ]
    if any(k in p for k in maze_kw):
        return GENRE_MAZE_ADVENTURE

    bubble_kw = [
        "બબલ", "પરપોટા", "પોપ", "ફુગ્ગા", "ક્લિક", "દડો",
        "bubble", "pop", "balloon", "physics", "clicker", "tap", "burst",
        "गुब्बारा", "बबल", "फोड़ना"
    ]
    if any(k in p for k in bubble_kw):
        return GENRE_BUBBLE_POPPER

    return GENRE_PLATFORMER

def _extract_theme_details(prompt: str, genre: str, language: str) -> Dict[str, Any]:
    p = prompt.lower()
    is_gu = language.startswith("gu")
    is_hi = language.startswith("hi")

    player_emoji = "🦄"
    collectible_emoji = "⭐"
    obstacle_emoji = "👾"

    if "દેડકો" in p or "frog" in p or "મેઢક" in p:
        player_emoji = "🐸"
        collectible_emoji = "🪰"
        obstacle_emoji = "🐊"
    elif "ડાયનાસોર" in p or "dino" in p or "dinosaur" in p:
        player_emoji = "🦖"
        collectible_emoji = "🍖"
        obstacle_emoji = "🌋"
    elif "સુપરહીરો" in p or "superhero" in p or "hero" in p:
        player_emoji = "🦸"
        collectible_emoji = "💎"
        obstacle_emoji = "⚡"
    elif "સસલું" in p or "bunny" in p or "rabbit" in p:
        player_emoji = "🐰"
        collectible_emoji = "🥕"
        obstacle_emoji = "🕳️"
    elif "બિલાડી" in p or "cat" in p or "kitty" in p:
        player_emoji = "🐱"
        collectible_emoji = "🐟"
        obstacle_emoji = "🧶"
    elif "રોકેટ" in p or "સ્પેસ" in p or genre == GENRE_SPACE_SHOOTER:
        player_emoji = "🚀"
        collectible_emoji = "⭐"
        obstacle_emoji = "☄️"
    elif "કાર" in p or "રેસિંગ" in p or genre == GENRE_CARTOON_RACER:
        player_emoji = "🏎️"
        collectible_emoji = "🪙"
        obstacle_emoji = "🚧"
    elif "કેન્ડી" in p or "ડોનટ" in p or genre == GENRE_CANDY_CATCHER:
        player_emoji = "🧺"
        collectible_emoji = "🍩"
        obstacle_emoji = "💣"
    elif genre == GENRE_MAZE_ADVENTURE:
        player_emoji = "🧙"
        collectible_emoji = "🔑"
        obstacle_emoji = "👻"
    elif genre == GENRE_BUBBLE_POPPER:
        player_emoji = "🪄"
        collectible_emoji = "🫧"
        obstacle_emoji = "💥"

    presets = {
        GENRE_SPACE_SHOOTER: {
            "title_gu": f"{player_emoji} સ્પેસ ગેલેક્સી શૂટર 🌌",
            "title_hi": f"{player_emoji} स्पेस गैलेक्सी शूटर 🌌",
            "title_en": f"{player_emoji} Cosmic Galaxy Shooter 🌌",
            "bg_gradient": ["#080918", "#170f38", "#2d0b59"],
            "accent": "#00f0ff",
            "css_class": "theme-space",
            "instructions_gu": "ખસવા માટે એરો કી (◀ ▶ ▲ ▼) વાપરો, લેઝર છોડવા સ્પેસબાર અથવા જાદુ દબાવો! ઉલ્કાઓ તોડીને સ્કોર બનાવો!",
            "instructions_hi": "हिलने के लिए तीर कुंजियों का उपयोग करें, लेजर चलाने के लिए स्पेसबार दबाएं!",
            "instructions_en": "Use Arrow keys or touch to steer, press Space or Action to fire lasers! Blast meteors to score!",
            "speech_gu": "અંતરિક્ષમાં રોકેટ તૈયાર છે! સ્પેસબારથી લેઝર છોડો અને ગેલેક્સી બચાવો! 🚀✨",
            "speech_hi": "अंतरिक्ष रॉकेट तैयार है! लेजर दागिए और उल्काओं से बचिए! 🚀✨",
            "speech_en": "Your cosmic starfighter is powered up! Fire lasers with Spacebar and defend the galaxy! 🚀✨"
        },
        GENRE_CARTOON_RACER: {
            "title_gu": f"{player_emoji} ટર્બો હાઇવે રેસિંગ 🏎️💨",
            "title_hi": f"{player_emoji} टर्बो हाईवे रेसिंग 🏎️💨",
            "title_en": f"{player_emoji} Turbo Highway Racer 🏎️💨",
            "bg_gradient": ["#1c1d24", "#2c303d", "#111218"],
            "accent": "#ffe600",
            "css_class": "theme-racer",
            "instructions_gu": "લેન બદલવા ડાબી/જમણી કી (◀ ▶) વાપરો, ટર્બો નાઇટ્રો સ્પીડ માટે ▲ અથવા સ્પેસબાર દબાવો! અવરોધોથી બચો!",
            "instructions_hi": "लेन बदलने के लिए बायाँ/दायाँ तीर इस्तेमाल करें, टर्बो गति के लिए स्पेसबार दबाएं!",
            "instructions_en": "Use Left/Right to change lanes, tap Up or Space for Turbo Nitro! Dodge traffic cones!",
            "speech_gu": "ટર્બો કાર રેસ શરૂ થઈ ગઈ છે! અવરોધોથી બચીને સોનાના સિક્કા પકડો! 🏎️⚡",
            "speech_hi": "टर्बो कार दौड़ शुरू हो गई है! बाधाओं से बचिए और सिक्के जीतिए! 🏎️⚡",
            "speech_en": "Engines roaring! Dodge the road hazards, pick up nitro boosters and speed to victory! 🏎️⚡"
        },
        GENRE_CANDY_CATCHER: {
            "title_gu": f"{player_emoji} જાદુઈ કેન્ડી કેચર 🍭🧁",
            "title_hi": f"{player_emoji} जादुई कैंडी कैचर 🍭🧁",
            "title_en": f"{player_emoji} Magical Sweet Catcher 🍭🧁",
            "bg_gradient": ["#2b0d3d", "#5c1363", "#ff4d88"],
            "accent": "#ff007a",
            "css_class": "theme-candy",
            "instructions_gu": "ટોપલી ખસેડવા ◀ ▶ કી વાપરો! આકાશમાંથી પડતી કેન્ડી, ડોનટ્સ અને તારા પકડો! બોમ્બથી બચો!",
            "instructions_hi": "टोकरी हिलाने के लिए तीर कुंजियों का उपयोग करें! गिरती मिठाइयाँ पकड़ें और बम से बचें!",
            "instructions_en": "Move left and right with Arrow keys to catch falling donuts & candies! Avoid the bombs!",
            "speech_gu": "વાહ! આકાશમાંથી સ્વાદિષ્ટ કેન્ડી અને ડોનટ્સનો વરસાદ થઈ રહ્યો છે! ટોપલીમાં ઝડપથી પકડી લો! 🍩🎉",
            "speech_hi": "आसमान से मिठाइयों की बारिश हो रही है! जल्दी से टोकरी में पकड़ें! 🍩🎉",
            "speech_en": "Delicious treats are raining from the sky! Move your basket and catch them all! 🍩🎉"
        },
        GENRE_MAZE_ADVENTURE: {
            "title_gu": f"{player_emoji} જાદુઈ મેઇઝ એડવેન્ચર 🏰🗝️",
            "title_hi": f"{player_emoji} जादुई भूलभुलैया एडवेंचर 🏰🗝️",
            "title_en": f"{player_emoji} Magic Dungeon Maze 🏰🗝️",
            "bg_gradient": ["#0d1117", "#161b22", "#21262d"],
            "accent": "#00e676",
            "css_class": "theme-arcade",
            "instructions_gu": "મેઇઝમાં ફરવા એરો કી (◀ ▶ ▲ ▼) વાપરો! ૩ સોનેરી ચાવીઓ (🔑) શોધો અને જાદુઈ દરવાજો (🚪) ખોલો!",
            "instructions_hi": "भूलभुलैया में चलने के लिए तीर कुंजियों का उपयोग करें! 3 चाबियाँ ढूंढकर दरवाजा खोलें!",
            "instructions_en": "Navigate the maze with Arrow keys! Collect all 3 golden keys to open the treasure portal!",
            "speech_gu": "જાદુઈ મેઇઝ તૈયાર છે! ૩ સોનેરી ચાવીઓ શોધો અને રહસ્યમય ખજાનાનો દરવાજો ખોલો! 🗝️✨",
            "speech_hi": "जादुई भूलभुलैया तैयार है! 3 चाबियाँ ढूंढिए और खजाना खोलिए! 🗝️✨",
            "speech_en": "The labyrinth is open! Collect the 3 golden keys to unlock the enchanted treasure! 🗝️✨"
        },
        GENRE_BUBBLE_POPPER: {
            "title_gu": f"{player_emoji} રંગબેરંગી બબલ પોપર 🫧✨",
            "title_hi": f"{player_emoji} रंग-बिरंगा बबल पॉपर 🫧✨",
            "title_en": f"{player_emoji} Rainbow Bubble Popper 🫧✨",
            "bg_gradient": ["#0c1b33", "#123b5c", "#007799"],
            "accent": "#00f0ff",
            "css_class": "theme-bubble",
            "instructions_gu": "પરપોટા ફોડવા માઉસ/સ્ક્રીન પર ટેપ કરો, અથવા આખી સ્ક્રીનમાં શોકવેવ છોડવા સ્પેસબાર દબાવો!",
            "instructions_hi": "बबल फोड़ने के लिए क्लिक करें या स्पेसबार दबाकर जादू चलाएं!",
            "instructions_en": "Click or tap on floating bubbles to pop them, or press Space for a mega bubble shockwave!",
            "speech_gu": "રંગબેરંગી પરપોટા આકાશમાં ઉડી રહ્યા છે! ટેપ કરો અને મજેદાર પોપિંગ સાઉન્ડ માણો! 🫧🎶",
            "speech_hi": "रंग-बिरंगे बुलबुले उड़ रहे हैं! क्लिक करके फोड़ें और मज़ा लें! 🫧🎶",
            "speech_en": "Sparkling rainbow bubbles are floating up! Tap or click to pop them in chain reactions! 🫧🎶"
        },
        GENRE_PLATFORMER: {
            "title_gu": f"{player_emoji} જાદુઈ કૂદકાની રમત 🦘🌈",
            "title_hi": f"{player_emoji} जादुई कूदने का गेम 🦘🌈",
            "title_en": f"{player_emoji} Bouncy Platform Hero 🦘🌈",
            "bg_gradient": ["#1f103b", "#491b6d", "#7b1fa2"],
            "accent": "#ff007a",
            "css_class": "theme-forest",
            "instructions_gu": "દોડવા માટે ◀ ▶ કી વાપરો, ઊંચો કૂદકો લગાવવા સ્પેસબાર અથવા ▲ દબાવો! તારા ભેગા કરો!",
            "instructions_hi": "दौड़ने के लिए तीर कुंजियाँ दबाएं, कूदने के लिए स्पेसबार दबाएं!",
            "instructions_en": "Run with Left/Right arrows, press Space or Up to jump high! Collect sparkling stars!",
            "speech_gu": "સુપર કૂદકાની રમત તૈયાર છે! સ્પેસબારથી ઊંચો કૂદકો લગાવો અને સોનેરી તારા પકડો! 🦘✨",
            "speech_hi": "कूदने का खेल तैयार है! स्पेसबार दबाइए और तारे जीतिए! 🦘✨",
            "speech_en": "Your jumping adventure is live! Leap across platforms and collect sparkling treasures! 🦘✨"
        }
    }

    preset = presets.get(genre, presets[GENRE_PLATFORMER])
    title = preset["title_gu"] if is_gu else (preset["title_hi"] if is_hi else preset["title_en"])
    instructions = preset["instructions_gu"] if is_gu else (preset["instructions_hi"] if is_hi else preset["instructions_en"])
    speech = preset["speech_gu"] if is_gu else (preset["speech_hi"] if is_hi else preset["speech_en"])

    hud_html = '<div class="hud-chip hud-lives-chip"><span class="hud-emoji">💖</span> <span class="hud-val" id="hud-lives">3</span></div><div class="hud-chip hud-score-chip"><span class="hud-emoji">⭐</span> <span class="hud-val" id="hud-score">0</span></div><div class="hud-chip hud-combo-chip"><span class="hud-emoji">⚡</span> <span class="hud-val" id="hud-combo">x1</span></div><div class="hud-chip hud-powerup-chip" id="hud-powerup-chip" style="display:none;"><span class="hud-emoji" id="hud-powerup-emoji">🛡️</span> <span class="hud-val" id="hud-powerup-timer">SHIELD</span></div><div class="hud-boss-chip" id="hud-boss-chip" style="display:none;"><span class="hud-boss-title" id="hud-boss-title">👾 BOSS</span><div class="hud-boss-bar"><div class="hud-boss-fill" id="hud-boss-fill" style="width:100%;"></div></div></div>'

    return {
        "title": title,
        "genre": genre,
        "spoken_response": speech,
        "instructions": instructions,
        "player_emoji": player_emoji,
        "collectible_emoji": collectible_emoji,
        "obstacle_emoji": obstacle_emoji,
        "bg_gradient": preset["bg_gradient"],
        "accent": preset["accent"],
        "css_class": preset["css_class"],
        "hud_html": hud_html
    }

def _generate_code_space_shooter(p_emoji: str, c_emoji: str, o_emoji: str) -> str:
    return f'''
window.createGameInstance = function() {{
  let ship = {{
    x: 400,
    y: 420,
    w: 50,
    h: 50,
    speed: 380,
    lives: 3,
    score: 0,
    combo: 1,
    emoji: '{p_emoji}',
    fireCooldown: 0,
    shieldTimer: 0,
    doubleLaserTimer: 0
  }};

  let lasers = [];
  let meteors = [];
  let stars = [];
  let powerups = [];
  let bossOrbs = [];
  let spawnTimer = 0;
  let powerupTimer = 0;
  let gameOver = false;
  let victory = false;

  let boss = {{
    active: false,
    defeated: false,
    x: 400,
    y: -80,
    targetY: 90,
    w: 70,
    h: 70,
    vx: 130,
    hp: 25,
    maxHp: 25,
    name: '👾 ALIEN TITAN BOSS',
    shootTimer: 0
  }};

  return {{
    init: function(engine) {{
      ship.x = engine.width / 2 - 25;
      ship.y = engine.height - 80;
      ship.lives = 3;
      ship.score = 0;
      ship.combo = 1;
      ship.fireCooldown = 0;
      ship.shieldTimer = 0;
      ship.doubleLaserTimer = 0;
      lasers = [];
      meteors = [];
      powerups = [];
      bossOrbs = [];
      gameOver = false;
      victory = false;

      boss.active = false;
      boss.defeated = false;
      boss.hp = 25;
      boss.x = engine.width / 2;
      boss.y = -80;

      stars = [];
      for (let i = 0; i < 70; i++) {{
        stars.push({{
          x: Math.random() * engine.width,
          y: Math.random() * engine.height,
          size: Math.random() * 2.5 + 1,
          speed: Math.random() * 40 + 20
        }});
      }}
      if (engine.updateHUD) {{
        engine.updateHUD({{
          score: ship.score,
          lives: ship.lives,
          combo: 'x' + ship.combo,
          bossHp: 0,
          bossMaxHp: boss.maxHp,
          activePowerup: null
        }});
      }}
    }},

    update: function(engine, dt) {{
      if (gameOver || victory) {{
        if (engine.input.keys.space || engine.input.keys.action) {{
          this.init(engine);
        }}
        return;
      }}

      // Background stars parallax
      stars.forEach(s => {{
        s.y += s.speed * dt;
        if (s.y > engine.height) {{
          s.y = 0;
          s.x = Math.random() * engine.width;
        }}
      }});

      // Ship movement
      if (engine.input.keys.left) ship.x -= ship.speed * dt;
      if (engine.input.keys.right) ship.x += ship.speed * dt;
      if (engine.input.keys.up) ship.y -= ship.speed * dt;
      if (engine.input.keys.down) ship.y += ship.speed * dt;

      ship.x = Math.max(10, Math.min(engine.width - 60, ship.x));
      ship.y = Math.max(50, Math.min(engine.height - 70, ship.y));

      // Powerup Timers
      if (ship.shieldTimer > 0) ship.shieldTimer -= dt;
      if (ship.doubleLaserTimer > 0) ship.doubleLaserTimer -= dt;

      // Update Powerup HUD
      if (engine.updateHUD) {{
        let activeP = null;
        if (ship.shieldTimer > 0) {{
          activeP = {{ emoji: '🛡️', text: Math.ceil(ship.shieldTimer) + 's SHIELD' }};
        }} else if (ship.doubleLaserTimer > 0) {{
          activeP = {{ emoji: '⚡⚡', text: Math.ceil(ship.doubleLaserTimer) + 's DUAL LASER' }};
        }}
        engine.updateHUD({{ activePowerup: activeP }});
      }}

      // Player Firing (Dual laser support)
      ship.fireCooldown -= dt;
      if ((engine.input.keys.space || engine.input.keys.action) && ship.fireCooldown <= 0) {{
        ship.fireCooldown = 0.20;
        if (ship.doubleLaserTimer > 0) {{
          lasers.push({{ x: ship.x + 12, y: ship.y - 10, vy: -650 }});
          lasers.push({{ x: ship.x + 38, y: ship.y - 10, vy: -650 }});
        }} else {{
          lasers.push({{ x: ship.x + 25, y: ship.y - 10, vy: -600 }});
        }}
        engine.audio.playSound('laser');
        engine.spawnParticles(ship.x + 25, ship.y, ['#00f0ff', '#ffe600'], 4);
      }}

      // Lasers update
      for (let i = lasers.length - 1; i >= 0; i--) {{
        const l = lasers[i];
        l.y += l.vy * dt;
        if (l.y < -20) lasers.splice(i, 1);
      }}

      // Check Boss Trigger (at score >= 800)
      if (ship.score >= 800 && !boss.active && !boss.defeated) {{
        boss.active = true;
        boss.y = -80;
        boss.hp = boss.maxHp;
        engine.triggerScreenShake(14, 600);
        engine.spawnScorePopup(engine.width / 2, 140, '⚠️ ALIEN BOSS INCOMING! ⚠️', '#ff0055');
        engine.audio.playSound('powerup');
        if (engine.updateHUD) {{
          engine.updateHUD({{ bossHp: boss.hp, bossMaxHp: boss.maxHp, bossName: boss.name }});
        }}
      }}

      // Boss Behavior
      if (boss.active) {{
        if (boss.y < boss.targetY) {{
          boss.y += 100 * dt;
        }} else {{
          boss.x += boss.vx * dt;
          if (boss.x < 60 || boss.x > engine.width - 60) boss.vx *= -1;

          boss.shootTimer += dt;
          if (boss.shootTimer > 1.3) {{
            boss.shootTimer = 0;
            bossOrbs.push({{ x: boss.x - 20, y: boss.y + 30, vx: -50, vy: 190 }});
            bossOrbs.push({{ x: boss.x + 20, y: boss.y + 30, vx: 50, vy: 190 }});
            engine.audio.playSound('hit');
          }}
        }}

        // Check player laser hits on boss
        for (let j = lasers.length - 1; j >= 0; j--) {{
          const l = lasers[j];
          if (Math.hypot(l.x - boss.x, l.y - boss.y) < 45) {{
            lasers.splice(j, 1);
            boss.hp -= 1;
            engine.audio.playSound('hit');
            engine.spawnParticles(l.x, l.y, ['#ff0055', '#ff9900', '#00f0ff'], 8);
            if (engine.updateHUD) {{
              engine.updateHUD({{ bossHp: Math.max(0, boss.hp), bossMaxHp: boss.maxHp }});
            }}

            if (boss.hp <= 0) {{
              boss.active = false;
              boss.defeated = true;
              ship.score += 2500;
              victory = true;
              engine.triggerScreenShake(20, 1000);
              engine.spawnParticles(boss.x, boss.y, ['#ff0055', '#ffe600', '#00f0ff', '#ffffff'], 45);
              engine.spawnScorePopup(boss.x, boss.y, '🏆 BOSS DEFEATED! +2500', '#ffe600');
              engine.audio.playSound('win');
              if (engine.updateHUD) engine.updateHUD({{ score: ship.score, bossHp: 0 }});
              break;
            }}
          }}
        }}
      }}

      // Boss Orbs update
      for (let i = bossOrbs.length - 1; i >= 0; i--) {{
        const orb = bossOrbs[i];
        orb.x += orb.vx * dt;
        orb.y += orb.vy * dt;

        if (Math.hypot((ship.x + 25) - orb.x, (ship.y + 25) - orb.y) < 32) {{
          bossOrbs.splice(i, 1);
          if (ship.shieldTimer > 0) {{
            engine.audio.playSound('powerup');
            engine.spawnScorePopup(ship.x + 25, ship.y, 'SHIELD BLOCKED!', '#00f0ff');
          }} else {{
            ship.lives -= 1;
            ship.combo = 1;
            engine.audio.playSound('hit');
            engine.triggerScreenShake(12, 350);
            engine.spawnParticles(ship.x + 25, ship.y + 25, ['#ff0000', '#ff9900'], 20);
            if (ship.lives <= 0) gameOver = true;
          }}
          if (engine.updateHUD) engine.updateHUD({{ lives: Math.max(0, ship.lives), combo: 'x' + ship.combo }});
          continue;
        }}
        if (orb.y > engine.height + 30) bossOrbs.splice(i, 1);
      }}

      // Powerups drop generator
      powerupTimer += dt;
      if (powerupTimer > 7.0) {{
        powerupTimer = 0;
        const isShield = Math.random() < 0.5;
        powerups.push({{
          x: Math.random() * (engine.width - 80) + 40,
          y: -30,
          vy: 90,
          type: isShield ? 'shield' : 'double_laser',
          emoji: isShield ? '🛡️' : '⚡'
        }});
      }}

      // Powerups update
      for (let i = powerups.length - 1; i >= 0; i--) {{
        const p = powerups[i];
        p.y += p.vy * dt;

        if (Math.hypot((ship.x + 25) - p.x, (ship.y + 25) - p.y) < 36) {{
          if (p.type === 'shield') {{
            ship.shieldTimer = 8;
            engine.spawnScorePopup(p.x, p.y, '🛡️ SHIELD ACTIVE! (8s)', '#00f0ff');
          }} else {{
            ship.doubleLaserTimer = 10;
            engine.spawnScorePopup(p.x, p.y, '⚡ DUAL LASER! (10s)', '#ffe600');
          }}
          engine.audio.playSound('powerup');
          engine.spawnParticles(p.x, p.y, ['#00f0ff', '#ffe600', '#ffffff'], 16);
          powerups.splice(i, 1);
          continue;
        }}
        if (p.y > engine.height + 30) powerups.splice(i, 1);
      }}

      // Meteors & Minions spawn
      spawnTimer += dt;
      if (spawnTimer > (boss.active ? 1.4 : 0.85)) {{
        spawnTimer = 0;
        const isBonus = Math.random() < 0.25;
        meteors.push({{
          x: Math.random() * (engine.width - 60) + 30,
          y: -40,
          w: 40,
          h: 40,
          vy: Math.random() * 110 + 130,
          vx: (Math.random() - 0.5) * 60,
          emoji: isBonus ? '{c_emoji}' : '{o_emoji}',
          isBonus: isBonus,
          rotation: 0
        }});
      }}

      for (let i = meteors.length - 1; i >= 0; i--) {{
        const m = meteors[i];
        m.y += m.vy * dt;
        m.x += m.vx * dt;
        m.rotation += dt * 2;

        let meteorHit = false;
        for (let j = lasers.length - 1; j >= 0; j--) {{
          const l = lasers[j];
          if (Math.hypot(l.x - m.x, l.y - m.y) < 32) {{
            lasers.splice(j, 1);
            meteorHit = true;
            break;
          }}
        }}

        if (meteorHit) {{
          const pts = m.isBonus ? 250 : 100;
          ship.score += pts * ship.combo;
          ship.combo = Math.min(ship.combo + 1, 8);
          engine.audio.playSound(m.isBonus ? 'powerup' : 'coin');
          engine.spawnParticles(m.x, m.y, ['#ff0055', '#ff9900', '#00f0ff', '#ffe600'], 15);
          engine.spawnScorePopup(m.x, m.y, '+' + (pts * ship.combo), '#00f0ff');
          meteors.splice(i, 1);
          if (engine.updateHUD) engine.updateHUD({{ score: ship.score, combo: 'x' + ship.combo }});
          continue;
        }}

        if (Math.hypot((ship.x + 25) - m.x, (ship.y + 25) - m.y) < 36) {{
          if (m.isBonus) {{
            ship.score += 200;
            engine.audio.playSound('powerup');
            engine.spawnScorePopup(m.x, m.y, '+200', '#ffe600');
          }} else {{
            if (ship.shieldTimer > 0) {{
              engine.audio.playSound('powerup');
              engine.spawnScorePopup(m.x, m.y, 'SHIELD DEFLECT!', '#00f0ff');
            }} else {{
              ship.lives -= 1;
              ship.combo = 1;
              engine.audio.playSound('hit');
              engine.triggerScreenShake(10, 300);
              engine.spawnParticles(ship.x + 25, ship.y + 25, ['#ff0000', '#ffaa00'], 20);
              if (ship.lives <= 0) {{
                gameOver = true;
                engine.audio.playSound('hit');
              }}
            }}
          }}
          meteors.splice(i, 1);
          if (engine.updateHUD) engine.updateHUD({{ lives: Math.max(0, ship.lives), score: ship.score, combo: 'x' + ship.combo }});
          continue;
        }}

        if (m.y > engine.height + 40) {{
          meteors.splice(i, 1);
        }}
      }}
    }},

    draw: function(engine, ctx) {{
      ctx.fillStyle = '#070919';
      ctx.fillRect(0, 0, engine.width, engine.height);

      const radGrad = ctx.createRadialGradient(engine.width / 2, engine.height / 2, 80, engine.width / 2, engine.height / 2, 400);
      radGrad.addColorStop(0, 'rgba(74, 15, 110, 0.45)');
      radGrad.addColorStop(1, 'rgba(7, 9, 25, 0)');
      ctx.fillStyle = radGrad;
      ctx.fillRect(0, 0, engine.width, engine.height);

      // Starfield
      ctx.fillStyle = '#ffffff';
      stars.forEach(s => {{
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.size, 0, Math.PI * 2);
        ctx.fill();
      }});

      // Powerups
      powerups.forEach(p => {{
        ctx.save();
        ctx.font = '28px serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.shadowColor = '#00f0ff';
        ctx.shadowBlur = 12;
        ctx.fillText(p.emoji, p.x, p.y);
        ctx.restore();
      }});

      // Lasers
      ctx.save();
      ctx.fillStyle = ship.doubleLaserTimer > 0 ? '#ffe600' : '#00f0ff';
      ctx.shadowColor = ctx.fillStyle;
      ctx.shadowBlur = 12;
      lasers.forEach(l => {{
        ctx.fillRect(l.x - 3, l.y, 6, 18);
      }});
      ctx.restore();

      // Boss Orbs
      ctx.save();
      ctx.fillStyle = '#ff0055';
      ctx.shadowColor = '#ff0055';
      ctx.shadowBlur = 10;
      bossOrbs.forEach(b => {{
        ctx.beginPath();
        ctx.arc(b.x, b.y, 8, 0, Math.PI * 2);
        ctx.fill();
      }});
      ctx.restore();

      // Boss
      if (boss.active) {{
        ctx.save();
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.font = '64px serif';
        ctx.shadowColor = '#ff0055';
        ctx.shadowBlur = 20;
        ctx.fillText('👾', boss.x, boss.y);
        ctx.restore();
      }}

      // Meteors
      meteors.forEach(m => {{
        ctx.save();
        ctx.translate(m.x, m.y);
        ctx.rotate(m.rotation);
        ctx.font = '36px serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(m.emoji, 0, 0);
        ctx.restore();
      }});

      // Ship & Shield Aura
      ctx.save();
      if (ship.shieldTimer > 0) {{
        ctx.strokeStyle = '#00f0ff';
        ctx.lineWidth = 3;
        ctx.shadowColor = '#00f0ff';
        ctx.shadowBlur = 15;
        ctx.beginPath();
        ctx.arc(ship.x + 25, ship.y + 20, 36, 0, Math.PI * 2);
        ctx.stroke();
      }}

      ctx.fillStyle = Math.random() > 0.5 ? '#ff9900' : '#ffe600';
      ctx.beginPath();
      ctx.arc(ship.x + 25, ship.y + 35, 8 + Math.random() * 4, 0, Math.PI * 2);
      ctx.fill();

      ctx.font = '46px serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(ship.emoji, ship.x + 25, ship.y + 20);
      ctx.restore();

      if (gameOver) {{
        ctx.fillStyle = 'rgba(10, 10, 30, 0.88)';
        ctx.fillRect(0, 0, engine.width, engine.height);
        ctx.fillStyle = '#ff0055';
        ctx.font = 'bold 36px Fredoka, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('💥 GAME OVER!', engine.width / 2, engine.height / 2 - 20);
        ctx.fillStyle = '#ffffff';
        ctx.font = '20px Fredoka, sans-serif';
        ctx.fillText('સ્પેસબાર અથવા સ્ક્રીન પર ટેપ કરીને ફરી રમો! 🚀', engine.width / 2, engine.height / 2 + 25);
      }}

      if (victory) {{
        ctx.fillStyle = 'rgba(10, 10, 30, 0.88)';
        ctx.fillRect(0, 0, engine.width, engine.height);
        ctx.fillStyle = '#ffe600';
        ctx.font = 'bold 38px Fredoka, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('🏆 VICTORY! ALIEN BOSS DEFEATED!', engine.width / 2, engine.height / 2 - 20);
        ctx.fillStyle = '#00f0ff';
        ctx.font = '20px Fredoka, sans-serif';
        ctx.fillText('તમે ગેલેક્સી જીતી લીધી! સ્પેસબાર દબાવી ફરી રમો! 🚀', engine.width / 2, engine.height / 2 + 25);
      }}
    }}
  }};
}};
'''

def _generate_code_candy_catcher(p_emoji: str, c_emoji: str, o_emoji: str) -> str:
    return f'''
window.createGameInstance = function() {{
  let basket = {{
    x: 360,
    y: 410,
    w: 80,
    h: 50,
    speed: 480,
    lives: 3,
    score: 0,
    combo: 1,
    magnetTimer: 0,
    emoji: '{p_emoji}'
  }};

  let items = [];
  let spawnTimer = 0;
  let gameOver = false;
  const sweetEmojis = ['{c_emoji}', '🍩', '🍬', '🍭', '🧁', '🍓'];

  return {{
    init: function(engine) {{
      basket.x = engine.width / 2 - 40;
      basket.y = engine.height - 85;
      basket.lives = 3;
      basket.score = 0;
      basket.combo = 1;
      basket.magnetTimer = 0;
      items = [];
      gameOver = false;
      if (engine.updateHUD) {{
        engine.updateHUD({{ score: basket.score, lives: basket.lives, combo: 'x' + basket.combo, activePowerup: null }});
      }}
    }},

    update: function(engine, dt) {{
      if (gameOver) {{
        if (engine.input.keys.space || engine.input.keys.action) this.init(engine);
        return;
      }}

      if (engine.input.keys.left) basket.x -= basket.speed * dt;
      if (engine.input.keys.right) basket.x += basket.speed * dt;
      basket.x = Math.max(10, Math.min(engine.width - basket.w - 10, basket.x));

      // Magnet timer & HUD
      if (basket.magnetTimer > 0) {{
        basket.magnetTimer -= dt;
        if (engine.updateHUD) {{
          engine.updateHUD({{ activePowerup: {{ emoji: '🧲', text: Math.ceil(basket.magnetTimer) + 's MAGNET' }} }});
        }}
      }} else if (engine.updateHUD && basket.magnetTimer <= 0) {{
        engine.updateHUD({{ activePowerup: null }});
      }}

      spawnTimer += dt;
      if (spawnTimer > 0.68) {{
        spawnTimer = 0;
        const rand = Math.random();
        let emoji = sweetEmojis[Math.floor(Math.random() * sweetEmojis.length)];
        let isBomb = false;
        let isMagnet = false;
        let isGolden = false;

        if (rand < 0.18) {{
          isBomb = true;
          emoji = '{o_emoji}';
        }} else if (rand < 0.28) {{
          isMagnet = true;
          emoji = '🧲';
        }} else if (rand < 0.38) {{
          isGolden = true;
          emoji = '🧁';
        }}

        items.push({{
          x: Math.random() * (engine.width - 80) + 40,
          y: -30,
          vy: Math.random() * 110 + 170,
          emoji: emoji,
          isBomb: isBomb,
          isMagnet: isMagnet,
          isGolden: isGolden,
          bob: Math.random() * Math.PI
        }});
      }}

      for (let i = items.length - 1; i >= 0; i--) {{
        const it = items[i];
        it.y += it.vy * dt;
        it.bob += dt * 4;

        // Magnet attraction
        if (basket.magnetTimer > 0 && !it.isBomb) {{
          const targetX = basket.x + basket.w / 2;
          it.x += (targetX - it.x) * 4.5 * dt;
        }}

        if (it.y > basket.y - 20 && it.y < basket.y + 40) {{
          if (it.x > basket.x - 20 && it.x < basket.x + basket.w + 20) {{
            if (it.isBomb) {{
              basket.lives -= 1;
              basket.combo = 1;
              engine.audio.playSound('hit');
              engine.triggerScreenShake(12, 300);
              engine.spawnParticles(it.x, it.y, ['#ff0055', '#ff9900'], 18);
              if (basket.lives <= 0) gameOver = true;
            }} else if (it.isMagnet) {{
              basket.magnetTimer = 8;
              engine.audio.playSound('powerup');
              engine.spawnScorePopup(it.x, it.y, '🧲 MAGNET ACTIVE! (8s)', '#00f0ff');
              engine.spawnParticles(it.x, it.y, ['#00f0ff', '#ffe600'], 16);
            }} else {{
              const pts = (it.isGolden ? 500 : 100) * basket.combo;
              basket.score += pts;
              basket.combo = Math.min(basket.combo + 1, 10);
              engine.audio.playSound(it.isGolden ? 'win' : 'coin');
              engine.spawnParticles(it.x, it.y, ['#ff007a', '#ffe600', '#00f0ff', '#ffffff'], 14);
              engine.spawnScorePopup(it.x, it.y, '+' + pts, it.isGolden ? '#ffe600' : '#ff007a');
            }}
            items.splice(i, 1);
            if (engine.updateHUD) engine.updateHUD({{ score: basket.score, lives: Math.max(0, basket.lives), combo: 'x' + basket.combo }});
            continue;
          }}
        }}

        if (it.y > engine.height + 20) {{
          if (!it.isBomb && !it.isMagnet) {{
            basket.combo = 1;
            if (engine.updateHUD) engine.updateHUD({{ combo: 'x1' }});
          }}
          items.splice(i, 1);
        }}
      }}
    }},

    draw: function(engine, ctx) {{
      const grad = ctx.createLinearGradient(0, 0, 0, engine.height);
      grad.addColorStop(0, '#2d0a4e');
      grad.addColorStop(0.6, '#6b117b');
      grad.addColorStop(1, '#ff4d88');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, engine.width, engine.height);

      ctx.fillStyle = 'rgba(255, 255, 255, 0.15)';
      for (let i = 0; i < 6; i++) {{
        ctx.beginPath();
        ctx.arc(i * 160 + 50, engine.height - 30, 90, 0, Math.PI * 2);
        ctx.fill();
      }}

      items.forEach(it => {{
        ctx.font = '38px serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(it.emoji, it.x + Math.sin(it.bob) * 6, it.y);
      }});

      ctx.fillStyle = '#ff007a';
      ctx.fillRect(0, engine.height - 20, engine.width, 20);

      ctx.save();
      if (basket.magnetTimer > 0) {{
        ctx.strokeStyle = 'rgba(0, 240, 255, 0.7)';
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.arc(basket.x + basket.w / 2, basket.y + 25, 45 + Math.sin(Date.now() / 120) * 5, 0, Math.PI * 2);
        ctx.stroke();
      }}
      ctx.font = '50px serif';
      ctx.textAlign = 'center';
      ctx.fillText(basket.emoji, basket.x + basket.w / 2, basket.y + 35);
      ctx.restore();

      if (gameOver) {{
        ctx.fillStyle = 'rgba(20, 0, 30, 0.85)';
        ctx.fillRect(0, 0, engine.width, engine.height);
        ctx.fillStyle = '#ffe600';
        ctx.font = 'bold 36px Fredoka, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('🎉 સ્કોર: ' + basket.score + ' પોઇન્ટ્સ!', engine.width / 2, engine.height / 2 - 20);
        ctx.fillStyle = '#ffffff';
        ctx.font = '20px Fredoka, sans-serif';
        ctx.fillText('ફરી રમવા સ્પેસબાર અથવા ટેપ કરો! 🍭', engine.width / 2, engine.height / 2 + 25);
      }}
    }}
  }};
}};
'''

def _generate_code_cartoon_racer(p_emoji: str, c_emoji: str, o_emoji: str) -> str:
    return f'''
window.createGameInstance = function() {{
  const lanes = [200, 330, 470, 600];
  let car = {{
    laneIndex: 1,
    targetX: 330,
    x: 330,
    y: 380,
    lives: 3,
    score: 0,
    combo: 1,
    turbo: false,
    turboTimer: 0,
    emoji: '{p_emoji}'
  }};

  let obstacles = [];
  let roadLines = [];
  let spawnTimer = 0;
  let gameOver = false;

  return {{
    init: function(engine) {{
      car.laneIndex = 1;
      car.x = lanes[car.laneIndex];
      car.targetX = car.x;
      car.y = engine.height - 110;
      car.lives = 3;
      car.score = 0;
      car.combo = 1;
      car.turbo = false;
      car.turboTimer = 0;
      obstacles = [];
      roadLines = [];
      for (let i = 0; i < 8; i++) roadLines.push(i * 70);
      gameOver = false;
      if (engine.updateHUD) {{
        engine.updateHUD({{ score: car.score, lives: car.lives, combo: 'x' + car.combo }});
      }}
    }},

    update: function(engine, dt) {{
      if (gameOver) {{
        if (engine.input.keys.space || engine.input.keys.action) this.init(engine);
        return;
      }}

      if (engine.input.keys.left && car.laneIndex > 0) {{
        car.laneIndex--;
        car.targetX = lanes[car.laneIndex];
        engine.input.keys.left = false;
        engine.audio.playSound('jump');
      }}
      if (engine.input.keys.right && car.laneIndex < lanes.length - 1) {{
        car.laneIndex++;
        car.targetX = lanes[car.laneIndex];
        engine.input.keys.right = false;
        engine.audio.playSound('jump');
      }}

      car.x += (car.targetX - car.x) * 16 * dt;

      if ((engine.input.keys.up || engine.input.keys.space) && car.turboTimer <= 0) {{
        car.turbo = true;
        car.turboTimer = 3.5;
        engine.audio.playSound('powerup');
        engine.triggerScreenShake(4, 200);
        if (engine.updateHUD) engine.updateHUD({{ activePowerup: {{ emoji: '⚡', text: '3.5s NITRO BOOST' }} }});
      }}

      const speedMult = car.turbo ? 2.0 : 1.0;
      car.score += Math.round(dt * 30 * speedMult);

      if (car.turbo) {{
        car.turboTimer -= dt;
        engine.spawnParticles(car.x, car.y + 40, ['#00f0ff', '#ffe600', '#ff0055'], 3);
        if (engine.updateHUD && Math.random() < 0.25) {{
          engine.updateHUD({{ activePowerup: {{ emoji: '⚡', text: Math.ceil(car.turboTimer) + 's NITRO BOOST' }} }});
        }}
        if (car.turboTimer <= 0) {{
          car.turbo = false;
          if (engine.updateHUD) engine.updateHUD({{ activePowerup: null }});
        }}
      }}

      for (let i = 0; i < roadLines.length; i++) {{
        roadLines[i] += 400 * speedMult * dt;
        if (roadLines[i] > engine.height) roadLines[i] = -70;
      }}

      spawnTimer += dt;
      if (spawnTimer > (car.turbo ? 0.45 : 0.75)) {{
        spawnTimer = 0;
        const targetLane = Math.floor(Math.random() * lanes.length);
        const isCoin = Math.random() < 0.35;
        obstacles.push({{
          x: lanes[targetLane],
          y: -50,
          isCoin: isCoin,
          emoji: isCoin ? '{c_emoji}' : '{o_emoji}',
          vy: (isCoin ? 280 : 330) * speedMult
        }});
      }}

      for (let i = obstacles.length - 1; i >= 0; i--) {{
        const ob = obstacles[i];
        ob.y += ob.vy * dt;

        if (Math.hypot(ob.x - car.x, ob.y - car.y) < 45) {{
          if (ob.isCoin) {{
            const pts = 150 * car.combo;
            car.score += pts;
            car.combo = Math.min(car.combo + 1, 6);
            engine.audio.playSound('coin');
            engine.spawnParticles(ob.x, ob.y, ['#ffe600', '#ff9900'], 12);
            engine.spawnScorePopup(ob.x, ob.y, '+' + pts, '#ffe600');
          }} else {{
            car.lives -= 1;
            car.combo = 1;
            car.turbo = false;
            car.turboTimer = 0;
            if (engine.updateHUD) engine.updateHUD({{ activePowerup: null }});
            engine.audio.playSound('hit');
            engine.triggerScreenShake(12, 350);
            engine.spawnParticles(car.x, car.y, ['#ff0055', '#ff9900', '#ffffff'], 20);
            if (car.lives <= 0) gameOver = true;
          }}
          obstacles.splice(i, 1);
          if (engine.updateHUD) engine.updateHUD({{ score: car.score, lives: Math.max(0, car.lives), combo: 'x' + car.combo }});
          continue;
        }}

        if (ob.y > engine.height + 50) obstacles.splice(i, 1);
      }}

      if (engine.updateHUD && Math.random() < 0.1) {{
        engine.updateHUD({{ score: car.score, combo: 'x' + car.combo }});
      }}
    }},

    draw: function(engine, ctx) {{
      ctx.fillStyle = '#1b5e20';
      ctx.fillRect(0, 0, engine.width, engine.height);

      ctx.fillStyle = '#263238';
      ctx.fillRect(130, 0, engine.width - 260, engine.height);

      ctx.fillStyle = '#ff1744';
      ctx.fillRect(130, 0, 10, engine.height);
      ctx.fillRect(engine.width - 140, 0, 10, engine.height);

      ctx.fillStyle = '#ffffff';
      [265, 400, 535].forEach(lx => {{
        roadLines.forEach(ly => {{
          ctx.fillRect(lx - 4, ly, 8, 40);
        }});
      }});

      obstacles.forEach(ob => {{
        ctx.font = '40px serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(ob.emoji, ob.x, ob.y);
      }});

      ctx.save();
      ctx.font = '52px serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      if (car.turbo) {{
        ctx.shadowColor = '#00f0ff';
        ctx.shadowBlur = 20;
      }}
      ctx.fillText(car.emoji, car.x, car.y);
      ctx.restore();

      if (car.turbo) {{
        ctx.fillStyle = '#00f0ff';
        ctx.font = 'bold 20px Fredoka, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('⚡ TURBO BOOST ACTIVATED! ⚡', engine.width / 2, 40);
      }}

      if (gameOver) {{
        ctx.fillStyle = 'rgba(10, 15, 25, 0.88)';
        ctx.fillRect(0, 0, engine.width, engine.height);
        ctx.fillStyle = '#ffe600';
        ctx.font = 'bold 36px Fredoka, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('🏁 રેસ પૂરી! સ્કોર: ' + car.score, engine.width / 2, engine.height / 2 - 20);
        ctx.fillStyle = '#ffffff';
        ctx.font = '20px Fredoka, sans-serif';
        ctx.fillText('ફરી રમવા સ્પેસબાર અથવા સ્ક્રીન પર ટેપ કરો! 🏎️', engine.width / 2, engine.height / 2 + 25);
      }}
    }}
  }};
}};
'''

def _generate_code_maze_adventure(p_emoji: str, c_emoji: str, o_emoji: str) -> str:
    return f'''
window.createGameInstance = function() {{
  let player = {{
    x: 80,
    y: 80,
    size: 36,
    speed: 220,
    keysCollected: 0,
    score: 0,
    emoji: '{p_emoji}'
  }};

  const walls = [
    {{ x: 180, y: 0, w: 20, h: 220 }},
    {{ x: 180, y: 300, w: 20, h: 200 }},
    {{ x: 360, y: 120, w: 20, h: 260 }},
    {{ x: 540, y: 0, w: 20, h: 200 }},
    {{ x: 540, y: 280, w: 20, h: 220 }},
    {{ x: 180, y: 220, w: 200, h: 20 }},
    {{ x: 360, y: 360, w: 200, h: 20 }}
  ];

  let keys = [];
  let ghost = {{ x: 450, y: 150, vx: 140, vy: 110, emoji: '{o_emoji}' }};
  const exitPortal = {{ x: 720, y: 250, size: 50, unlocked: false }};
  let winState = false;

  return {{
    init: function(engine) {{
      player.x = 70;
      player.y = 70;
      player.keysCollected = 0;
      player.score = 0;
      winState = false;
      exitPortal.unlocked = false;
      ghost.x = 450;
      ghost.y = 150;
      keys = [
        {{ x: 100, y: 420, collected: false }},
        {{ x: 280, y: 140, collected: false }},
        {{ x: 640, y: 80, collected: false }}
      ];
      if (engine.updateHUD) {{
        engine.updateHUD({{ score: player.score, lives: 3, combo: 'ચાવી: 0/3' }});
      }}
    }},

    update: function(engine, dt) {{
      if (winState) {{
        if (engine.input.keys.space || engine.input.keys.action) this.init(engine);
        return;
      }}

      let nextX = player.x;
      let nextY = player.y;
      if (engine.input.keys.left) nextX -= player.speed * dt;
      if (engine.input.keys.right) nextX += player.speed * dt;
      if (engine.input.keys.up) nextY -= player.speed * dt;
      if (engine.input.keys.down) nextY += player.speed * dt;

      nextX = Math.max(30, Math.min(engine.width - 40, nextX));
      nextY = Math.max(30, Math.min(engine.height - 40, nextY));

      let collideX = false;
      let collideY = false;
      walls.forEach(w => {{
        if (nextX + 15 > w.x && nextX - 15 < w.x + w.w && player.y + 15 > w.y && player.y - 15 < w.y + w.h) collideX = true;
        if (player.x + 15 > w.x && player.x - 15 < w.x + w.w && nextY + 15 > w.y && nextY - 15 < w.y + w.h) collideY = true;
      }});

      if (!collideX) player.x = nextX;
      if (!collideY) player.y = nextY;

      keys.forEach((k, idx) => {{
        if (!k.collected && Math.hypot(player.x - k.x, player.y - k.y) < 36) {{
          k.collected = true;
          player.keysCollected++;
          player.score += 250;
          engine.audio.playSound('coin');
          engine.spawnParticles(k.x, k.y, ['#ffe600', '#ff9900', '#ffffff'], 15);
          engine.spawnScorePopup(k.x, k.y, '+250 🔑', '#ffe600');
          if (player.keysCollected >= 3) {{
            exitPortal.unlocked = true;
            engine.audio.playSound('powerup');
            engine.spawnScorePopup(exitPortal.x, exitPortal.y, '🚪 પોર્ટલ ખૂલી ગયું!', '#00f0ff');
          }}
          if (engine.updateHUD) engine.updateHUD({{ score: player.score, combo: 'ચાવી: ' + player.keysCollected + '/3' }});
        }}
      }});

      ghost.x += ghost.vx * dt;
      ghost.y += ghost.vy * dt;
      if (ghost.x < 220 || ghost.x > 500) ghost.vx *= -1;
      if (ghost.y < 50 || ghost.y > 450) ghost.vy *= -1;

      if (Math.hypot(player.x - ghost.x, player.y - ghost.y) < 32) {{
        engine.audio.playSound('hit');
        engine.triggerScreenShake(8, 250);
        player.x = 70;
        player.y = 70;
      }}

      if (exitPortal.unlocked && Math.hypot(player.x - exitPortal.x, player.y - exitPortal.y) < 40) {{
        winState = true;
        engine.audio.playSound('win');
        engine.spawnParticles(exitPortal.x, exitPortal.y, ['#00f0ff', '#ffe600', '#ff007a'], 30);
      }}
    }},

    draw: function(engine, ctx) {{
      ctx.fillStyle = '#0f172a';
      ctx.fillRect(0, 0, engine.width, engine.height);

      ctx.fillStyle = '#334155';
      ctx.strokeStyle = '#64748b';
      ctx.lineWidth = 3;
      walls.forEach(w => {{
        ctx.fillRect(w.x, w.y, w.w, w.h);
        ctx.strokeRect(w.x, w.y, w.w, w.h);
      }});

      keys.forEach(k => {{
        if (!k.collected) {{
          ctx.font = '32px serif';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText('{c_emoji}', k.x, k.y);
        }}
      }});

      ctx.save();
      ctx.font = '44px serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      if (exitPortal.unlocked) {{
        ctx.shadowColor = '#00f0ff';
        ctx.shadowBlur = 18;
      }}
      ctx.fillText(exitPortal.unlocked ? '🏆' : '🚪', exitPortal.x, exitPortal.y);
      ctx.restore();

      ctx.font = '38px serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(ghost.emoji, ghost.x, ghost.y);

      ctx.font = '42px serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(player.emoji, player.x, player.y);

      if (winState) {{
        ctx.fillStyle = 'rgba(15, 23, 42, 0.9)';
        ctx.fillRect(0, 0, engine.width, engine.height);
        ctx.fillStyle = '#ffe600';
        ctx.font = 'bold 36px Fredoka, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('🎉 અદ્ભુત વિજય! મેઇઝ જીતી ગયા!', engine.width / 2, engine.height / 2 - 20);
        ctx.fillStyle = '#ffffff';
        ctx.font = '20px Fredoka, sans-serif';
        ctx.fillText('ફરી રમવા સ્પેસબાર દબાવો! 🗝️', engine.width / 2, engine.height / 2 + 25);
      }}
    }}
  }};
}};
'''

def _generate_code_bubble_popper(p_emoji: str, c_emoji: str, o_emoji: str) -> str:
    return f'''
window.createGameInstance = function() {{
  let bubbles = [];
  let score = 0;
  let combo = 1;
  let spawnTimer = 0;
  let waveTimer = 0;

  const bubbleColors = [
    {{ bg: 'rgba(0, 240, 255, 0.65)', border: '#00f0ff', pts: 100 }},
    {{ bg: 'rgba(255, 0, 122, 0.65)', border: '#ff007a', pts: 150 }},
    {{ bg: 'rgba(255, 230, 0, 0.65)', border: '#ffe600', pts: 200 }},
    {{ bg: 'rgba(0, 230, 118, 0.65)', border: '#00e676', pts: 250 }}
  ];

  return {{
    init: function(engine) {{
      bubbles = [];
      score = 0;
      combo = 1;
      spawnTimer = 0;
      for (let i = 0; i < 14; i++) {{
        const col = bubbleColors[Math.floor(Math.random() * bubbleColors.length)];
        bubbles.push({{
          x: Math.random() * (engine.width - 120) + 60,
          y: Math.random() * (engine.height - 100) + 50,
          radius: Math.random() * 20 + 26,
          vy: -(Math.random() * 50 + 40),
          col: col,
          wobble: Math.random() * Math.PI,
          emoji: Math.random() < 0.25 ? '{c_emoji}' : ''
        }});
      }}
      if (engine.updateHUD) {{
        engine.updateHUD({{ score: score, lives: 3, combo: 'x1' }});
      }}
    }},

    popAt: function(engine, x, y, radius = 40) {{
      let poppedAny = false;
      for (let i = bubbles.length - 1; i >= 0; i--) {{
        const b = bubbles[i];
        if (Math.hypot(b.x - x, b.y - y) <= b.radius + radius) {{
          poppedAny = true;
          const pts = b.col.pts * combo;
          score += pts;
          combo = Math.min(combo + 1, 12);
          engine.audio.playSound('coin');
          engine.spawnParticles(b.x, b.y, [b.col.border, '#ffffff', '#ffe600'], 14);
          engine.spawnScorePopup(b.x, b.y, '+' + pts, b.col.border);
          bubbles.splice(i, 1);
        }}
      }}
      if (poppedAny && engine.updateHUD) {{
        engine.updateHUD({{ score: score, combo: 'x' + combo }});
      }}
      return poppedAny;
    }},

    update: function(engine, dt) {{
      if (engine.input.pointer && engine.input.pointer.isDown) {{
        this.popAt(engine, engine.input.pointer.x, engine.input.pointer.y, 25);
      }}

      if (engine.input.keys.space || engine.input.keys.action) {{
        waveTimer = 0.3;
        engine.audio.playSound('powerup');
        engine.triggerScreenShake(6, 200);
        this.popAt(engine, engine.width / 2, engine.height / 2, 280);
        engine.input.keys.space = false;
        engine.input.keys.action = false;
      }}

      if (waveTimer > 0) waveTimer -= dt;

      spawnTimer += dt;
      if (spawnTimer > 0.6) {{
        spawnTimer = 0;
        const col = bubbleColors[Math.floor(Math.random() * bubbleColors.length)];
        bubbles.push({{
          x: Math.random() * (engine.width - 120) + 60,
          y: engine.height + 40,
          radius: Math.random() * 20 + 26,
          vy: -(Math.random() * 60 + 50),
          col: col,
          wobble: Math.random() * Math.PI,
          emoji: Math.random() < 0.3 ? '{c_emoji}' : ''
        }});
      }}

      for (let i = bubbles.length - 1; i >= 0; i--) {{
        const b = bubbles[i];
        b.y += b.vy * dt;
        b.wobble += dt * 3;
        b.x += Math.sin(b.wobble) * 25 * dt;

        if (b.y < -50) {{
          bubbles.splice(i, 1);
          combo = 1;
        }}
      }}
    }},

    draw: function(engine, ctx) {{
      const grad = ctx.createLinearGradient(0, 0, 0, engine.height);
      grad.addColorStop(0, '#0a192f');
      grad.addColorStop(1, '#0e3a53');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, engine.width, engine.height);

      if (waveTimer > 0) {{
        ctx.save();
        ctx.beginPath();
        ctx.arc(engine.width / 2, engine.height / 2, (0.3 - waveTimer) * 900, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(0, 240, 255, 0.7)';
        ctx.lineWidth = 6;
        ctx.stroke();
        ctx.restore();
      }}

      bubbles.forEach(b => {{
        ctx.save();
        ctx.beginPath();
        ctx.arc(b.x, b.y, b.radius, 0, Math.PI * 2);
        ctx.fillStyle = b.col.bg;
        ctx.fill();
        ctx.lineWidth = 3;
        ctx.strokeStyle = b.col.border;
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(b.x - b.radius * 0.35, b.y - b.radius * 0.35, b.radius * 0.25, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
        ctx.fill();

        if (b.emoji) {{
          ctx.font = (b.radius * 0.9) + 'px serif';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(b.emoji, b.x, b.y);
        }}
        ctx.restore();
      }});

      ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
      ctx.font = '16px Fredoka, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('પરપોટા ફોડવા માટે ક્લિક અથવા ટેપ કરો! 🫧', engine.width / 2, engine.height - 20);
    }}
  }};
}};
'''

def _generate_code_platformer(p_emoji: str, c_emoji: str, o_emoji: str) -> str:
    return f'''
window.createGameInstance = function() {{
  let hero = {{
    x: 100,
    y: 350,
    w: 50,
    h: 50,
    vy: 0,
    isJumping: false,
    speed: 320,
    lives: 3,
    score: 0,
    combo: 1,
    emoji: '{p_emoji}'
  }};

  let items = [];
  let groundY = 410;
  let platforms = [
    {{ x: 220, y: 310, w: 120, h: 18 }},
    {{ x: 420, y: 230, w: 130, h: 18 }},
    {{ x: 620, y: 310, w: 120, h: 18 }}
  ];
  let spawnTimer = 0;
  let gameOver = false;

  return {{
    init: function(engine) {{
      hero.x = 100;
      hero.y = groundY - hero.h;
      hero.vy = 0;
      hero.isJumping = false;
      hero.lives = 3;
      hero.score = 0;
      hero.combo = 1;
      gameOver = false;
      items = [];
      for (let i = 0; i < 4; i++) {{
        items.push({{
          x: 240 + i * 140,
          y: groundY - 60 - Math.sin(i) * 90,
          emoji: '{c_emoji}',
          bob: Math.random() * Math.PI
        }});
      }}
      if (engine.updateHUD) {{
        engine.updateHUD({{ score: hero.score, lives: hero.lives, combo: 'x' + hero.combo }});
      }}
    }},

    update: function(engine, dt) {{
      if (gameOver) {{
        if (engine.input.keys.space || engine.input.keys.action) this.init(engine);
        return;
      }}

      if (engine.input.keys.left) hero.x -= hero.speed * dt;
      if (engine.input.keys.right) hero.x += hero.speed * dt;
      hero.x = Math.max(20, Math.min(engine.width - hero.w - 20, hero.x));

      if ((engine.input.keys.space || engine.input.keys.up) && !hero.isJumping) {{
        hero.vy = -600;
        hero.isJumping = true;
        engine.audio.playSound('jump');
        engine.spawnParticles(hero.x + 25, hero.y + 45, ['#ff007a', '#ffe600', '#00f0ff'], 10);
      }}

      hero.vy += 1250 * dt;
      hero.y += hero.vy * dt;

      let onPlatform = false;
      platforms.forEach(pl => {{
        if (hero.vy >= 0 &&
            hero.x + hero.w * 0.7 > pl.x &&
            hero.x + hero.w * 0.3 < pl.x + pl.w &&
            hero.y + hero.h >= pl.y &&
            hero.y + hero.h <= pl.y + 22) {{
          hero.y = pl.y - hero.h;
          hero.vy = 0;
          hero.isJumping = false;
          onPlatform = true;
        }}
      }});

      if (!onPlatform && hero.y >= groundY - hero.h) {{
        hero.y = groundY - hero.h;
        hero.vy = 0;
        hero.isJumping = false;
      }}

      spawnTimer += dt;
      if (spawnTimer > 2.0) {{
        spawnTimer = 0;
        items.push({{
          x: engine.width + 30,
          y: groundY - 40 - Math.random() * 140,
          emoji: Math.random() < 0.7 ? '{c_emoji}' : '⭐',
          bob: 0
        }});
      }}

      for (let i = items.length - 1; i >= 0; i--) {{
        const it = items[i];
        it.x -= 120 * dt;
        it.bob += dt * 4;

        if (Math.hypot((hero.x + 25) - it.x, (hero.y + 25) - (it.y + Math.sin(it.bob) * 8)) < 42) {{
          hero.score += 150;
          engine.audio.playSound('coin');
          engine.spawnParticles(it.x, it.y, ['#ff4d4d', '#ffb84d', '#ffff4d', '#4da6ff'], 14);
          engine.spawnScorePopup(it.x, it.y, '+150', '#ffe600');
          items.splice(i, 1);
          if (engine.updateHUD) engine.updateHUD({{ score: hero.score }});
        }} else if (it.x < -40) {{
          items.splice(i, 1);
        }}
      }}
    }},

    draw: function(engine, ctx) {{
      const grad = ctx.createLinearGradient(0, 0, 0, engine.height);
      grad.addColorStop(0, '#1a103c');
      grad.addColorStop(0.7, '#441666');
      grad.addColorStop(1, '#ff4081');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, engine.width, engine.height);

      ctx.fillStyle = '#00e676';
      platforms.forEach(pl => {{
        ctx.fillRect(pl.x, pl.y, pl.w, pl.h);
        ctx.fillStyle = '#ff007a';
        ctx.fillRect(pl.x, pl.y + 4, pl.w, 4);
        ctx.fillStyle = '#00e676';
      }});

      ctx.fillStyle = '#00c853';
      ctx.fillRect(0, groundY, engine.width, engine.height - groundY);
      ctx.fillStyle = '#ff007a';
      ctx.fillRect(0, groundY + 8, engine.width, 6);

      items.forEach(it => {{
        ctx.font = '36px serif';
        ctx.textAlign = 'center';
        ctx.fillText(it.emoji, it.x, it.y + Math.sin(it.bob) * 8);
      }});

      ctx.save();
      ctx.font = '46px serif';
      ctx.textAlign = 'center';
      ctx.fillText(hero.emoji, hero.x + 25, hero.y + 40);
      ctx.restore();
    }}
  }};
}};
'''

def synthesize_game_for_prompt(prompt: str, language: str = "gu-IN", skills_summary: str = "") -> Dict[str, Any]:
    genre = classify_genre(prompt)
    theme_info = _extract_theme_details(prompt, genre, language)

    p_emoji = theme_info["player_emoji"]
    c_emoji = theme_info["collectible_emoji"]
    o_emoji = theme_info["obstacle_emoji"]

    generators = {
        GENRE_SPACE_SHOOTER: _generate_code_space_shooter,
        GENRE_CANDY_CATCHER: _generate_code_candy_catcher,
        GENRE_CARTOON_RACER: _generate_code_cartoon_racer,
        GENRE_MAZE_ADVENTURE: _generate_code_maze_adventure,
        GENRE_BUBBLE_POPPER: _generate_code_bubble_popper,
        GENRE_PLATFORMER: _generate_code_platformer
    }

    gen_func = generators.get(genre, _generate_code_platformer)
    game_code = gen_func(p_emoji, c_emoji, o_emoji)

    skill_id = f"custom_mechanic_{genre}"
    skill_names = {
        GENRE_SPACE_SHOOTER: "Space Laser Starfighter Engine",
        GENRE_CANDY_CATCHER: "High-Speed Basket Physics Catcher",
        GENRE_CARTOON_RACER: "Multi-Lane Nitro Turbo Racer",
        GENRE_MAZE_ADVENTURE: "Dungeon Key & Portal Explorer",
        GENRE_BUBBLE_POPPER: "Dynamic Sonic Wave Bubble Physics",
        GENRE_PLATFORMER: "Bouncy Spring Platformer Hero"
    }

    return {
        "title": theme_info["title"],
        "genre": genre,
        "spoken_response": theme_info["spoken_response"],
        "theme": {
            "background_gradient": theme_info["bg_gradient"],
            "accent_color": theme_info["accent"],
            "css_class": theme_info["css_class"],
            "player_emoji": p_emoji,
            "collectible_emoji": c_emoji,
            "obstacle_emoji": o_emoji,
            "hud_html": theme_info["hud_html"]
        },
        "instructions": theme_info["instructions"],
        "html_hud_overlay": theme_info["hud_html"],
        "game_code": game_code.strip(),
        "new_skill_learned": {
            "id": skill_id,
            "name": skill_names.get(genre, "Arcade Custom Mechanic"),
            "description": f"Mastered {genre} mechanics with custom HTML HUD and 60fps loop"
        }
    }
