import json
import os
import time
import logging
import random
from typing import Dict, Any, List, Optional

logger = logging.getLogger("EvolutionEngine")

class EvolutionEngine:
    """
    Autonomous Self-Evolution, Self-Healing, and Dynamic Skill Growth Engine.
    Allows the agent to diagnose bugs, heal broken code, learn new mechanics,
    synthesize surprising game ideas, and level up its own capabilities.
    """
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.skills_file = os.path.join(self.data_dir, "skills_registry.json")
        self.memory_file = os.path.join(self.data_dir, "memory.json")
        self.solutions_file = os.path.join(self.data_dir, "self_solutions.json")
        self.surprises_file = os.path.join(self.data_dir, "surprise_ledger.json")
        self._init_database()

    def _init_database(self):
        # Default starter skills
        if not os.path.exists(self.skills_file):
            default_skills = {
                "particle_rainbow_explosion": {
                    "name": "Rainbow Star Particles",
                    "description": "Spawns bursting colorful stars upon coin pickup or jump",
                    "code_snippet": "spawnParticles(x, y, ['#ff4d4d','#ffb84d','#ffff4d','#4dff4d','#4da6ff','#b84dff'], 12);"
                },
                "floating_score_popup": {
                    "name": "Floating Score Text",
                    "description": "Animates score popup floating up and fading",
                    "code_snippet": "spawnScorePopup(x, y, '+100');"
                },
                "screen_shake_effect": {
                    "name": "Screen Shake on Impact",
                    "description": "Adds juice and camera shake when player hits obstacle or booster",
                    "code_snippet": "triggerScreenShake(8, 200);"
                },
                "sound_synth_synthesizer": {
                    "name": "Retro 8-bit Audio Synthesizer",
                    "description": "Synthesizes tones for jump, coin, powerup, win without external audio files",
                    "code_snippet": "playSound('coin'); playSound('jump'); playSound('powerup');"
                },
                "turbo_boost_mechanic": {
                    "name": "Turbo Rocket Boost",
                    "description": "Doubles speed and draws rainbow exhaust trail",
                    "code_snippet": "player.turboTimer = 180; player.speedMultiplier = 2.0;"
                },
                "kid_invincibility_shield": {
                    "name": "Magical Bubble Shield",
                    "description": "Protects kid from 1 hit with a glowing rainbow orb",
                    "code_snippet": "player.hasShield = true; drawGlowingBubble(player.x, player.y);"
                }
            }
            with open(self.skills_file, "w", encoding="utf-8") as f:
                json.dump(default_skills, f, indent=2)

        if not os.path.exists(self.memory_file):
            default_memory = {
                "total_games_created": 0,
                "total_modifications": 0,
                "bugs_self_healed": 0,
                "skills_learned_count": 6,
                "evolution_level": 1,
                "evolution_title": "🌱 Novice AI Game Alchemist (શરૂઆતનો ગેમ કીમિયાગર)",
                "surprise_ideas_generated": 0,
                "favorite_themes": ["unicorns", "space", "candies", "superheroes", "dinosaurs", "racing"],
                "kid_preferences": {
                    "tone": "excited, encouraging, super fun",
                    "visuals": "vibrant, smooth 60fps, large colorful buttons",
                    "difficulty": "fun and forgiving with powerups"
                },
                "lessons_learned": [
                    "Kids love big colorful particles when they collect items.",
                    "Always ensure jump physics feel bouncy and responsive.",
                    "Provide on-screen touch buttons for tablets and mouse/arrow controls for keyboard.",
                    "Keep game loop 60fps with requestAnimationFrame.",
                    "Surprise ideas should be unexpected, magical, and instantly playable!"
                ]
            }
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(default_memory, f, indent=2)

        if not os.path.exists(self.solutions_file):
            with open(self.solutions_file, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)

        if not os.path.exists(self.surprises_file):
            with open(self.surprises_file, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)

    def get_skills_summary(self) -> str:
        """Returns registered skills formatted for Gemini prompt injection."""
        try:
            with open(self.skills_file, "r", encoding="utf-8") as f:
                skills = json.load(f)
            lines = []
            for k, v in skills.items():
                lines.append(f"- **{v['name']}**: {v['description']}")
            return "\n".join(lines)
        except Exception as e:
            logger.error(f"Error reading skills: {e}")
            return "Standard arcade mechanics, particles, sound synthesizer"

    def register_new_skill(self, skill_id: str, name: str, description: str, code_snippet: str = ""):
        """Dynamically expand the agent's capability library and level up."""
        try:
            with open(self.skills_file, "r", encoding="utf-8") as f:
                skills = json.load(f)
            skills[skill_id] = {
                "name": name,
                "description": description,
                "code_snippet": code_snippet,
                "learned_at": time.time()
            }
            with open(self.skills_file, "w", encoding="utf-8") as f:
                json.dump(skills, f, indent=2)
            
            self._increment_memory_counter("skills_learned_count")
            self._update_evolution_level()
            logger.info(f"✨ Evolution Engine learned a new skill: {name} ({skill_id})")
        except Exception as e:
            logger.error(f"Failed to register new skill: {e}")

    def _update_evolution_level(self):
        """Calculates and updates evolution rank based on skills and self-healing."""
        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                memory = json.load(f)

            skills_count = memory.get("skills_learned_count", 6)
            heals_count = memory.get("bugs_self_healed", 0)
            score = skills_count + (heals_count * 2)

            if score >= 20:
                level = 5
                title = "🌌 Cosmic AI Game Architect (કોસ્મિક AI માસ્ટર આર્કિટેક્ટ)"
            elif score >= 15:
                level = 4
                title = "⚡ Supreme Magic Game Creator (સર્વોચ્ચ જાદુઈ નિર્માતા)"
            elif score >= 11:
                level = 3
                title = "🔮 Master Game Sorcerer (માસ્ટર ગેમ જાદુગર)"
            elif score >= 8:
                level = 2
                title = "✨ Advanced Creative Alchemist (એડવાન્સ્ડ કીમિયાગર)"
            else:
                level = 1
                title = "🌱 Novice AI Game Alchemist (શરૂઆતનો ગેમ કીમિયાગર)"

            memory["evolution_level"] = level
            memory["evolution_title"] = title

            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(memory, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to update evolution level: {e}")

    def record_surprise_idea(self, idea_data: Dict[str, Any]):
        """Logs a generated surprise idea into the surprise history ledger."""
        try:
            with open(self.surprises_file, "r", encoding="utf-8") as f:
                surprises = json.load(f)
            surprises.append({
                **idea_data,
                "timestamp": time.time()
            })
            with open(self.surprises_file, "w", encoding="utf-8") as f:
                json.dump(surprises[-50:], f, indent=2, ensure_ascii=False)
            self._increment_memory_counter("surprise_ideas_generated")
        except Exception as e:
            logger.error(f"Failed to record surprise: {e}")

    def get_fallback_surprise_ideas(self, language: str = "gu-IN") -> Dict[str, Any]:
        """Provides instant high-creativity surprise ideas if offline or fast-response needed."""
        gu_surprises = [
            {
                "surprise_title": "🌌 એન્ટિ-ગ્રાવિટી સ્પેસ પોર્ટલ! (Zero Gravity)",
                "spoken_announcement": "અરે વાહ દોસ્ત! મારી પાસે એક જબરદસ્ત સરપ્રાઇઝ આઈડિયા છે! શું હું ગેમમાં એન્ટિ-ગ્રાવિટી પોર્ટલ ઉમેરી દઉં, જેથી તમે સીધા આકાશની છત પર ચાલી શકો?",
                "description": "કૂદવા પર ગ્રાવિટી ઉલટી થઈ જાય છે અને તમે આકાશમાં ઊંધા ચાલીને સોનેરી પિઝા અને તારા પકડો છો!",
                "action_prompt": "ગેમમાં એન્ટિ-ગ્રાવિટી ફ્લિપ મિકેનિક ઉમેરો જેથી સ્પેસબાર દબાવતા પ્લેયર છત પર ચાલવા લાગે અને આકાશમાં સોનેરી પિઝા ભેગા કરે",
                "badge": "🌌 Zero Gravity"
            },
            {
                "surprise_title": "🐉 બેબી ડ્રેગન કમ્પેનિયન અને ફાયરબબલ્સ! (Pet Dragon)",
                "spoken_announcement": "દોસ્ત! કેવું રહે જો તમારી પાછળ એક નાનકડો ક્યૂટ બેબી ડ્રેગન ઉડતો આવે અને રંગબેરંગી પરપોટા છોડીને પોઈન્ટ્સ ભેગા કરવામાં મદદ કરે?",
                "description": "એક નાનો પેટ ડ્રેગન જે તમારી સાથે ઉડે છે અને જાદુઈ ફાયરબબલ્સ ફેંકીને બોનસ કોઈન્સ આકર્ષિત કરે છે!",
                "action_prompt": "ગેમમાં પ્લેયરની પાછળ ઉડતો એક નાનો બેબી ડ્રેગન પેટ ઉમેરો જે ચમકતા બબલ્સ છોડે અને કોઈન્સ ખેંચે",
                "badge": "🐉 Pet Dragon"
            },
            {
                "surprise_title": "🧁 મેગા સુપર કેન્ડી રેઇન સ્ટોર્મ! (Candy Storm)",
                "spoken_announcement": "મારી પાસે એક મસ્ત સરપ્રાઇઝ આઈડિયા છે! આકાશમાંથી અચાનક રંગબેરંગી કપકેક અને લોલીપોપ્સનો ગોલ્ડન વરસાદ શરૂ થઈ જાય તો કેવી મજા પડે?",
                "description": "જાદુઈ કેન્ડી સ્ટોર્મ જેમાં આકાશમાંથી ચમકતા કપકેક, કેન્ડી અને ૫૦૦ પોઈન્ટ વાળા મેગા બોનસ તારા વરસે છે!",
                "action_prompt": "ગેમમાં એક મેજિકલ કેન્ડી સ્ટોર્મ મોડ ઉમેરો જ્યાં આકાશમાંથી કપકેક, લોલીપોપ અને બોનસ તારાઓ વરસે",
                "badge": "🧁 Candy Storm"
            },
            {
                "surprise_title": "⚡ ટર્બો રેઇન્બો જેટપેક અને સ્પીડ ટનલ! (Rainbow Jetpack)",
                "spoken_announcement": "સરપ્રાઇઝ! ચાલો પ્લેયરને એક અલ્ટ્રા ટર્બો રેઇન્બો જેટપેક આપી દઈએ, જેનાથી તમે સુપરસોનિક સ્પીડે આકાશમાં ઉડી શકો!",
                "description": "રેઇન્બો જેટપેક જે પ્લેયરને હવામાં અનંત ઉડવાની શક્તિ આપે છે અને પાછળ મેઘધનુષી ધુમાડો છોડે છે!",
                "action_prompt": "પ્લેયરને એક રેઇન્બો જેટપેક બૂસ્ટર આપો જેથી 'જાદુ' બટન દબાવતા તે સુપર સ્પીડે આકાશમાં ઉડી શકે",
                "badge": "⚡ Rainbow Jetpack"
            }
        ]

        en_surprises = [
            {
                "surprise_title": "🌌 Anti-Gravity Cosmic Portal!",
                "spoken_announcement": "Hey friend! I have a mind-blowing surprise idea! What if we flip gravity upside down so you can walk on the sky ceiling?",
                "description": "Gravity inverts! Walk on the ceiling and catch flying space pizzas and neon stars!",
                "action_prompt": "Add an anti-gravity inversion mechanic where tapping jump flips the player onto the sky ceiling to collect flying cosmic pizzas",
                "badge": "🌌 Zero Gravity"
            },
            {
                "surprise_title": "🐉 Baby Dragon Companion Pet!",
                "spoken_announcement": "Surprise! How about a cute baby dragon companion flying right behind you that shoots sparkling bubbles to grab coins?",
                "description": "A loyal mini dragon companion following the player, launching magnetic bubbles that scoop up collectibles!",
                "action_prompt": "Add a flying baby dragon pet companion that follows the player and magnetizes nearby stars and treats",
                "badge": "🐉 Pet Dragon"
            },
            {
                "surprise_title": "🧁 Golden Candy Meteor Storm!",
                "spoken_announcement": "Surprise! What if a magical golden cloud rolls in and rains giant sparkling cupcakes and 500-point stars from the sky?",
                "description": "Sudden sweet shower: giant glowing cupcakes, lollipops, and super bonus stars falling with neon fireworks!",
                "action_prompt": "Add a magical candy storm event where colorful giant cupcakes and 500-point star meteors rain down from the sky",
                "badge": "🧁 Candy Storm"
            }
        ]

        pool = gu_surprises if language.startswith("gu") else en_surprises
        chosen = random.choice(pool)
        self.record_surprise_idea(chosen)
        return chosen

    def record_self_healed_bug(self, error_message: str, fix_applied: str, context: Optional[Dict[str, Any]] = None):
        """Log a diagnosed & self-healed bug to prevent recurrence."""
        try:
            with open(self.solutions_file, "r", encoding="utf-8") as f:
                solutions = json.load(f)
            solutions.append({
                "error": error_message,
                "fix": fix_applied,
                "context": context or {},
                "timestamp": time.time()
            })
            with open(self.solutions_file, "w", encoding="utf-8") as f:
                json.dump(solutions[-50:], f, indent=2)
            self._increment_memory_counter("bugs_self_healed")
            self._update_evolution_level()
            logger.info(f"🛡️ Self-Healing recorded solution for: {error_message[:60]}")
        except Exception as e:
            logger.error(f"Failed to log self-healed bug: {e}")

    def add_lesson_learned(self, lesson: str):
        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                memory = json.load(f)
            if lesson not in memory.get("lessons_learned", []):
                memory.setdefault("lessons_learned", []).append(lesson)
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(memory, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to record lesson: {e}")

    def _increment_memory_counter(self, key: str):
        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                memory = json.load(f)
            memory[key] = memory.get(key, 0) + 1
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(memory, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to increment memory counter {key}: {e}")

    def get_memory(self) -> Dict[str, Any]:
        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def get_all_skills(self) -> Dict[str, Any]:
        try:
            with open(self.skills_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
