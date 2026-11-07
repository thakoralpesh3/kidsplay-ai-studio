#!/usr/bin/env python3
"""
Exports Python game synthesizer generators into static/js/game_synthesizer.js
Enables 100% standalone, serverless, zero-latency execution directly on GitHub Pages!
"""

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY_SYNTH = ROOT / "server" / "game_synthesizer.py"
JS_OUT = ROOT / "static" / "js" / "game_synthesizer.js"

with open(PY_SYNTH, "r", encoding="utf-8") as f:
    py_code = f.read()

def extract_generator_body(func_name: str) -> str:
    pattern = rf"def {func_name}\([^)]*\)\s*->\s*str:\s*return\s*f'''(.*?)'''\s*(?=def |\Z)"
    match = re.search(pattern, py_code, re.DOTALL)
    if not match:
        raise ValueError(f"Could not extract {func_name}")
    body = match.group(1)
    # Convert Python f-string escaping to JS template literal
    # 1. Replace placeholder variables with ${var}
    body = body.replace("{p_emoji}", "${p_emoji}")
    body = body.replace("{c_emoji}", "${c_emoji}")
    body = body.replace("{o_emoji}", "${o_emoji}")
    # 2. Unescape {{ and }} to { and }
    body = body.replace("{{", "{").replace("}}", "}")
    # 3. Escape backticks if any
    body = body.replace("`", "\\`")
    return body

space_code = extract_generator_body("_generate_code_space_shooter")
candy_code = extract_generator_body("_generate_code_candy_catcher")
racer_code = extract_generator_body("_generate_code_cartoon_racer")
maze_code = extract_generator_body("_generate_code_maze_adventure")
bubble_code = extract_generator_body("_generate_code_bubble_popper")
platformer_code = extract_generator_body("_generate_code_platformer")

