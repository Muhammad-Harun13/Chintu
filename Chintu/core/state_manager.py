from __future__ import annotations

from dataclasses import dataclass, field
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
    logs: list[str] = field(default_factory=list)
    transcript_query: str = ""
    transcript_response: str = ""
    ui_ask_ai: bool = False
    ui_commands: bool = False
    audio_level: float = 0.0


class StateManager:
    def __init__(self, bus: EventBus):
        self._bus = bus
        self._state = RobotState()
        self._lock = Lock()
        # ANSI shell colors
        self._colors = {
            "reset": "\033[0m",
            "cyan": "\033[96m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "red": "\033[91m",
            "bold": "\033[1m"
        }

    @property
    def state(self) -> RobotState:
        with self._lock:
            # Return a shallow copy to prevent external mutation issues
            return RobotState(
                emotion=self._state.emotion,
                last_interaction_ts=self._state.last_interaction_ts,
                logs=list(self._state.logs),
                transcript_query=self._state.transcript_query,
                transcript_response=self._state.transcript_response,
                ui_ask_ai=self._state.ui_ask_ai,
                ui_commands=self._state.ui_commands,
                audio_level=self._state.audio_level
            )

    def touch_interaction(self) -> None:
        with self._lock:
            self._state.last_interaction_ts = monotonic()

    def set_emotion(self, emotion: Emotion) -> None:
        with self._lock:
            if self._state.emotion == emotion:
                return
            self._state.emotion = emotion
            print(f"{self._colors['yellow']}[STATE]{self._colors['reset']} Emotion changed to: {self._colors['bold']}{emotion.value}{self._colors['reset']}")
        self._bus.publish("emotion_changed", emotion)

    def add_log(self, text: str) -> None:
        with self._lock:
            self._state.logs.append(text)
            if len(self._state.logs) > 100:
                self._state.logs.pop(0)
            print(f"{self._colors['green']}[LOG]{self._colors['reset']} {text}")
        self._bus.publish("log_added", text)

    def set_transcript(self, query: str | None = None, response: str | None = None) -> None:
        with self._lock:
            if query is not None:
                self._state.transcript_query = query
                if query:
                    print(f"{self._colors['cyan']}[AI]{self._colors['reset']} {self._colors['bold']}User:{self._colors['reset']} {query}")
            if response is not None:
                self._state.transcript_response = response
                if response:
                    print(f"{self._colors['cyan']}[AI]{self._colors['reset']} {self._colors['bold']}Chintu:{self._colors['reset']} {response}")
        self._bus.publish("transcript_updated", {"query": query, "response": response})

    def set_ui_states(self, ask_ai: bool | None = None, commands: bool | None = None) -> None:
        with self._lock:
            if ask_ai is not None:
                self._state.ui_ask_ai = ask_ai
            if commands is not None:
                self._state.ui_commands = commands
        self._bus.publish("ui_state_changed", {"ask_ai": ask_ai, "commands": commands})

    def update_audio_level(self, level: float) -> None:
        with self._lock:
            self._state.audio_level = level
        self._bus.publish("audio_level_updated", level)
