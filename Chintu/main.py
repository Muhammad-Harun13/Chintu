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
    def __init__(self, bus: EventBus | None = None, state: StateManager | None = None):
        self.bus = bus or EventBus()
        self.state = state or StateManager(self.bus)
        self.eyes = EyesEngine(
            self.state,
            CONFIG.display.width,
            CONFIG.display.height,
            CONFIG.display.fps,
            CONFIG.display.fullscreen,
        )
        self.motor = MotorDriver(CONFIG.motor)
        self.speaker = Speaker()
        self.listener = Listener(self.state, CONFIG.voice)
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

        # Subscribe to UI events
        self.bus.subscribe("ui_ask_ai", self._handle_ui_ask_ai)
        self.bus.subscribe("ui_commands", self._handle_ui_commands)
        self.bus.subscribe("app_quit", self._handle_app_quit)
        self.bus.subscribe("move", self._handle_move)

    def _handle_move(self, direction: str):
        logger.info("UI Move: %s", direction)
        self.state.add_log(f"Manual move: {direction}")
        if direction == "forward":
            self.motor.forward()
        elif direction == "backward":
            self.motor.backward()
        elif direction == "left":
            self.motor.left()
        elif direction == "right":
            self.motor.right()
        elif direction == "stop":
            self.motor.stop()

    def _handle_app_quit(self, _):
        logger.info("UI: App Quit event received")
        self.running = False

    def _handle_ui_ask_ai(self, _):
        # print("DEBUG: ChintuApp._handle_ui_ask_ai triggered")
        def _task():
            logger.info("UI Ask AI: Triggered")
            self.state.set_ui_states(ask_ai=True)
            self.state.set_emotion(Emotion.CURIOUS)
            self.state.set_transcript(query="", response="") # Clear old ones
            self.speaker.say("I'm listening. How can I help?")
            text = self.listener.listen()
            if not text:
                self.speaker.say("I didn't catch that.")
                self.state.set_emotion(Emotion.IDLE)
                self.state.set_ui_states(ask_ai=False)
                return

            self.state.set_transcript(query=text)
            self.state.set_emotion(Emotion.THINKING)
            try:
                response = self.gemini.ask_text(text)
                self.state.set_transcript(response=response)
                self.state.set_emotion(Emotion.HAPPY)
                self.speaker.say(response)
            except Exception as e:
                logger.error("AI Error: %s", e)
                self.state.set_emotion(Emotion.ERROR)
                self.speaker.say("Sorry, I'm having trouble connecting to my brain.")
            
            self.state.set_emotion(Emotion.IDLE)
            self.state.set_ui_states(ask_ai=False)
            # Clear transcript after 10 seconds
            threading.Timer(10.0, lambda: self.state.set_transcript(query="", response="")).start()

        threading.Thread(target=_task, daemon=True).start()

    def _handle_ui_commands(self, _):
        def _task():
            logger.info("UI Commands: Triggered")
            self.state.set_ui_states(commands=True)
            self.state.set_emotion(Emotion.SCANNING)
            self.state.set_transcript(query="", response="")
            self.speaker.say("What command should I execute?")
            text = self.listener.listen()
            if not text:
                self.state.set_emotion(Emotion.IDLE)
                self.state.set_ui_states(commands=False)
                return

            self.state.set_transcript(query=text)
            self.state.set_emotion(Emotion.THINKING)
            t = text.lower()
            
            executed = False
            resp_text = ""
            if "forward" in t:
                self.motor.forward()
                resp_text = "Moving forward"
                executed = True
            elif "backward" in t:
                self.motor.backward()
                resp_text = "Moving backward"
                executed = True
            elif "left" in t:
                self.motor.left()
                resp_text = "Turning left"
                executed = True
            elif "right" in t:
                self.motor.right()
                resp_text = "Turning right"
                executed = True
            
            if executed:
                self.state.set_transcript(response=resp_text)
                self.speaker.say(resp_text)
                self.state.set_emotion(Emotion.MOVING)
            else:
                resp_err = f"I don't know the command {text}"
                self.state.set_transcript(response=resp_err)
                self.speaker.say(resp_err)
                self.state.set_emotion(Emotion.IDLE)
            
            self.state.set_ui_states(commands=False)
            threading.Timer(10.0, lambda: self.state.set_transcript(query="", response="")).start()

        threading.Thread(target=_task, daemon=True).start()

    def on_wake_word(self):
        self._wake_event.set()

    def start(self):
        self.eyes.start()
        self.wake.start()
        logger.info("Chintu started. Reachable via wake word or UI buttons.")
        self.state.add_log("System started. Ready for commands.")

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
