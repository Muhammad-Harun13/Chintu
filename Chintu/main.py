from __future__ import annotations

import signal
import threading
from datetime import datetime
from time import monotonic

from ai.gemini_api import GeminiAPI
from ai.local_llama import LocalLlama
from ai.router import AIRouter
from core.config import CONFIG
from core.event_bus import EventBus
from core.state_manager import Emotion, StateManager
from display.eyes_engine import EyesEngine
from motion.motor_driver import MotorDriver
from motion.patrol import PatrolRoutine
from utils.logger import get_logger
from vision.camera import Camera
from vision.scanner import SceneScanner
from voice.listen import Listener
from voice.speak import Speaker
from voice.wakeword import WakeWordDetector

logger = get_logger(__name__)


class ChintuApp:
    def __init__(self):
        self.bus = EventBus()
        self.state = StateManager(self.bus)
        self.eyes = EyesEngine(
            self.state,
            CONFIG.display.width,
            CONFIG.display.height,
            CONFIG.display.fps,
            CONFIG.display.fullscreen,
        )
        self.motor = MotorDriver(CONFIG.motor)
        self.speaker = Speaker()
        self.listener = Listener(CONFIG.voice)
        self.local = LocalLlama(CONFIG.ai)
        self.gemini = GeminiAPI(CONFIG.ai)
        self.router = AIRouter(self.local, self.gemini)

        self.camera = Camera(CONFIG.camera)
        self.scanner = SceneScanner(self.camera, self.gemini, self.speaker, self.state)
        logger.info(self.camera.status_message())

        self.patrol = PatrolRoutine(self.motor, self.state)
        self.wake = WakeWordDetector(self.on_wake_word, CONFIG.voice)
        self.running = True
        self._wake_event = threading.Event()

    def on_wake_word(self):
        self._wake_event.set()

    def start(self):
        self.eyes.start()
        self.wake.start()
        logger.info("Chintu started. Type text after wake trigger.")

        def handle_sig(*_):
            self.running = False

        signal.signal(signal.SIGINT, handle_sig)

        while self.running:
            if monotonic() - self.state.state.last_interaction_ts > CONFIG.voice.inactivity_sleep_s:
                self.state.set_emotion(Emotion.SLEEPY)

            if not self._wake_event.wait(timeout=0.2):
                continue
            self._wake_event.clear()

            self.state.touch_interaction()
            self.state.set_emotion(Emotion.LISTENING)
            text = self.listener.listen()
            if not text:
                self.state.set_emotion(Emotion.IDLE)
                continue

            self.state.set_emotion(Emotion.THINKING)
            route = self.router.route(text)
            logger.debug("Route result: kind=%s action=%s", route.kind, route.action)
            self.handle_route(route)

        self.shutdown()

    def handle_route(self, route):
        logger.debug("Handling route: %s", route)
        if route.kind == "DIRECT":
            action = route.action
            if action == "forward":
                self.state.set_emotion(Emotion.MOVING)
                self.motor.forward()
                self.speaker.say("Moving forward")
            elif action == "backward":
                self.state.set_emotion(Emotion.MOVING)
                self.motor.backward()
                self.speaker.say("Moving backward")
            elif action == "left":
                self.state.set_emotion(Emotion.MOVING)
                self.motor.left()
                self.speaker.say("Turning left")
            elif action == "right":
                self.state.set_emotion(Emotion.MOVING)
                self.motor.right()
                self.speaker.say("Turning right")
            elif action == "stop":
                self.motor.stop()
                self.state.set_emotion(Emotion.IDLE)
                self.speaker.say("Stopped")
            elif action == "time":
                now = datetime.now().strftime("%I:%M %p")
                self.state.set_emotion(Emotion.HAPPY)
                self.speaker.say(f"It is {now}")
            elif action == "scan":
                self.patrol.start_scan(5)
                self.scanner.scan_and_describe()
            elif action == "sleep":
                self.state.set_emotion(Emotion.SLEEPY)
                self.speaker.say("Entering sleepy mode")
        else:
            self.state.set_emotion(Emotion.HAPPY)
            self.speaker.say(route.response or "Okay")
            self.state.set_emotion(Emotion.IDLE)

    def shutdown(self):
        logger.info("Shutting down Chintu")
        self.wake.stop()
        self.eyes.stop()
        self.motor.cleanup()
        self.camera.close()


if __name__ == "__main__":
    app = ChintuApp()
    app.start()
