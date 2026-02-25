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
                except Exception as e:
                    logger.error("TTS Init Error: %s", e)
            return self._engine

    def say(self, text: str) -> None:
        logger.info("TTS: %s", text)
        engine = self._get_engine()
        if not engine:
            return
        
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            logger.error("TTS Speak Error: %s", e)
