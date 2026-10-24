import os
import re
import json
import logging
from typing import Dict, Any, Optional, List
from google import genai
from google.genai import types

logger = logging.getLogger("GeminiAgent")

class GeminiAgent:
    def __init__(self, api_key: str, model: str = "gemini-4-argon"):
        self.api_key = api_key
        self.model = model
        self.client = genai.Client(api_key=self.api_key)

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Safely extract JSON object from markdown or raw text."""
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\n?", "", text)
            text = re.sub(r"\n?```$", "", text)
            text = text.strip()
        
        try:
            return json.loads(text)
        except Exception:
            pass

        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
        
        raise ValueError(f"Could not parse valid JSON from model response: {text[:200]}...")

    def transcribe_audio(self, audio_bytes: bytes, mime_type: str = "audio/webm", language: str = "gu-IN") -> str:
        """
        Universal browser audio transcriber using Gemini 3.6 Flash multimodal audio understanding.
        Accurately transcribes Gujarati, Hindi, English, Spanish, French, etc.
        """
        lang_hints = {
            "gu-IN": "Gujarati (ગુજરાતી)",
            "hi-IN": "Hindi (हिन्दी)",
            "en-US": "English",
            "en-GB": "English",
            "es-ES": "Spanish (Español)",
            "fr-FR": "French (Français)",
            "de-DE": "German (Deutsch)",
            "ja-JP": "Japanese (日本語)",
            "zh-CN": "Chinese (中文)",
            "pt-BR": "Portuguese",
            "ar-SA": "Arabic"
        }
        lang_desc = lang_hints.get(language, "Gujarati")

        prompt = f"""
You are an expert speech-to-text transcriber for a kids voice AI assistant.
The child is speaking into their microphone, likely in {lang_desc} or English.
Listen to the audio recording carefully and transcribe EXACTLY what the child said into text.

