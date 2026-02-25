from __future__ import annotations

import json
import math
import queue
import struct
from queue import Empty

from core.config import VoiceConfig
from core.state_manager import StateManager
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

    def __init__(self, state: StateManager, config: VoiceConfig) -> None:
        self.state = state
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
            logger.error("❌ Microphone ERROR: VOSK model or sounddevice not available. Voice interaction disabled.")
            return ""

        rec = KaldiRecognizer(self.model, 16000)
        audio_q: queue.Queue[bytes] = queue.Queue(maxsize=64)

        def callback(indata, frames, time_info, status):
            if status:
                return
            
            # Calculate audio level (RMS)
            try:
                count = len(indata) // 2
                format = "%dh" % count
                shorts = struct.unpack(format, indata)
                sum_squares = sum(s * s for s in shorts)
                rms = math.sqrt(sum_squares / count) / 32768.0
                self.state.update_audio_level(min(1.0, rms * 5.0)) # Boosted for visual effect
            except Exception:
                pass

            try:
                audio_q.put_nowait(bytes(indata))
            except queue.Full:
                pass

        logger.info("Microphone ON: Listening for your command...")
        self.state.add_log("Microphone active: listening...")
        
        recognized_text = ""
        try:
            with sd.RawInputStream(samplerate=16000, blocksize=4000, dtype="int16", channels=1, callback=callback):
                for i in range(120): # ~30 seconds max
                    from core.state_manager import Emotion
                    if not self.state.state.emotion == Emotion.LISTENING:
                        break
                    try:
                        chunk = audio_q.get(timeout=0.25)
                    except Empty:
                        continue
                    if rec.AcceptWaveform(chunk):
                        result = json.loads(rec.Result())
                        recognized_text = (result.get("text") or "").strip()
                        if recognized_text:
                            logger.info("Speech detected: %s", recognized_text)
                            break
                
                if not recognized_text:
                    final_result = json.loads(rec.FinalResult())
                    recognized_text = (final_result.get("text") or "").strip()
                    if recognized_text:
                        logger.info("Speech detected: %s", recognized_text)
        except Exception as e:
            logger.error("❌ Microphone ERROR: %s", e)
        finally:
            logger.info("🛑 Microphone OFF")
            self.state.update_audio_level(0)
            if not recognized_text:
                self.state.add_log("No speech detected.")
        
        return recognized_text
