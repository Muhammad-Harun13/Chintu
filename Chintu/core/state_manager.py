from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from threading import Lock
from time import monotonic

from core.event_bus import EventBus


class Emotion(str, Enum):
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    THINKING = "THINKING"
    HAPPY = "HAPPY"
    SAD = "SAD"
    CURIOUS = "CURIOUS"
    ANGRY = "ANGRY"
    SLEEPY = "SLEEPY"
    SCANNING = "SCANNING"
    MOVING = "MOVING"
    ERROR = "ERROR"


@dataclass
class RobotState:
    emotion: Emotion = Emotion.IDLE
    last_interaction_ts: float = monotonic()
    audio_level: float = 0.0
    ask_ai_active: bool = False
    commands_active: bool = False
    last_query: str = ""
    last_response: str = ""
    logs: list[str] = None  # Will be list
    hardware_status: dict = None  # Will be dict
    dashboard_active: bool = False

    def __post_init__(self):
        if self.logs is None:
            self.logs = []
        if self.hardware_status is None:
            self.hardware_status = {"battery": 100, "wifi": "connected", "temp": 35}

class StateManager:
    def __init__(self, bus: EventBus):
        self._bus = bus
        self._state = RobotState()
        self._lock = Lock()

    @property
    def state(self) -> RobotState:
        with self._lock:
            # Shallow copy of the state dataclass to avoid direct mutation issues
            import copy
            return copy.copy(self._state)

    def touch_interaction(self) -> None:
        with self._lock:
            self._state.last_interaction_ts = monotonic()

    def set_emotion(self, emotion: Emotion) -> None:
        with self._lock:
            if self._state.emotion == emotion:
                return
            self._state.emotion = emotion
        self._bus.publish("emotion_changed", emotion)

    def set_ui_states(self, ask_ai: bool | None = None, commands: bool | None = None) -> None:
        with self._lock:
            if ask_ai is not None:
                # print(f"DEBUG: StateManager setting ask_ai={ask_ai}")
                self._state.ask_ai_active = ask_ai
            if commands is not None:
                # print(f"DEBUG: StateManager setting commands={commands}")
                self._state.commands_active = commands
        self._bus.publish("ui_state_changed")

    def set_transcript(self, query: str | None = None, response: str | None = None) -> None:
        with self._lock:
            if query is not None:
                self._state.last_query = query
                self.add_log(f"User: {query}")
            if response is not None:
                self._state.last_response = response
                self.add_log(f"Chintu: {response}")
        self._bus.publish("transcript_updated")

    def add_log(self, message: str) -> None:
        with self._lock:
            if self._state.logs is None:
                self._state.logs = []
            self._state.logs.append(message)
            if len(self._state.logs) > 50:
                self._state.logs.pop(0)
        self._bus.publish("log_added", message)

    def update_hardware(self, key: str, value: any) -> None:
        with self._lock:
            self._state.hardware_status[key] = value
        self._bus.publish("hardware_updated")

    def set_dashboard_active(self, active: bool) -> None:
        with self._lock:
            self._state.dashboard_active = active
        self._bus.publish("ui_mode_changed", active)

    def update_audio_level(self, level: float) -> None:
        with self._lock:
            self._state.audio_level = level
