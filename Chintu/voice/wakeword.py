from __future__ import annotations

import queue
from queue import Empty
import struct
import threading
from time import sleep

from core.config import VoiceConfig
from utils.logger import get_logger

logger = get_logger(__name__)

try:
    import pvporcupine
except Exception:
    pvporcupine = None

try:
    import sounddevice as sd
except Exception:
    sd = None


class WakeWordDetector:
    """Wake word detector with Porcupine + microphone and safe fallback."""

    def __init__(self, callback, config: VoiceConfig):
        self.callback = callback
        self.config = config
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True, name="wakeword")
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)

    def _create_porcupine(self):
        if not pvporcupine:
            return None

        kwargs = {}
        if self.config.porcupine_access_key:
            kwargs["access_key"] = self.config.porcupine_access_key

        if self.config.porcupine_keyword_path:
            kwargs["keyword_paths"] = [self.config.porcupine_keyword_path]
        else:
            kwargs["keywords"] = [self.config.wake_word]

        return pvporcupine.create(**kwargs)

    def _run(self):
        if not pvporcupine or not sd:
            logger.warning("Wake word stack unavailable; using simulation mode")
            while self._running:
                sleep(0.25)
            return

        audio_q: queue.Queue[bytes] = queue.Queue(maxsize=32)
        porcupine = None
        stream = None
        try:
            porcupine = self._create_porcupine()
            if porcupine is None:
                raise RuntimeError("Porcupine initialization unavailable")

            def audio_callback(indata, frames, time_info, status):
                if status:
                    return
                try:
                    audio_q.put_nowait(bytes(indata))
                except queue.Full:
                    pass

            stream = sd.RawInputStream(
                samplerate=porcupine.sample_rate,
                blocksize=porcupine.frame_length,
                dtype="int16",
                channels=1,
                callback=audio_callback,
            )
            stream.start()
            logger.info("👂 Wake Word detector ON: Listening for '%s'...", self.config.wake_word)

            while self._running:
                try:
                    frame_bytes = audio_q.get(timeout=0.5)
                except Empty:
                    continue
                pcm = struct.unpack_from("h" * porcupine.frame_length, frame_bytes)
                if porcupine.process(pcm) >= 0:
                    logger.info("🔔 Wake Word DETECTED: %s", self.config.wake_word)
                    self.callback()
        except Exception as exc:
            logger.error("❌ Wake Word detector ERROR: %s", exc)
            while self._running:
                sleep(0.25)
        finally:
            logger.info("🛑 Wake Word detector OFF")
            if stream:
                stream.stop()
                stream.close()
            if porcupine:
                porcupine.delete()

    def trigger_for_test(self):
        self.callback()
