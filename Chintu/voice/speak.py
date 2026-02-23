from __future__ import annotations

from utils.logger import get_logger

logger = get_logger(__name__)

try:
    import pyttsx3
except Exception:
    pyttsx3 = None


class Speaker:
    def __init__(self):
        self.engine = pyttsx3.init() if pyttsx3 else None
        if self.engine:
            self.engine.setProperty("rate", 165)

    def say(self, text: str) -> None:
        logger.info("TTS: %s", text)
        if not self.engine:
            return
        self.engine.say(text)
        self.engine.runAndWait()
