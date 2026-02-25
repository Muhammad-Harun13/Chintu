from __future__ import annotations

import signal
import threading
from utils.logger import get_logger

logger = get_logger(__name__)

try:
    import pyttsx3
except Exception:
    pyttsx3 = None


class Speaker:
    def __init__(self):
        self._engine = None
        self._lock = threading.Lock()

    def _get_engine(self):
        with self._lock:
            if self._engine is None and pyttsx3:
                try:
                    # Initialize COM for the current thread on Windows
                    import pythoncom
                    pythoncom.CoInitialize()
                except Exception:
                    pass
                
                try:
                    self._engine = pyttsx3.init()
                    self._engine.setProperty("rate", 165)
                    
                    # Try to set a female voice
                    voices = self._engine.getProperty("voices")
                    for v in voices:
                        name = v.name.lower()
                        if "female" in name or "girl" in name or "zira" in name or "hazel" in name:
                            self._engine.setProperty("voice", v.id)
                            logger.info("Speaker: Selected female voice - %s", v.name)
                            break
                except Exception as e:
                    logger.error("TTS Init Error: %s", e)
            return self._engine

    def say(self, text: str) -> None:
        logger.info("🔊 Speaking: %s", text)
        engine = self._get_engine()
        if not engine:
            return
        
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            logger.error("TTS Speak Error: %s", e)