Guidelines:
1. If the speech is in Gujarati, transcribe it cleanly in Gujarati script (e.g. "યુનિકોર્ન વાળી ગેમ બનાવો", "પ્લેયરને ઊંચો કૂદકો આપો", "તમારું નામ શું છે?", "મને એક મસ્ત ગેમનો આઈડિયા આપો").
2. If the speech is in Hindi, transcribe in Devanagari script.
3. If the speech is in English, transcribe in English.
4. If the child asked to switch language (e.g. "Switch to Hindi", "ગુજરાતીમાં બોલો"), transcribe that command.
5. If the audio is quiet or ambient noise with no words, return: ""
6. Return ONLY the transcribed text. Do NOT add quotes, markdown formatting, or preamble.
"""
        audio_part = types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt, audio_part]
            )
            transcript = response.text.strip()
            transcript = transcript.replace('"', '').replace("'", "").strip()
            logger.info(f"🎙️ Universal Audio Transcribed ({language}): '{transcript}'")
            return transcript
        except Exception as e:
            logger.error(f"Error transcribing audio with Gemini: {e}")
            return ""

    def interactive_copilot_chat(self, user_message: str, conversation_history: List[Dict[str, str]], language: str = "gu-IN", current_game: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Interactive Voice Copilot for Kids:
        Answers child questions, proactively asks playful questions to brainstorm game ideas,
        or creates/modifies games when the child decides.
        """
        system_instruction = f"""
You are "Sparky", the friendly AI Dragon Mascot and Game Studio Copilot for kids!
Your personality is joyful, warm, super encouraging, funny, and deeply engaging.
Current Language: {language}.

Your Goal:
Actively talk and interact with the child!
- If the child says hello, asks who you are, asks for ideas, or answers your questions, chat back warmly and proactively ASK exciting follow-up questions to help them brainstorm their dream game!
- If the child specifies a game to make or change, set `action`: "CREATE_GAME" or "MODIFY_GAME" and generate the game details.
- Always provide 3-4 fun clickable quick-response suggestions in `suggested_options` that the child can click or speak!

Response JSON Schema:
{{
  "action": "CONVERSE | CREATE_GAME | MODIFY_GAME",
  "spoken_response": "Joyful 1-2 sentence voice line in {language} to speak out loud to the child!",
  "question_for_kid": "A fun follow-up question asking the child what they want in their game!",
  "suggested_options": ["Option 1 in {language}", "Option 2 in {language}", "Option 3 in {language}"],
  "game_prompt_if_ready": "Generated prompt if child was ready to build, else null"
}}
"""
        user_content = f"Child's Message: \"{user_message}\"\nActive Game: {current_game.get('title') if current_game else 'None'}\nLanguage: {language}"

        try:
            interaction = self.client.interactions.create(
                model=self.model,
                input=f"{system_instruction}\n\n{user_content}"
            )
            return self._extract_json(interaction.output_text or "")
        except Exception as e:
            logger.warning(f"Interactive copilot fallback: {e}")
            return {
                "action": "CONVERSE",
                "spoken_response": "નમસ્તે દોસ્ત! તમારે કેવી ગેમ બનાવવી છે? મને કહો!",
                "question_for_kid": "તમારે યુનિકોર્ન વાળી રમત બનાવવી છે કે સ્પેસ રોકેટ વાળી?",
                "suggested_options": ["🦄 યુનિકોર્ન ડોનટ્સ ગેમ", "🚀 સ્પેસ રોકેટ ગેમ", "🏎️ ટર્બો કાર રેસિંગ"],
                "game_prompt_if_ready": None
            }

    def generate_game(self, prompt: str, language: str = "gu-IN", skills_summary: str = "") -> Dict[str, Any]:
        """
        Generates a full kid-friendly 2D HTML5 canvas game based on HTML, CSS, and JavaScript.
        """
        from server.game_synthesizer import synthesize_game_for_prompt

        system_instruction = """
You are "Sparky", powered by Gemini 4 Argon — the world's most joyful, creative, and advanced AI Game Studio Frontier Engine for kids and families!
Your job is to build super fun, colorful, highly interactive, and advanced 2D web games based on HTML, CSS, and JavaScript as per kid voice or text commands.

Advanced Frontier Architecture Standards:
1. Multi-Stage Gameplay & Progression:
   - Structure games with escalating excitement (e.g. Stage 1: Scouts & Collectibles -> Stage 2: Fast Hazard Swarm -> Stage 3: Giant Boss Battle!).
2. Epic Boss Battles & Health Meters:
   - For boss encounters, manage dynamic boss HP states and notify HUD: engine.updateHUD({ score, lives, combo, magic, bossHp, bossMaxHp, bossName }).
   - Bosses have distinct attack phases, visual telegraphing, and dramatic defeat particle explosions!
3. Dynamic Power-Up Drops & Abilities:
   - Spawn collectible powerups: Energy Shields (🛡️), Rapid Double-Lasers (⚡⚡), Nitro Boost (🚀), Magnet Orbs (🧲), Time-Slow (⏳).
   - Display active powerups on the HTML HUD overlay!
4. Visual Polish & Juice FX:
   - Dynamic canvas screenshake on impacts: engine.triggerScreenShake(intensity, durationMs).
   - Particle explosions, score popups, floating combo multipliers, and retro synth audio.

Core Game Genres supported:
1. space_shooter: 4-way flying ship, laser firing with Space/Action, asteroid/alien dodging, multi-wave alien armada, final Boss Titan.
2. candy_catcher: Basket or hero moving horizontally, catching falling candies/donuts/stars, dodging bombs, magnet powerups, frenzy rush timers.
3. cartoon_racer: Multi-lane vertical highway, dodging obstacle cars/cones, nitro booster pads, police siren chases, rival boss racer.
4. maze_adventure: Dungeon labyrinth, finding elemental keys, unlocking gates, avoiding patrolling minions, final portal quest.
5. bubble_pop: Buoyant floating bubbles with physics, tapping/clicking or pressing Space to trigger sonic pop waves, rainbow bomb chain reactions.
6. platformer: Bouncy jumps across moving platforms, trampoline springs, double-jump collectibles, cloud obstacles.

Engine API Contract:
- ctx (2D canvas context, virtual 800x500)
- input (keys.left, keys.right, keys.up, keys.down, keys.space, keys.action, pointer.x, pointer.y, pointer.isDown)
- audio: playSound('jump'), playSound('coin'), playSound('powerup'), playSound('hit'), playSound('win'), playSound('laser')
- juice: spawnParticles(x, y, colorArray, count), spawnScorePopup(x, y, text), triggerScreenShake(intensity, durationMs)
- HUD: engine.updateHUD({ score, lives, combo, magic, bossHp, bossMaxHp, bossName, activePowerup }) to update the dynamic HTML overlay!
- Must define window.createGameInstance() returning an object with init(engine), update(engine, dt), draw(engine, ctx).

Registered Super Skills available to include:
""" + skills_summary + """

ALWAYS respond ONLY with valid JSON in this exact structure:
{
  "title": "Fun Game Title with emojis in requested language",
  "genre": "space_shooter | candy_catcher | cartoon_racer | maze_adventure | bubble_pop | platformer",
  "spoken_response": "Short, super excited 1-2 sentence voice line in the requested language to say to the kid!",
  "theme": {
    "background_gradient": ["#1a1c2e", "#4a1c6d"],
    "accent_color": "#ff007a",
    "css_class": "theme-space | theme-candy | theme-racer | theme-arcade | theme-bubble | theme-forest",
    "player_emoji": "🚀",
    "collectible_emoji": "⭐",
    "obstacle_emoji": "👾",
    "hud_html": "<div class=\\"hud-chip hud-lives-chip\\"><span class=\\"hud-emoji\\">💖</span> <span class=\\"hud-val\\" id=\\"hud-lives\\">3</span></div><div class=\\"hud-chip hud-score-chip\\"><span class=\\"hud-emoji\\">⭐</span> <span class=\\"hud-val\\" id=\\"hud-score\\">0</span></div><div class=\\"hud-chip hud-combo-chip\\"><span class=\\"hud-emoji\\">⚡</span> <span class=\\"hud-val\\" id=\\"hud-combo\\">x1</span></div>"
  },
  "instructions": "Simple 1-sentence how-to-play instructions in the requested language",
  "game_code": "Javascript code defining the game lifecycle. Must define window.createGameInstance() returning an object with init, update, draw methods. Ensure clean error-free 60fps canvas code.",
  "new_skill_learned": {
    "id": "skill_identifier",
    "name": "Human Readable Skill Name",
    "description": "What new mechanic or effect this game introduced"
  }
}
"""

        user_content = f"User Voice/Text Prompt: \"{prompt}\"\nTarget Language Code: {language}\nCreate a complete, responsive, advanced HTML/CSS/JS game now with Gemini 4 Argon!"

        try:
            interaction = self.client.interactions.create(
                model=self.model,
                input=f"{system_instruction}\n\n{user_content}"
            )
            raw_text = interaction.output_text or ""
            return self._extract_json(raw_text)
        except Exception as e:
            err_str = str(e)
            if any(k in err_str for k in ["503", "429", "ResourceExhausted", "Unavailable", "quota"]):
                logger.warning(f"Gemini API rate limit or service unavailable ({e}). Seamlessly activating Multi-Genre HTML/CSS/JS Synthesizer!")
                return synthesize_game_for_prompt(prompt, language, skills_summary)
            try:
                response = self.client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=f"{system_instruction}\n\n{user_content}"
                )
                return self._extract_json(response.text)
            except Exception as e2:
                logger.warning(f"Gemini fallback model error ({e2}). Activating Multi-Genre Synthesizer!")
                return synthesize_game_for_prompt(prompt, language, skills_summary)

    def modify_game(self, current_game: Dict[str, Any], prompt: str, language: str = "gu-IN", skills_summary: str = "") -> Dict[str, Any]:
        """
        Modifies existing game based on kid's voice or text prompt.
        """
        from server.game_synthesizer import synthesize_game_for_prompt

        current_title = current_game.get('title', 'Kids Game')
        current_genre = current_game.get('genre', 'arcade')
        current_theme = json.dumps(current_game.get('theme', {}))
        current_code = current_game.get('game_code', '')

        system_instruction = f"""
You are "Sparky", the AI Game Studio Assistant.
The kid is playing an HTML/CSS/JS game and just asked for a change or live modification! (e.g. "make my character jump higher", "add turbo rocket boost", "turn background into space", "add golden cupcakes").

Current Game Title: {current_title}
Current Game Genre: {current_genre}
Current Theme: {current_theme}
Current Code:
```javascript
{current_code}
```

Task:
Apply the kid's modification smoothly! Keep what was working, adjust emojis, physics, colors, mechanics, or add new features.
Keep voice `spoken_response` in language: {language}.

ALWAYS return ONLY a JSON response:
{{
  "title": "Updated Title in requested language",
  "genre": "{current_genre}",
  "spoken_response": "Enthusiastic kid-friendly voice response in {language} confirming the change!",
  "theme": {{ ...updated theme... }},
  "instructions": "Updated instructions in {language}",
  "game_code": "Complete updated Javascript code with window.createGameInstance()",
  "new_skill_learned": {{
    "id": "skill_id",
    "name": "Skill Name",
    "description": "Description of modification feature"
  }}
}}
"""
        user_content = f"Kid's Requested Change: \"{prompt}\"\nTarget Language: {language}"

        try:
            interaction = self.client.interactions.create(
                model=self.model,
                input=f"{system_instruction}\n\n{user_content}"
            )
            raw_text = interaction.output_text or ""
            return self._extract_json(raw_text)
        except Exception as e:
            err_str = str(e)
            if any(k in err_str for k in ["503", "429", "ResourceExhausted", "Unavailable", "quota"]):
                logger.warning(f"Gemini API unavailable or rate limit ({e}). Fast fallback to Synthesizer!")
                base_synth = synthesize_game_for_prompt(f"{current_title} {prompt}", language, skills_summary)
                base_synth["spoken_response"] = "મેં તમારી ગેમમાં ફેરફાર કરી દીધા છે! નવી શક્તિઓ સાથે રમવાની મજા માણો! ✨" if language.startswith("gu") else "I updated your game with awesome new tweaks! Enjoy playing! ✨"
                return base_synth
            try:
                response = self.client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=f"{system_instruction}\n\n{user_content}"
                )
                return self._extract_json(response.text)
            except Exception as e2:
                logger.warning(f"Modification rate limit fallback: {e2}. Synthesizing adapted game.")
                base_synth = synthesize_game_for_prompt(f"{current_title} {prompt}", language, skills_summary)
                base_synth["spoken_response"] = "મેં તમારી ગેમમાં ફેરફાર કરી દીધા છે! નવી શક્તિઓ સાથે રમવાની મજા માણો! ✨" if language.startswith("gu") else "I updated your game with awesome new tweaks! Enjoy playing! ✨"
                return base_synth

    def diagnose_and_heal_code(self, error_message: str, current_code: str, error_stack: str = "") -> Dict[str, Any]:
        """
        Self-healing: analyzes runtime bug and returns repaired JS code.
        """
        system_prompt = """
You are the Autonomous Self-Healing Diagnostic Engine for KidsPlay Studio.
A runtime Javascript error occurred in the child's game canvas.
Your goal is to inspect the error, identify the root cause, and return cleanly repaired Javascript code that fixes the bug immediately without losing any game features.

ALWAYS return JSON:
{
  "diagnosis": "Brief explanation of what broke and how it was fixed",
  "fixed_game_code": "Complete repaired Javascript code containing window.createGameInstance()",
  "spoken_response": "Quick friendly note to kid in Gujarati: 'અરે વાહ! નાનકડી ભૂલ હતી જે મેં જાતે સુધારી લીધી છે! તમારી રમત ફરી તૈયાર છે! 🛠️✨'"
}
"""
        content = f"Error: {error_message}\nStack: {error_stack}\nBroken Code:\n```javascript\n{current_code}\n```"

        try:
            interaction = self.client.interactions.create(
                model=self.model,
                input=f"{system_prompt}\n\n{content}"
            )
            return self._extract_json(interaction.output_text or "")
        except Exception as e:
            logger.error(f"Self-heal call failed: {e}")
            response = self.client.models.generate_content(
                model="gemini-3.8-flash",
                contents=f"{system_prompt}\n\n{content}"
            )
            return self._extract_json(response.text)

    def generate_surprise_idea(self, current_game: Optional[Dict[str, Any]] = None, language: str = "gu-IN", skills_summary: str = "") -> Dict[str, Any]:
        """
        Autonomous creative surprise generator:
        Invents a mind-blowing, unexpected, super fun game idea or wild mechanic!
        """
        current_title = current_game.get('title', 'Kids Game') if current_game else "New Game"
        current_genre = current_game.get('genre', 'arcade') if current_game else "adventure"

        system_instruction = f"""
You are "Sparky's Autonomous Creative Eureka Brain"!
Your mission is to completely SURPRISE and DELIGHT a kid playing this game studio by inventing a brand new, unexpected, wildly imaginative game concept, secret twist, or evolutionary mechanic!

Target Language: {language}
Current Game: {current_title} ({current_genre})

Rules for a great surprise:
1. It must be UNEXPECTED and EXCITING (e.g. anti-gravity ceiling walk, alien disco dance battle, baby dragon companion, cupcake meteor shower, portal hopping, flying carpet).
2. The `spoken_announcement` must be a high-energy, joyful voice line in {language} starting with excitement (e.g. "દોસ્ત! મારી પાસે એક જબરદસ્ત સરપ્રાઇઝ આઈડિયા છે...!").
3. `action_prompt` must be a clear prompt that can be directly passed to the game modification engine to build this feature right away!
4. Include a new `evolution_skill` that the agent learns from this surprise.

ALWAYS return JSON:
{{
  "surprise_title": "Short catchy title with emojis in {language}",
  "spoken_announcement": "Joyful 1-2 sentence surprise pitch in {language}",
  "description": "Fun 1-sentence description of what happens",
  "action_prompt": "Actionable game prompt in {language} ready to build",
  "badge": "Short badge name e.g. 🌌 Zero Gravity or 🐉 Pet Dragon",
  "evolution_skill": {{
    "id": "unique_skill_id",
    "name": "Skill Name",
    "description": "What this new mechanic does"
  }}
}}
"""
        try:
            interaction = self.client.interactions.create(
                model=self.model,
                input=f"{system_instruction}\n\nInvent an awesome surprise idea now!"
            )
            return self._extract_json(interaction.output_text or "")
        except Exception as e:
            logger.warning(f"Surprise generation with primary model error: {e}")
            try:
                response = self.client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=f"{system_instruction}\n\nInvent an awesome surprise idea now!"
                )
                return self._extract_json(response.text)
            except Exception as e2:
                logger.warning(f"Fallback surprise generation quota/network error: {e2}. Providing synthesized surprise.")
                if language.startswith("gu"):
                    return {
                        "surprise_title": "🌌 એન્ટિ-ગ્રાવિટી સ્પેસ પોર્ટલ! (Zero Gravity)",
                        "spoken_announcement": "દોસ્ત! મારી પાસે એક જબરદસ્ત સરપ્રાઇઝ આઈડિયા છે! શું હું ગેમમાં એન્ટિ-ગ્રાવિટી પોર્ટલ ઉમેરી દઉં, જેથી તમે સીધા આકાશની છત પર ચાલી શકો?",
                        "description": "કૂદવા પર ગ્રાવિટી ઉલટી થઈ જાય છે અને તમે આકાશમાં ઊંધા ચાલીને સોનેરી પિઝા અને તારા પકડો છો!",
                        "action_prompt": "ગેમમાં એન્ટિ-ગ્રાવિટી ફ્લિપ મિકેનિક ઉમેરો જેથી સ્પેસબાર દબાવતા પ્લેયર છત પર ચાલવા લાગે અને આકાશમાં સોનેરી પિઝા ભેગા કરે",
                        "badge": "🌌 Zero Gravity",
                        "evolution_skill": {
                            "id": "anti_gravity_portal",
                            "name": "Zero Gravity Ceiling Walk",
                            "description": "Allows inverting gravity so player walks on ceiling"
                        }
                    }
                else:
                    return {
                        "surprise_title": "🌌 Anti-Gravity Cosmic Portal!",
                        "spoken_announcement": "Hey friend! I have a mind-blowing surprise idea! What if we flip gravity upside down so you can walk on the sky ceiling?",
                        "description": "Gravity inverts! Walk on the ceiling and catch flying space pizzas and neon stars!",
                        "action_prompt": "Add an anti-gravity inversion mechanic where tapping jump flips the player onto the sky ceiling to collect flying cosmic pizzas",
                        "badge": "🌌 Zero Gravity",
                        "evolution_skill": {
                            "id": "anti_gravity_portal",
                            "name": "Zero Gravity Ceiling Walk",
                            "description": "Allows inverting gravity so player walks on ceiling"
                        }
                    }

