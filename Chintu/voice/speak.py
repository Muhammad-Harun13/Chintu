from __future__ import annotations

import queue
import threading
from utils.logger import get_logger

logger = get_logger(__name__)

try:
    import pyttsx3
except Exception:
    pyttsx3 = None

class Speaker:
    def __init__(self):
        self._queue = queue.Queue()
        self._thread = threading.Thread(target=self._worker, daemon=True, name="SpeakerWorker")
        if pyttsx3:
            self._thread.start()
            logger.info("Speaker: Worker thread started")

    def _worker(self):
        # Initialize COM and Engine once in this dedicated thread
        engine = None
        try:
            import pythoncom
            pythoncom.CoInitialize()
        except Exception:
            pass
            
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", 165)
            
            # Try to set a female voice
            voices = engine.getProperty("voices")
            for v in voices:
                name = v.name.lower()
                if "female" in name or "girl" in name or "zira" in name or "hazel" in name:
                    engine.setProperty("voice", v.id)
                    logger.info("Speaker: Selected female voice - %s", v.name)
                    break
        except Exception as e:
            logger.error("TTS: Initialization Error: %s", e)
            return

        while True:
            try:
                text = self._queue.get()
                if text is None: break
                
                logger.info("Speaking: %s", text)
                engine.say(text)
                engine.runAndWait()
                self._queue.task_done()
            except Exception as e:
                logger.error("TTS: Error during speaking: %s", e)

    def say(self, text: str) -> None:
        if not pyttsx3:
            logger.warning("TTS: pyttsx3 not available. Skipping: %s", text)
            return
        self._queue.put(text)

    def wait_until_done(self):
        self._queue.join()
