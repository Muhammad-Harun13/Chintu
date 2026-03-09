from __future__ import annotations
import speech_recognition as sr
from core.config import VoiceConfig
from core.state_manager import StateManager, Emotion
from utils.logger import get_logger

logger = get_logger(__name__)

class Listener:
    """Speech-to-text adapter using SpeechRecognition library."""

    def __init__(self, state: StateManager, config: VoiceConfig) -> None:
        self.state = state
        self.config = config
        self.recognizer = sr.Recognizer()

    def listen(self, prompt: str = "You> ") -> str:
        logger.info("Listening for speech (Device Index: %s)...", self.config.mic_index)
        self.state.add_log(f"Microphone active (Device {self.config.mic_index}): listening...")
        
        try:
            with sr.Microphone(device_index=self.config.mic_index) as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=15, phrase_time_limit=20)
            
            text = self.recognizer.recognize_google(audio)
            logger.info("User Voice Input: %s", text)
            return text.strip()

        except sr.WaitTimeoutError:
            logger.warning("Listening timed out.")
            self.state.add_log("No speech detected (timeout).")
            return ""
        except sr.UnknownValueError:
            logger.warning("Google Speech Recognition could not understand audio")
            self.state.add_log("Speech not understood.")
            return ""
        except Exception as e:
            logger.error("Speech Recognition error: %s", e)
            self.state.add_log(f"Mic error: {str(e)[:30]}")
            return ""