from __future__ import annotations
import os
import threading
import pygame
from gtts import gTTS
from utils.logger import get_logger

logger = get_logger(__name__)

class Speaker:
    """TTS Speaker using Google TTS (gTTS) and Pygame for playback."""
    
    def __init__(self):
        self._lock = threading.Lock()
        if not pygame.mixer.get_init():
            pygame.mixer.init()

    def say(self, text: str) -> None:
        if not text:
            return
            
        logger.info("TTS: %s", text)
        
        with self._lock:
            try:
                # Generate TTS
                tts = gTTS(text=text, lang='en')
                filename = "voice.mp3"
                tts.save(filename)
                
                # Play using pygame mixer
                pygame.mixer.music.load(filename)
                pygame.mixer.music.play()
                
                # Wait for playback to finish
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                    
                # Cleanup
                pygame.mixer.music.unload()
                if os.path.exists(filename):
                    try:
                        os.remove(filename)
                    except Exception:
                        pass
            except Exception as e:
                logger.error("TTS Speak Error: %s", e)
