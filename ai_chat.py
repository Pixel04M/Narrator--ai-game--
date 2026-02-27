"""
AI Chat System for Virtual Pet Game
===================================
Handles AI responses using Fireworks AI API and rule-based fallbacks.
"""

import pygame
import random
import threading
import re

# Try to import requests for API calls
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: 'requests' library not available. AI chat will use rule-based mode.")
    print("Install with: pip install requests")

import config


def clean_ai_response(text):
    """Clean AI response by removing markdown code blocks and formatting artifacts."""
    if not text:
        return text
    
    # Remove markdown code blocks (```code``` or ```)
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'```', '', text)
    
    # Remove inline code markers
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # Remove any remaining markdown formatting
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*([^*]+)\*', r'\1', text)  # Italic
    text = re.sub(r'__([^_]+)__', r'\1', text)  # Underline bold
    text = re.sub(r'_([^_]+)_', r'\1', text)  # Underline italic
    
    # Remove any leading/trailing whitespace
    text = text.strip()
    
    # Remove any multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text


class AIChat:
    """AI Chat System that generates responses using real AI API.
    
    Supports Fireworks AI provider (minimax-m2p5 model).
    """
    
    def __init__(self, api_key=None, model=None, provider=None):
        self.provider = provider or config.AI_PROVIDER
        self.is_available = False
        self.is_thinking = False
        self.conversation_history = {}  # Per-character conversation history
        self.global_conversation_history = []  # For global chat
        self.thinking_message = ""
        
        # Check if AI is properly configured
        if not config.USE_AI_CHAT:
            print("AI Chat: Disabled via configuration (USE_AI_CHAT = False)")
            return
            
        if not REQUESTS_AVAILABLE:
            print("AI Chat: Requests library not available. Using rule-based mode.")
            return
        
        # Set API key and model based on provider
        if self.provider == "fireworks":
            self.api_key = api_key or config.FIREWORKS_API_KEY
            self.model = model or config.FIREWORKS_MODEL
            self.api_url = config.FIREWORKS_API_URL
            
            if not self.api_key:
                print("AI Chat: No Fireworks AI API key configured. Using rule-based mode.")
                print("To enable Fireworks AI chat:")
                print("  1. Get an API key from https://fireworks.ai")
                print("  2. Set USE_AI_CHAT = True in config.py")
                print("  3. Set AI_PROVIDER = \"fireworks\" in config.py")
                print("  4. Set FIREWORKS_API_KEY with your key (or use environment variable)")
                return
            
            self.is_available = True
            print(f"AI Chat: Enabled using Fireworks AI ({self.model})")
        else:
            print(f"AI Chat: Unknown provider '{self.provider}'. Using rule-based mode.")
            print("Supported provider: 'fireworks'")
    
    def _get_conversation_history(self, character_name, all_characters=None):
        """Get or initialize conversation history for a character."""
        if character_name not in self.conversation_history:
            # Start with system prompt
            system_prompt = config.CHARACTER_PROMPTS.get(character_name, 
                "You are a friendly virtual pet.")
            
            # Add character awareness - information about other characters
            if all_characters:
                relationships = config.CHARACTER_RELATIONSHIPS.get(character_name, {})
                if relationships:
                    system_prompt += " The other characters in the room are: "
                    rel_parts = []
                    for other_name, relation in relationships.items():
                        rel_parts.append(f"{other_name} ({relation})")
                    system_prompt += "; ".join(rel_parts) + "."
            
            # Add instruction for brief responses
            system_prompt += " Always give brief, direct answers (1-2 sentences max)."
            self.conversation_history[character_name] = [
                {"role": "system", "content": system_prompt}
            ]
        return self.conversation_history[character_name]
    
    def _get_global_system_prompt(self, characters):
        """Get system prompt for global chat (all characters respond)."""
        # Build prompt that includes all character info
        all_char_info = []
        for char in characters:
            personality = config.CHARACTER_PROMPTS.get(char.name, "You are a virtual pet.")
            relationships = config.CHARACTER_RELATIONSHIPS.get(char.name, {})
            rel_text = ""
            if relationships:
                rel_parts = [f"{k}: {v}" for k, v in relationships.items()]
                rel_text = f" You know: {', '.join(rel_parts)}."
            
            all_char_info.append(f"- {char.name}: {personality}{rel_text}")
        
        system_prompt = (
            "You are in a group conversation with other characters. "
            "The players asked a general question to everyone. "
            "Respond as your character would, keeping it brief (1-2 sentences). "
            "Consider what other characters might say but speak as yourself.\n\n"
            "Character info:\n" + "\n".join(all_char_info)
        )
        return system_prompt
    
    def generate_response(self, character, message, callback=None, all_characters=None):
        """Generate AI response using the API."""
        if not self.is_available:
            # Fallback to rule-based
            return None
        
        # Show thinking message
        self.is_thinking = True
        self.thinking_message = random.choice(config.AI_LOADING_MESSAGES)
        
        # Run API call in background thread
        thread = threading.Thread(
            target=self._generate_response_async,
            args=(character, message, callback, all_characters)
        )
        thread.daemon = True
        thread.start()
        
        return self.thinking_message  # Return loading message
    
    def generate_global_response(self, message, characters, callback):
        """Generate AI response for global chat (all characters hear it)."""
        if not self.is_available:
            return None
        
        # For global chat, we'll send to each character individually
        # but with context about the global message
        self.is_thinking = True
        self.thinking_message = random.choice(config.AI_LOADING_MESSAGES)
        
        thread = threading.Thread(
            target=self._generate_global_response_async,
            args=(message, characters, callback)
        )
        thread.daemon = True
        thread.start()
        
        return self.thinking_message
    
    def _generate_global_response_async(self, message, characters, callback):
        """Generate responses for all characters in global chat."""
        try:
            # Each character responds individually
            responses = []
            for character in characters:
                # Get their conversation history
                history = self._get_conversation_history(character.name, characters)
                
                # Add the global message as user input
                history.append({"role": "user", "content": f"[Global question to everyone] {message}"})
                
                # Make API request for this character
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": self.model,
                    "messages": history,
                    "max_tokens": 500,
                    "temperature": 0.7
                }
                
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=20
                )
                
                if response.status_code == 200:
                    data = response.json()
                    ai_response = data['choices'][0]['message']['content']
                    # Clean the response
                    ai_response = clean_ai_response(ai_response)
                    
                    # Add to history
                    history.append({"role": "assistant", "content": ai_response})
                    
                    # Keep history manageable
                    if len(history) > 12:
                        history[:] = [history[0]] + history[-10:]
                    
                    responses.append((character, ai_response))
                else:
                    # Use fallback
                    fallback = config.AI_FALLBACK_MESSAGES.get(character.personality, "*looks around*")
                    responses.append((character, fallback))
            
            # Call callback with all responses
            if callback:
                callback(responses)
                
        except Exception as e:
            print(f"AI Chat: Error in global response - {str(e)}")
            if callback:
                # Fallback responses for all
                fallback_responses = []
                for char in characters:
                    fallback_responses.append((char, config.AI_FALLBACK_MESSAGES.get(char.personality, "*looks confused*")))
                callback(fallback_responses)
        finally:
            self.is_thinking = False
    
    def _generate_response_async(self, character, message, callback, all_characters=None):
        """Generate response in background thread."""
        try:
            # Get conversation history
            history = self._get_conversation_history(character.name, all_characters)
            
            # Add user message
            history.append({"role": "user", "content": message})
            
            # Make API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Fireworks AI format - optimized for fast, brief responses
            payload = {
                "model": self.model,
                "messages": history,
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data['choices'][0]['message']['content']
                
                # Clean the response (remove code blocks, markdown, etc.)
                ai_response = clean_ai_response(ai_response)
                
                # Add AI response to history
                history.append({"role": "assistant", "content": ai_response})
                
                # Keep history manageable (last 10 messages)
                if len(history) > 12:
                    history[:] = [history[0]] + history[-10:]
                
                # Call callback with response
                if callback:
                    callback(ai_response)
            elif response.status_code == 429:
                # Rate limited
                print("AI Chat: Rate limited. Using fallback.")
                if callback:
                    callback(None)
            else:
                print(f"AI Chat: API error {response.status_code} - {response.text[:200]}")
                if callback:
                    callback(None)
                    
        except requests.exceptions.Timeout:
            print("AI Chat: Request timed out. Using fallback.")
            if callback:
                callback(None)
        except Exception as e:
            print(f"AI Chat: Error - {str(e)}")
            if callback:
                callback(None)
        finally:
            self.is_thinking = False
    
    def get_thinking_message(self):
        """Get current thinking message for display."""
        return self.thinking_message if self.is_thinking else ""
    
    def reset_conversation(self, character_name):
        """Reset conversation history for a character."""
        if character_name in self.conversation_history:
            del self.conversation_history[character_name]


class ChatSystem:
    """AI Chat System that generates responses based on character personality.
    
    This system can use either real AI (via API) or rule-based responses.
    """
    
    def __init__(self, ai_chat=None):
        # Link to AI chat system (if available)
        self.ai_chat = ai_chat
        self.pending_callbacks = {}  # Store callbacks for async AI responses
        
        # Response templates for each personality
        self.fifi_responses = [
            "Oh, that's wonderful to hear! Tell me more!",
            "I'm so happy you're here! How's your day going?",
            "You know, I was just thinking about you!",
            "That's so sweet of you to say! *giggles*",
            "I love spending time with you! What shall we do next?",
            "Your day sounds great! Mine was lovely too, thanks for asking!",
            "Aww, you're the best friend ever! *hugs*",
            "I was wondering when you'd come talk to me!",
            "Gosh, I've missed you! Tell me everything!",
            "That's amazing! I always knew you were special.",
        ]
        
        self.shyel_responses = [
            "O-oh, hello... *fidgets nervously*",
            "You... you want to talk to me? *surprised*",
            "I-I'm not used to this... *looks down*",
            "Th-thank you for being nice to me...",
            "*quietly* That's really kind of you to say...",
            "I-I guess... maybe... you're okay... *blushes*",
            "Um, c-can we keep this between us? *nervous*",
            "*shy smile* You're not so scary after all...",
            "I appreciate that... really I do...",
            "*takes a deep breath* Okay, I can do this...",
        ]
        
        self.grump_responses = [
            "*sighs* What do you want now?",
            "Hmmph. Can't a character get some peace around here?",
            "You're bothering me. Go away. ...Fine, what is it?",
            "*grumbles* I was having a nice nap before you showed up.",
            "Oh, great. Another person who wants something from me.",
            "*rolls eyes* Let me guess, you want me to be happy?",
            "This better be important... *crosses arms*",
            "*mutters* Kids these days, always wanting to chat...",
            "Fine. But make it quick. I have important things to do.",
            "Ugh, fine. I'll play along. What do you want?",
        ]
        
        self.pippin_responses = [
            "WHOOOO! That sounds AMAZING! Let's do it!",
            "Haha, you're the best! Wanna play a game?",
            "*bounces up and down* Ooh ooh, tell me more!",
            "Wowzers! That's so cool! I love your energy!",
            "Let's have an adventure! What should we explore first?",
            "*excited squeal* I knew you were fun!",
            "High five! *jumps* We're gonna have SO much fun!",
            "Golly gee! You really know how to make a day exciting!",
            "*cartwheels* Can we do that again? Please please please?",
            "You're awesome! Wanna cause some chaos with me?",
        ]
        
        # Question responses
        self.question_responses = {
            config.PERSONALITY_FRIENDLY: [
                "Oh, what a lovely question! Let me think...",
                "You know, I've been wondering the same thing!",
                "That's such a thoughtful question! Here, let me tell you...",
                "I'm so glad you asked! Here's what I think...",
            ],
            config.PERSONALITY_SHY: [
                "*looks around nervously* You... you want to know?",
                "Um, I-I suppose... *whispers* let me tell you...",
                "*takes a moment* I think... maybe...",
                "*nervous* Are you sure you want to hear my thoughts?",
            ],
            config.PERSONALITY_GRUMPY: [
                "*sighs heavily* You're really asking me questions now?",
                "*grumbles* Fine, if you must know...",
                "*rolls eyes* Honestly, people these days... fine.",
                "*mutters* Here we go again... well, here you go...",
            ],
            config.PERSONALITY_PLAYFUL: [
                "Ooooh, a question! Let me think out loud!",
                "*gasps* That's a fun one! Okay, here's my thoughts...",
                "Hmm, let me bounce some ideas around! *thinks*",
                "*taps chin* Great question! Watch this...",
            ],
        }
        
        self.greeting_responses = {
            config.PERSONALITY_FRIENDLY: [
                "Hi there, friend! I've been waiting for you!",
                "Oh yay, you came to see me! *waves happily*",
                "Hello hello! So happy you're here!",
                "*bright smile* Hey there, superstar!",
            ],
            config.PERSONALITY_SHY: [
                "*looks up slowly* H-hi...",
                "*soft whisper* Oh, hello...",
                "*small wave* Um, hi there...",
                "*almost inaudible* Hey...",
            ],
            config.PERSONALITY_GRUMPY: [
                "*dry tone* Oh, it's you.",
                "*barely looks up* What do you want?",
                "*sighs* Let me guess, you want to chat?",
                "*grumbles* Fine, hello. Happy now?",
            ],
            config.PERSONALITY_PLAYFUL: [
                "YO! You're here! WOOO! *does a flip*",
                "*bounces over* Hey hey hey! What's happening!" ,
                "*excited* OMG hi! I've been SO bored!",
                "*waves frantically* Over here! Let's hang out!",
            ],
        }
    
    def generate_response(self, character, message):
        """Generate an AI response based on character's personality and message."""
        msg_lower = message.lower().strip()
        
        # Check for greetings
        greetings = ['hello', 'hi', 'hey', 'howdy', 'hiya', 'greetings']
        if any(greet in msg_lower for greet in greetings):
            responses = self.greeting_responses.get(character.personality, ["I see..."])
            return random.choice(responses)
        
        # Check for questions
        if '?' in message:
            responses = self.question_responses.get(character.personality, ["Interesting question..."])
            return random.choice(responses) + " " + random.choice(self._get_responses_by_personality(character.personality))
        
        # Check for specific keywords
        keywords = self._analyze_keywords(msg_lower, character.personality, character.name)
        if keywords:
            return keywords
        
        # Default personality-based responses
        return random.choice(self._get_responses_by_personality(character.personality))
    
    def _get_responses_by_personality(self, personality):
        """Get response list for a personality type."""
        if personality == config.PERSONALITY_FRIENDLY:
            return self.fifi_responses
        elif personality == config.PERSONALITY_SHY:
            return self.shyel_responses
        elif personality == config.PERSONALITY_GRUMPY:
            return self.grump_responses
        elif personality == config.PERSONALITY_PLAYFUL:
            return self.pippin_responses
        return ["I see..."]
    
    def _analyze_keywords(self, message, personality, character_name):
        """Analyze message for keywords and generate appropriate responses."""
        # Love/affection keywords
        if any(word in message for word in ['love', 'like', 'care', 'miss', 'happy']):
            if personality == config.PERSONALITY_FRIENDLY:
                return random.choice([
                    "*beams* I love you too! You're the best!",
                    "Aww, that makes my heart go all warm and fuzzy! *hugs*",
                    "I love you so much too! Let's be best friends forever!",
                ])
            elif personality == config.PERSONALITY_SHY:
                return random.choice([
                    "*blushes intensely* You... you really mean that? *smiles shyly*",
                    "*looks down, smiling* I-I think I love you too...",
                    "*can't stop smiling* That's... that's really nice to hear...",
                ])
            elif personality == config.PERSONALITY_GRUMPY:
                return random.choice([
                    "*slightly flustered* Yeah, yeah, love you too... whatever.",
                    "*looks away* Don't get all mushy on me... *small smile*",
                    "*crosses arms* Hmph. Fine. You're... not so bad yourself.",
                ])
            elif personality == config.PERSONALITY_PLAYFUL:
                return random.choice([
                    "WOOO! I LOVE YOU TOO! *spins around excitedly*",
                    "*tackle hug* I LOVE YOU! YOU'RE THE BEST! *bounces*",
                    "Aww, that's SO sweet! I wanna squeeze you! *giggles*",
                ])
        
        # Sad/down keywords
        if any(word in message for word in ['sad', 'sorry', 'miss', 'lonely', 'bad']):
            if personality == config.PERSONALITY_FRIENDLY:
                return random.choice([
                    "Oh no, I'm here for you! *hugs* Everything will be okay!",
                    "Aww, don't be sad! You have me now! *pat pat*",
                    "*concerned* I'm sorry you're feeling that way. Want to talk about it?",
                ])
            elif personality == config.PERSONALITY_SHY:
                return random.choice([
                    "*moves closer* I-I understand... *offers gentle hand*",
                    "*softly* I get that way too sometimes... *quiet company*",
                    "*nods* It's okay to feel that way... I'm here...",
                ])
            elif personality == config.PERSONALITY_GRUMPY:
                return random.choice([
                    "*awkward pat* There, there. Don't be dramatic.",
                    "*uncomfortable* Fine, I'm here. Don't make it weird.",
                    "*sighs* What even is there to be sad about? Get it together.",
                ])
            elif personality == config.PERSONALITY_PLAYFUL:
                return random.choice([
                    "HEY! No sadness allowed! *tries to make you smile*",
                    "*pouts* Don't be sad! Let me cheer you up! *does silly dance*",
                    "NOO! I won't let you be sad! *gives big hug*",
                ])
        
        # Fun/play keywords
        if any(word in message for word in ['play', 'fun', 'game', 'jump', 'run', 'dance']):
            if personality == config.PERSONALITY_FRIENDLY:
                return random.choice([
                    "Ooh, that sounds fun! Let's do it together!",
                    "I'd love to play with you! *claps hands excitedly*",
                    "That sounds wonderful! Lead the way!",
                ])
            elif personality == config.PERSONALITY_SHY:
                return random.choice([
                    "*nervous but excited* I-I'll try... please be patient with me...",
                    "Um, maybe... if you don't mind a beginner... *smiles*",
                    "*quietly* I'd like that... if you show me how...",
                ])
            elif personality == config.PERSONALITY_GRUMPY:
                return random.choice([
                    "*exasperated sigh* Fine, I'll play. But just this once.",
                    "*stands up slowly* You really want to do this? Fine.",
                    "*cracks knuckles* Don't expect me to enjoy it though.",
                ])
            elif personality == config.PERSONALITY_PLAYFUL:
                return random.choice([
                    "YES! LET'S GO! *immediately starts bouncing*",
                    "OH MY GOSH! FINALLY! *can't contain excitement*",
                    "*screams with joy* THIS IS GONNA BE AWESOME!",
                ])
        
        # Food/hunger keywords
        if any(word in message for word in ['food', 'eat', 'hungry', 'yummy', 'delicious']):
            if personality == config.PERSONALITY_FRIENDLY:
                return random.choice([
                    "Ooh, I'm a bit hungry too! Want to share a snack?",
                    "*tummies rumble* Maybe we should get some treats!",
                    "Food is the way to my heart! *giggles*",
                ])
            elif personality == config.PERSONALITY_SHY:
                return random.choice([
                    "*quietly* I guess I could eat... if there's enough...",
                    "*looks down* I... I haven't eaten in a while...",
                    "*nods* Food sounds... nice...",
                ])
            elif personality == config.PERSONALITY_GRUMPY:
                return random.choice([
                    "*stomach growls loudly* Ugh, fine. I AM hungry.",
                    "*grumbles* What's for food? Better not be that awful stuff again.",
                    "*crosses arms* I suppose I could eat. Eventually.",
                ])
            elif personality == config.PERSONALITY_PLAYFUL:
                return random.choice([
                    "FOOOOD! *drools* Let's get some nom noms!",
                    "*bounces* OOH I LOVE FOOD! Pizza? Burgers? CAKE?",
                    "*eyes widen* Did someone say food?! Count me in!",
                ])
        
        # Name check - now uses the character_name parameter
        character_names_lower = {'fifi': 'Fifi', 'shyel': 'Shyel', 'grump': 'Grump', 'pippin': 'Pippin'}
        if found_name := next((name for name_key, name in character_names_lower.items() if name_key in message), None):
            if personality == config.PERSONALITY_FRIENDLY:
                return random.choice([
                    "That's my name! *waves* Nice to meet you!",
                    "Yep, that's me! *happy wiggle*",
                    "You remembered my name! *tears of joy*",
                ])
            elif personality == config.PERSONALITY_SHY:
                return random.choice([
                    "*softly* Yes... that's my name...",
                    "*nods* M-my name... thank you for asking...",
                    "*quiet voice* You know my name... *small smile*",
                ])
            elif personality == config.PERSONALITY_GRUMPY:
                return random.choice([
                    "*points at self* That's me. Grump. The grumpy one.",
                    "*flatly* Yep. Grump. Don't wear it out.",
                    "What about my name? *suspicious*",
                ])
            elif personality == config.PERSONALITY_PLAYFUL:
                return random.choice([
                    "THAT'S ME! Pippin! The fun one! *strikes pose*",
                    "*does jazz hands* The one and only Pippin! WOO!",
                    "You know my name! I'm Pippin! *tumbles happily*",
                ])
        
        # Check for references to other characters
        other_characters = {
            'fifi': ('Fifi', config.PERSONALITY_FRIENDLY),
            'shyel': ('Shyel', config.PERSONALITY_SHY),
            'grump': ('Grump', config.PERSONALITY_GRUMPY),
            'pippin': ('Pippin', config.PERSONALITY_PLAYFUL)
        }
        
        for char_key, (char_name, char_personality) in other_characters.items():
            if char_key in message and char_name != character_name:
                # They mentioned another character
                if personality == config.PERSONALITY_FRIENDLY:
                    return random.choice([
                        f"Oh, you want to talk about {char_name}? They're wonderful!",
                        f"{char_name}? I love them dearly!",
                        f"*smiles* {char_name} is such a dear friend!",
                    ])
                elif personality == config.PERSONALITY_SHY:
                    return random.choice([
                        f"*looks at {char_name}* T-they're nice...",
                        f"{char_name}? *nods quietly* They're okay...",
                        "*whispers* I... I like {char_name}...",
                    ])
                elif personality == config.PERSONALITY_GRUMPY:
                    return random.choice([
                        f"{char_name}? *shrugs* They're tolerable, I guess.",
                        "*grumbles* {char_name} is... fine, I suppose.",
                        f"*mutters* What about {char_name}?",
                    ])
                elif personality == config.PERSONALITY_PLAYFUL:
                    return random.choice([
                        f"OH! {char_name}! They're the BEST!",
                        f"*bounces* {char_name}! We should all play together!",
                        f"{char_name}? OMG I LOVE {char_name}!",
                    ])
        
        return None
    
    def generate_response_async(self, character, message, callback, all_characters=None):
        """Generate response using AI if available, otherwise use rule-based."""
        if self.ai_chat and self.ai_chat.is_available:
            # Use AI - this will call callback when response is ready
            return self.ai_chat.generate_response(character, message, callback, all_characters)
        else:
            # Use rule-based immediately
            return self.generate_response(character, message)
    
    def handle_ai_response(self, character, response):
        """Handle the AI response, falling back to rule-based if needed."""
        if response:
            # Clean the response (remove code blocks, etc.)
            return clean_ai_response(response)
        else:
            # AI failed, use fallback
            return config.AI_FALLBACK_MESSAGES.get(character.personality, 
                "*looks confused*")
    
    def generate_global_responses(self, message, characters, callback):
        """Generate responses from all characters for a global message."""
        if self.ai_chat and self.ai_chat.is_available:
            # Use AI for each character
            return self.ai_chat.generate_global_response(message, characters, callback)
        else:
            # Use rule-based immediately
            responses = []
            for char in characters:
                resp = self.generate_response(char, message)
                responses.append((char, resp))
            return callback(responses)
