from __future__ import annotations

import json
import queue
from queue import Empty

from core.config import VoiceConfig
from utils.logger import get_logger

logger = get_logger(__name__)

try:
    from vosk import KaldiRecognizer, Model
except Exception:
    Model = None
    KaldiRecognizer = None

try:
    import sounddevice as sd
except Exception:
    sd = None


class Listener:
    """Speech-to-text adapter. Uses VOSK when available, else console fallback."""

    def __init__(self, config: VoiceConfig) -> None:
        self.model = None
        self.config = config
        if Model and sd:
            try:
                self.model = Model(config.vosk_model_path)
                logger.info("VOSK model loaded from %s", config.vosk_model_path)
            except Exception as exc:
                logger.warning("VOSK model not loaded (%s), using text fallback", exc)

    def listen(self, prompt: str = "You> ") -> str:
        if not self.model or not KaldiRecognizer or not sd:
            try:
                return input(prompt).strip()
            except EOFError:
                logger.warning("No stdin available for listener")
                return ""

        rec = KaldiRecognizer(self.model, 16000)
        audio_q: queue.Queue[bytes] = queue.Queue(maxsize=64)

        def callback(indata, frames, time_info, status):
            if status:
                return
            try:
                audio_q.put_nowait(bytes(indata))
            except queue.Full:
                pass

        logger.info("Listening for speech...")
        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16", channels=1, callback=callback):
            for _ in range(120):
                try:
                    chunk = audio_q.get(timeout=0.5)
                except Empty:
                    continue
                if rec.AcceptWaveform(chunk):
                    result = json.loads(rec.Result())
                    text = (result.get("text") or "").strip()
                    if text:
                        return text

        final_result = json.loads(rec.FinalResult())
        return (final_result.get("text") or "").strip()
