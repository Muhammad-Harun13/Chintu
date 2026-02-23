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


class StateManager:
    def __init__(self, bus: EventBus):
        self._bus = bus
        self._state = RobotState()
        self._lock = Lock()

    @property
    def state(self) -> RobotState:
        with self._lock:
            return RobotState(self._state.emotion, self._state.last_interaction_ts)

    def touch_interaction(self) -> None:
        with self._lock:
            self._state.last_interaction_ts = monotonic()

    def set_emotion(self, emotion: Emotion) -> None:
        with self._lock:
            if self._state.emotion == emotion:
                return
            self._state.emotion = emotion
        self._bus.publish("emotion_changed", emotion)
