from __future__ import annotations
from core.config import MotorConfig
from motion.hardware_interface import GPIOMotorController, HardwareController
from utils.logger import get_logger

logger = get_logger(__name__)


class MotorDriver:
    def __init__(self, config: MotorConfig, controller: HardwareController | None = None):
        self.cfg = config
        self.controller = controller or GPIOMotorController(config)
        logger.info("MotorDriver initialized with %s", self.controller.__class__.__name__)

    def _apply(self, a1: int, a2: int, b1: int, b2: int, speed: int) -> None:
        self.controller.apply(a1, a2, b1, b2, speed)

    def forward(self, speed: int = 60) -> None:
        self._apply(1, 0, 1, 0, speed)

    def backward(self, speed: int = 60) -> None:
        self._apply(0, 1, 0, 1, speed)

    def left(self, speed: int = 55) -> None:
        self._apply(0, 1, 1, 0, speed)

    def right(self, speed: int = 55) -> None:
        self._apply(1, 0, 0, 1, speed)

    def stop(self) -> None:
        self._apply(0, 0, 0, 0, 0)

    def cleanup(self) -> None:
        self.controller.cleanup()
