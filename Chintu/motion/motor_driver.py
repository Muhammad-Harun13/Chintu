from __future__ import annotations

from core.config import MotorConfig
from utils.logger import get_logger

logger = get_logger(__name__)

try:
    import RPi.GPIO as GPIO
except Exception:
    GPIO = None


class MotorDriver:
    def __init__(self, config: MotorConfig):
        self.cfg = config
        self.current_speed = config.default_speed
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

    def _apply(self, a1: int, a2: int, b1: int, b2: int, speed: int | None = None) -> None:
        if speed is None:
            speed = self.current_speed
        speed = max(0, min(100, speed))
        
        if not self._enabled:
            logger.info("motor simulate a(%s,%s) b(%s,%s) speed=%s", a1, a2, b1, b2, speed)
            return

        GPIO.output(self.cfg.in1_pin, a1)
        GPIO.output(self.cfg.in2_pin, a2)
        GPIO.output(self.cfg.in3_pin, b1)
        GPIO.output(self.cfg.in4_pin, b2)
        self._pwm_a.ChangeDutyCycle(speed)
        self._pwm_b.ChangeDutyCycle(speed)

    def forward(self, speed: int | None = None) -> None:
        self._apply(1, 0, 1, 0, speed)

    def backward(self, speed: int | None = None) -> None:
        self._apply(0, 1, 0, 1, speed)

    def left(self, speed: int | None = None) -> None:
        # User Logic: (1,0) and (0,1)
        self._apply(1, 0, 0, 1, speed)

    def right(self, speed: int | None = None) -> None:
        # User Logic: (0,1) and (1,0)
        self._apply(0, 1, 1, 0, speed)

    def set_speed(self, speed: int) -> None:
        self.current_speed = max(0, min(100, speed))
        logger.info("Motor speed set to %s%%", self.current_speed)

    def increase_speed(self) -> str:
        self.set_speed(self.current_speed + 10)
        return f"Speed increased to {self.current_speed}%"

    def decrease_speed(self) -> str:
        self.set_speed(self.current_speed - 10)
        return f"Speed decreased to {self.current_speed}%"

    def stop(self) -> None:
        self._apply(0, 0, 0, 0, 0)

    def cleanup(self) -> None:
        self.stop()
        if self._enabled:
            self._pwm_a.stop()
            self._pwm_b.stop()
            GPIO.cleanup()