js_template = f'''/**
 * KidsPlay AI Studio • Client-Side Universal Game Synthesizer
 * ============================================================
 * 100% Standalone & Serverless: Runs directly in browser on GitHub Pages, mobile, tablet & PC!
 * Features:
 * - Zero-Latency (<5ms) game synthesis across 6 core kid-favorite genres.
 * - Alien Titan Boss battles with animated in-game HUD boss HP bar.
 * - Collectible powerup drops (Shield 🛡️, Dual-Laser ⚡⚡, Magnet 🧲, Turbo Nitro ⚡).
 * - Multilingual support (Gujarati, Hindi, English).
 */

(function(root) {{
  'use strict';

  const GENRE_SPACE_SHOOTER = 'space_shooter';
  const GENRE_CANDY_CATCHER = 'candy_catcher';
  const GENRE_CARTOON_RACER = 'cartoon_racer';
  const GENRE_MAZE_ADVENTURE = 'maze_adventure';
  const GENRE_BUBBLE_POPPER = 'bubble_pop';
  const GENRE_PLATFORMER = 'platformer';

  function classifyGenre(prompt) {{
    const p = (prompt || '').toLowerCase();
    const space_kw = [
      'સ્પેસ', 'રોકેટ', 'ઉલ્કા', 'એલિયન', 'લેઝર', 'શૂટર', 'શૂટ', 'અંતરિક્ષ', 'તારાઓ',
      'space', 'rocket', 'alien', 'meteor', 'laser', 'shoot', 'shooter', 'galaxy', 'ufo',
      'अंतरिक्ष', 'रॉकेट', 'निशाना'
    ];
    if (space_kw.some(k => p.includes(k))) return GENRE_SPACE_SHOOTER;

    const racer_kw = [
      'કાર', 'રેસિંગ', 'ગાડી', 'ડ્રાઇવ', 'હાઇવે', 'ટર્બો', 'ટ્રાફિક', 'મોટર',
      'car', 'racing', 'racer', 'drive', 'highway', 'traffic', 'turbo', 'speed', 'vehicle',
      'गाड़ी', 'कार', 'रेस', 'दौड़'
    ];
    if (racer_kw.some(k => p.includes(k))) return GENRE_CARTOON_RACER;

    const catcher_kw = [
      'કેન્ડી', 'ડોનટ', 'ફળ', 'ટોપલી', 'પકડવા', 'પકડો', 'આકાશમાંથી', 'ચોકલેટ', 'કેક',
      'catch', 'catcher', 'candy', 'donut', 'fruit', 'basket', 'drop', 'falling', 'sweets',
      'पकड़ना', 'कैंडी', 'फल', 'टोकरी'
    ];
    if (catcher_kw.some(k => p.includes(k))) return GENRE_CANDY_CATCHER;

    const maze_kw = [
      'મેઇઝ', 'ભૂલભુલામણી', 'ચાવી', 'દરવાજો', 'ખજાનો', 'રૂમ', 'દિવાલ',
      'maze', 'labyrinth', 'dungeon', 'key', 'door', 'treasure', 'quest', 'explore',
      'भूलभुलैया', 'चाबी', 'खजाना', 'कमरा'
    ];
    if (maze_kw.some(k => p.includes(k))) return GENRE_MAZE_ADVENTURE;

    const bubble_kw = [
      'બબલ', 'પરપોટા', 'પોપ', 'ફુગ્ગા', 'ક્લિક', 'દડો',
      'bubble', 'pop', 'balloon', 'physics', 'clicker', 'tap', 'burst',
      'गुब्बारा', 'बबल', 'फोड़ना'
    ];
    if (bubble_kw.some(k => p.includes(k))) return GENRE_BUBBLE_POPPER;

    return GENRE_PLATFORMER;
  }}

  function extractThemeDetails(prompt, genre, language) {{
    const p = (prompt || '').toLowerCase();
    const is_gu = (language || 'gu-IN').startsWith('gu');
    const is_hi = (language || '').startsWith('hi');

    let player_emoji = '🦄';
    let collectible_emoji = '⭐';
    let obstacle_emoji = '👾';

    if (p.includes('દેડકો') || p.includes('frog') || p.includes('મેઢક')) {{
      player_emoji = '🐸'; collectible_emoji = '🪰'; obstacle_emoji = '🐊';
    }} else if (p.includes('ડાયનાસોર') || p.includes('dino') || p.includes('dinosaur')) {{
      player_emoji = '🦖'; collectible_emoji = '🍖'; obstacle_emoji = '🌋';
    }} else if (p.includes('સુપરહીરો') || p.includes('superhero') || p.includes('hero')) {{
      player_emoji = '🦸'; collectible_emoji = '💎'; obstacle_emoji = '⚡';
    }} else if (p.includes('સસલું') || p.includes('bunny') || p.includes('rabbit')) {{
      player_emoji = '🐰'; collectible_emoji = '🥕'; obstacle_emoji = '🕳️';
    }} else if (p.includes('બિલાડી') || p.includes('cat') || p.includes('kitty')) {{
      player_emoji = '🐱'; collectible_emoji = '🐟'; obstacle_emoji = '🧶';
    }} else if (p.includes('રોકેટ') || p.includes('સ્પેસ') || genre === GENRE_SPACE_SHOOTER) {{
      player_emoji = '🚀'; collectible_emoji = '⭐'; obstacle_emoji = '☄️';
    }} else if (p.includes('કાર') || p.includes('રેસિંગ') || genre === GENRE_CARTOON_RACER) {{
      player_emoji = '🏎️'; collectible_emoji = '🪙'; obstacle_emoji = '🚧';
    }} else if (p.includes('કેન્ડી') || p.includes('ડોનટ') || genre === GENRE_CANDY_CATCHER) {{
      player_emoji = '🧺'; collectible_emoji = '🍩'; obstacle_emoji = '💣';
    }} else if (genre === GENRE_MAZE_ADVENTURE) {{
      player_emoji = '🧙'; collectible_emoji = '🔑'; obstacle_emoji = '👻';
    }} else if (genre === GENRE_BUBBLE_POPPER) {{
      player_emoji = '🪄'; collectible_emoji = '🫧'; obstacle_emoji = '💥';
    }}

    const presets = {{
      [GENRE_SPACE_SHOOTER]: {{
        title_gu: `${{player_emoji}} સ્પેસ ગેલેક્સી શૂટર 🌌`,
        title_hi: `${{player_emoji}} स्पेस गैलेक्सी शूटर 🌌`,
        title_en: `${{player_emoji}} Cosmic Galaxy Shooter 🌌`,
        bg_gradient: ['#080918', '#170f38', '#2d0b59'],
        accent: '#00f0ff',
        css_class: 'theme-space',
        instructions_gu: 'ખસવા માટે એરો કી (◀ ▶ ▲ ▼) વાપરો, લેઝર છોડવા સ્પેસબાર અથવા જાદુ દબાવો! ઉલ્કાઓ તોડીને સ્કોર બનાવો!',
        instructions_hi: 'हिलने के लिए तीर कुंजियों का उपयोग करें, लेजर चलाने के लिए स्पेसबार दबाएं!',
        instructions_en: 'Use Arrow keys or touch to steer, press Space or Action to fire lasers! Blast meteors to score!',
        speech_gu: 'અંતરિક્ષમાં રોકેટ તૈયાર છે! સ્પેસબારથી લેઝર છોડો અને ગેલેક્સી બચાવો! 🚀✨',
        speech_hi: 'अंतरिक्ष रॉकेट तैयार है! लेजर दागिए और उल्काओं से बचिए! 🚀✨',
        speech_en: 'Your cosmic starfighter is powered up! Fire lasers with Spacebar and defend the galaxy! 🚀✨'
      }},
      [GENRE_CARTOON_RACER]: {{
        title_gu: `${{player_emoji}} ટર્બો હાઇવે રેસિંગ 🏎️💨`,
        title_hi: `${{player_emoji}} टर्बो हाईवे रेसिंग 🏎️💨`,
        title_en: `${{player_emoji}} Turbo Highway Racer 🏎️💨`,
        bg_gradient: ['#1c1d24', '#2c303d', '#111218'],
        accent: '#ffe600',
        css_class: 'theme-racer',
        instructions_gu: 'લેન બદલવા ડાબી/જમણી કી (◀ ▶) વાપરો, ટર્બો નાઇટ્રો સ્પીડ માટે ▲ અથવા સ્પેસબાર દબાવો! અવરોધોથી બચો!',
        instructions_hi: 'लेन बदलने के लिए बायाँ/दायाँ तीर इस्तेमाल करें, टर्बो गति के लिए स्पेसबार दबाएं!',
        instructions_en: 'Use Left/Right to change lanes, tap Up or Space for Turbo Nitro! Dodge traffic cones!',
        speech_gu: 'ટર્બો કાર રેસ શરૂ થઈ ગઈ છે! અવરોધોથી બચીને સોનાના સિક્કા પકડો! 🏎️⚡',
        speech_hi: 'कार रेस शुरू हो गई है! बाधाओं से बचिए और सिक्के जीतिए! 🏎️⚡',
        speech_en: 'Turbo road race is on! Dodge obstacles and collect golden coins! 🏎️⚡'
      }},
      [GENRE_CANDY_CATCHER]: {{
        title_gu: `${{player_emoji}} કેન્ડી કાર્નિવલ કેચર 🍭🧁`,
        title_hi: `${{player_emoji}} कैंडी कार्निवल कैचर 🍭🧁`,
        title_en: `${{player_emoji}} Sweet Candy Catcher 🍭🧁`,
        bg_gradient: ['#2d0a4e', '#6b117b', '#ff4d88'],
        accent: '#ff007a',
        css_class: 'theme-candy',
        instructions_gu: 'ટોપલી ખસેડવા ◀ ▶ કી વાપરો! આકાશમાંથી પડતી કેન્ડી, ડોનટ્સ અને તારા પકડો! બોમ્બથી બચો!',
        instructions_hi: 'टोकरी हिलाने के लिए तीर कुंजियों का उपयोग करें! गिरती मिठाइयाँ पकड़ें और बम से बचें!',
        instructions_en: 'Move left and right with Arrow keys to catch falling donuts & candies! Avoid the bombs!',
        speech_gu: 'વાહ! આકાશમાંથી સ્વાદિષ્ટ કેન્ડી અને ડોનટ્સનો વરસાદ થઈ રહ્યો છે! ટોપલીમાં ઝડપથી પકડી લો! 🍩🎉',
        speech_hi: 'आसमान से मिठाइयों की बारिश हो रही है! जल्दी से टोकरी में पकड़ें! 🍩🎉',
        speech_en: 'Delicious treats are raining from the sky! Move your basket and catch them all! 🍩🎉'
      }},
      [GENRE_MAZE_ADVENTURE]: {{
        title_gu: `${{player_emoji}} જાદુઈ મેઇઝ એડવેન્ચર 🏰🗝️`,
        title_hi: `${{player_emoji}} जादुई भूलभुलैया एडवेंचर 🏰🗝️`,
        title_en: `${{player_emoji}} Magic Dungeon Maze 🏰🗝️`,
        bg_gradient: ['#0d1117', '#161b22', '#21262d'],
        accent: '#00e676',
        css_class: 'theme-arcade',
        instructions_gu: 'મેઇઝમાં ફરવા એરો કી (◀ ▶ ▲ ▼) વાપરો! ૩ સોનેરી ચાવીઓ (🔑) શોધો અને જાદુઈ દરવાજો (🚪) ખોલો!',
        instructions_hi: 'भूलभुलैया में चलने के लिए तीर कुंजियों का उपयोग करें! 3 चाबियाँ ढूंढकर दरवाजा खोलें!',
        instructions_en: 'Navigate the maze with Arrow keys! Collect all 3 golden keys to open the treasure portal!',
        speech_gu: 'જાદુઈ મેઇઝ તૈયાર છે! ૩ સોનેરી ચાવીઓ શોધો અને રહસ્યમય ખજાનાનો દરવાજો ખોલો! 🗝️✨',
        speech_hi: 'जादुई भूलभुलैया तैयार है! 3 चाबियाँ ढूंढिए और खजाना खोलिए! 🗝️✨',
        speech_en: 'The labyrinth is open! Collect the 3 golden keys to unlock the enchanted treasure! 🗝️✨'
      }},
      [GENRE_BUBBLE_POPPER]: {{
        title_gu: `${{player_emoji}} રંગબેરંગી બબલ પોપર 🫧✨`,
        title_hi: `${{player_emoji}} रंग-बिरंगा बबल पॉपर 🫧✨`,
        title_en: `${{player_emoji}} Rainbow Bubble Popper 🫧✨`,
        bg_gradient: ['#0c1b33', '#123b5c', '#007799'],
        accent: '#00f0ff',
        css_class: 'theme-bubble',
        instructions_gu: 'પરપોટા ફોડવા માઉસ/સ્ક્રીન પર ટેપ કરો, અથવા આખી સ્ક્રીનમાં શોકવેવ છોડવા સ્પેસબાર દબાવો!',
        instructions_hi: 'बबल फोड़ने के लिए क्लिक करें या स्पेसबार दबाकर जादू चलाएं!',
        instructions_en: 'Click or tap on floating bubbles to pop them, or press Space for a mega bubble shockwave!',
        speech_gu: 'રંગબેરંગી પરપોટા આકાશમાં ઉડી રહ્યા છે! ટેપ કરો અને મજેદાર પોપિંગ સાઉન્ડ માણો! 🫧🎶',
        speech_hi: 'रंग-बिरंगे बुलबुले उड़ रहे हैं! क्लिक करके फोड़ें और मज़ा लें! 🫧🎶',
        speech_en: 'Sparkling rainbow bubbles are floating up! Tap or click to pop them in chain reactions! 🫧🎶'
      }},
      [GENRE_PLATFORMER]: {{
        title_gu: `${{player_emoji}} જાદુઈ કૂદકાની રમત 🦘🌈`,
        title_hi: `${{player_emoji}} जादुई कूदने का गेम 🦘🌈`,
        title_en: `${{player_emoji}} Bouncy Platform Hero 🦘🌈`,
        bg_gradient: ['#1f103b', '#491b6d', '#7b1fa2'],
        accent: '#ff007a',
        css_class: 'theme-forest',
        instructions_gu: 'દોડવા માટે ◀ ▶ કી વાપરો, ઊંચો કૂદકો લગાવવા સ્પેસબાર અથવા ▲ દબાવો! તારા ભેગા કરો!',
        instructions_hi: 'दौड़ने के लिए तीर कुंजियाँ दबाएं, कूदने के लिए स्पेसबार दबाएं!',
        instructions_en: 'Run with Left/Right arrows, press Space or Up to jump high! Collect sparkling stars!',
        speech_gu: 'સુપર કૂદકાની રમત તૈયાર છે! સ્પેસબારથી ઊંચો કૂદકો લગાવો અને સોનેરી તારા પકડો! 🦘✨',
        speech_hi: 'कूदने का खेल तैयार है! स्पेसबार दबाइए और तारे जीतिए! 🦘✨',
        speech_en: 'Your jumping adventure is live! Leap across platforms and collect sparkling treasures! 🦘✨'
      }}
    }};

    const preset = presets[genre] || presets[GENRE_PLATFORMER];
    const title = is_gu ? preset.title_gu : (is_hi ? preset.title_hi : preset.title_en);
    const instructions = is_gu ? preset.instructions_gu : (is_hi ? preset.instructions_hi : preset.instructions_en);
    const speech = is_gu ? preset.speech_gu : (is_hi ? preset.speech_hi : preset.speech_en);

    const hud_html = '<div class="hud-chip hud-lives-chip"><span class="hud-emoji">💖</span> <span class="hud-val" id="hud-lives">3</span></div><div class="hud-chip hud-score-chip"><span class="hud-emoji">⭐</span> <span class="hud-val" id="hud-score">0</span></div><div class="hud-chip hud-combo-chip"><span class="hud-emoji">⚡</span> <span class="hud-val" id="hud-combo">x1</span></div><div class="hud-chip hud-powerup-chip" id="hud-powerup-chip" style="display:none;"><span class="hud-emoji" id="hud-powerup-emoji">🛡️</span> <span class="hud-val" id="hud-powerup-timer">SHIELD</span></div><div class="hud-boss-chip" id="hud-boss-chip" style="display:none;"><span class="hud-boss-title" id="hud-boss-title">👾 BOSS</span><div class="hud-boss-bar"><div class="hud-boss-fill" id="hud-boss-fill" style="width:100%;"></div></div></div>';

    return {{
      title,
      genre,
      spoken_response: speech,
      instructions,
      player_emoji,
      collectible_emoji,
      obstacle_emoji,
      bg_gradient: preset.bg_gradient,
      accent: preset.accent,
      css_class: preset.css_class,
      hud_html
    }};
  }}

  function generateCodeSpaceShooter(p_emoji, c_emoji, o_emoji) {{
    return `{space_code}`.trim();
  }}

  function generateCodeCandyCatcher(p_emoji, c_emoji, o_emoji) {{
    return `{candy_code}`.trim();
  }}

  function generateCodeCartoonRacer(p_emoji, c_emoji, o_emoji) {{
    return `{racer_code}`.trim();
  }}

  function generateCodeMazeAdventure(p_emoji, c_emoji, o_emoji) {{
    return `{maze_code}`.trim();
  }}

  function generateCodeBubblePopper(p_emoji, c_emoji, o_emoji) {{
    return `{bubble_code}`.trim();
  }}

  function generateCodePlatformer(p_emoji, c_emoji, o_emoji) {{
    return `{platformer_code}`.trim();
  }}

  function synthesizeGame(prompt, language) {{
    const genre = classifyGenre(prompt);
    const theme = extractThemeDetails(prompt, genre, language);
    const generators = {{
      [GENRE_SPACE_SHOOTER]: generateCodeSpaceShooter,
      [GENRE_CANDY_CATCHER]: generateCodeCandyCatcher,
      [GENRE_CARTOON_RACER]: generateCodeCartoonRacer,
      [GENRE_MAZE_ADVENTURE]: generateCodeMazeAdventure,
      [GENRE_BUBBLE_POPPER]: generateCodeBubblePopper,
      [GENRE_PLATFORMER]: generateCodePlatformer
    }};

    const genFn = generators[genre] || generateCodePlatformer;
    const game_code = genFn(theme.player_emoji, theme.collectible_emoji, theme.obstacle_emoji);

    return {{
      title: theme.title,
      genre: genre,
      spoken_response: theme.spoken_response,
      theme: {{
        background_gradient: theme.bg_gradient,
        accent_color: theme.accent,
        css_class: theme.css_class,
        player_emoji: theme.player_emoji,
        collectible_emoji: theme.collectible_emoji,
        obstacle_emoji: theme.obstacle_emoji,
        hud_html: theme.hud_html
      }},
      instructions: theme.instructions,
      html_hud_overlay: theme.hud_html,
      game_code: game_code,
      new_skill_learned: {{
        id: `custom_mechanic_${{genre}}`,
        name: `${{theme.title}} Engine`,
        description: `Mastered ${{genre}} mechanics with standalone 60fps loop and HUD.`
      }}
    }};
  }}

  function getFallbackSurpriseIdea(language) {{
    const is_gu = (language || 'gu-IN').startsWith('gu');
    const surprises_gu = [
      {{
        surprise_title: '🌌 ઝીરો-ગ્રેવિટી એન્ટિ-ગ્રેવિટી સ્પેસ!',
        spoken_announcement: 'વાહ દોસ્ત! મેં એક જબરદસ્ત આઈડિયા વિચાર્યો છે: છત પર ઊંધા ચાલો અને ઉડતા તારા પકડો!',
        description: 'તમારો પાત્ર હવે ગુરુત્વાકર્ષણને ઉલટાવીને છત પર દોડી શકે છે!',
        action_prompt: 'એન્ટિ-ગ્રેવિટી છત પર ઊંધા દોડવાની શક્તિ ઉમેરો',
        badge: '🌌 ઝીરો ગ્રેવિટી'
      }},
      {{
        surprise_title: '🐉 બેબી ડ્રેગન સાથીદાર!',
        spoken_announcement: 'એક નાનકડો ક્યૂટ બેબી ડ્રેગન તમારી સાથે ઉડશે અને બોનસ સિક્કા લાવી આપશે!',
        description: 'તમારી પાછળ ઉડતો જાદુઈ બેબી ડ્રેગન જે આપમેળે સિક્કા ભેગા કરે છે!',
        action_prompt: 'સાથે ઉડતો બેબી ડ્રેગન સાથીદાર ઉમેરો',
        badge: '🐉 પેટ ડ્રેગન'
      }},
      {{
        surprise_title: '⚡ સુપર નાઇટ્રો ડબલ સ્પીડ!',
        spoken_announcement: 'ઝડપ બમણી થઈ ગઈ છે! રોકેટ બૂસ્ટર સાથે સ્ક્રીન પર વીજળીની જેમ દોડો!',
        description: 'સુપર સ્પીડ અને નિયોન ટ્રેઇલ્સ સાથે હાઇપર ડ્રાઇવ!',
        action_prompt: 'સુપર નાઇટ્રો સ્પીડ અને ગોલ્ડન ચમકારો ઉમેરો',
        badge: '⚡ નાઇટ્રો બૂસ્ટ'
      }}
    ];

    const surprises_en = [
      {{
        surprise_title: '🌌 Zero-Gravity Inversion Mode!',
        spoken_announcement: 'Hey friend! I have an awesome surprise idea: flip gravity and run upside down on the ceiling!',
        description: 'Reverse gravity with Spacebar and collect floating space stars!',
        action_prompt: 'Add anti-gravity ceiling runner mechanics',
        badge: '🌌 Zero Gravity'
      }},
      {{
        surprise_title: '🐉 Baby Dragon Companion!',
        spoken_announcement: 'A cute little flying dragon will follow you and scoop up golden treasures!',
        description: 'Enchanted pet dragon companion that magnetizes treasures!',
        action_prompt: 'Add flying pet baby dragon companion',
        badge: '🐉 Pet Dragon'
      }}
    ];

    const list = is_gu ? surprises_gu : surprises_en;
    return list[Math.floor(Math.random() * list.length)];
  }}

  root.ClientGameSynthesizer = {{
    classifyGenre,
    synthesizeGame,
    getFallbackSurpriseIdea
  }};

}})(typeof window !== 'undefined' ? window : this);
'''

with open(JS_OUT, "w", encoding="utf-8") as f:
    f.write(js_template)

print(f"✨ Successfully generated client-side synthesizer: {JS_OUT} ({os.path.getsize(JS_OUT)} bytes)")
