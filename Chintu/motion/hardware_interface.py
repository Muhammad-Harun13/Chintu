from __future__ import annotations
from abc import ABC, abstractmethod
from core.config import MotorConfig
from utils.logger import get_logger

logger = get_logger(__name__)

try:
    import RPi.GPIO as GPIO
except Exception:
    GPIO = None


class HardwareController(ABC):
    @abstractmethod
    def apply(self, a1: int, a2: int, b1: int, b2: int, speed: int) -> None:
        pass

    @abstractmethod
    def cleanup(self) -> None:
        pass


class GPIOMotorController(HardwareController):
    def __init__(self, config: MotorConfig):
        self.cfg = config
        self._enabled = GPIO is not None
        self._pwm_a = None
        self._pwm_b = None
        if self._enabled:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            pins = [config.ena_pin, config.in1_pin, config.in2_pin, config.enb_pin, config.in3_pin, config.in4_pin]
            for p in pins:
                GPIO.setup(p, GPIO.OUT)
            self._pwm_a = GPIO.PWM(config.ena_pin, config.pwm_hz)
            self._pwm_b = GPIO.PWM(config.enb_pin, config.pwm_hz)
            self._pwm_a.start(0)
            self._pwm_b.start(0)
        else:
            logger.warning("RPi.GPIO unavailable: running in simulation mode")

    def apply(self, a1: int, a2: int, b1: int, b2: int, speed: int) -> None:
        speed = max(0, min(100, speed))
        if not self._enabled:
            logger.info("Hardware Sim: a(%s,%s) b(%s,%s) speed=%s", a1, a2, b1, b2, speed)
            return
        GPIO.output(self.cfg.in1_pin, a1)
        GPIO.output(self.cfg.in2_pin, a2)
        GPIO.output(self.cfg.in3_pin, b1)
        GPIO.output(self.cfg.in4_pin, b2)
        self._pwm_a.ChangeDutyCycle(speed)
        self._pwm_b.ChangeDutyCycle(speed)

    def cleanup(self) -> None:
        if self._enabled:
            if self._pwm_a: self._pwm_a.stop()
            if self._pwm_b: self._pwm_b.stop()
            GPIO.cleanup()


class SerialController(HardwareController):
    """Placeholder for future serial-based hardware control"""
    def __init__(self, port: str = "COM3", baud: int = 9600):
        self.port = port
        self.baud = baud
        logger.info("Initializing SerialController on %s", port)

    def apply(self, a1: int, a2: int, b1: int, b2: int, speed: int) -> None:
        logger.info("Serial Command: %s,%s,%s,%s,%s", a1, a2, b1, b2, speed)

    def cleanup(self) -> None:
        logger.info("Closing SerialController")
