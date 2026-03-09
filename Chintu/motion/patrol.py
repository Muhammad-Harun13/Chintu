from __future__ import annotations

import threading
from time import sleep

from core.state_manager import Emotion, StateManager
from motion.motor_driver import MotorDriver


class PatrolRoutine:
    def __init__(self, motor: MotorDriver, state: StateManager):
        self.motor = motor
        self.state = state
        self._active = False
        self._thread: threading.Thread | None = None

    def start_scan(self, duration_s: float = 4.0):
        if self._active:
            return
        self._active = True
        self._thread = threading.Thread(target=self._run, args=(duration_s,), daemon=True)
        self._thread.start()

    def _run(self, duration_s: float):
        self.state.set_emotion(Emotion.SCANNING)
        half = duration_s / 2
        self.motor.left(35)
        sleep(half)
        self.motor.right(35)
        sleep(half)
        self.motor.stop()
        self.state.set_emotion(Emotion.IDLE)
        self._active = False
