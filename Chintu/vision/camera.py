from __future__ import annotations

from pathlib import Path

from core.config import CameraConfig
from utils.logger import get_logger

logger = get_logger(__name__)

try:
    from picamera2 import Picamera2
except Exception:
    Picamera2 = None


class Camera:
    """Safe Picamera2 wrapper.

    Handles Raspberry Pi camera-missing cases gracefully so app startup does not crash.
    """

    def __init__(self, config: CameraConfig | None = None) -> None:
        self.config = config
        self.cam = None
        self.available = False
        self.last_error: str | None = None

        if not Picamera2:
            self.last_error = "Picamera2 not installed"
            logger.warning("Camera not connected: Picamera2 is not installed")
            return

        try:
            cameras = Picamera2.global_camera_info()
            logger.debug("Camera discovery returned: %s", cameras)
            if not cameras:
                self.last_error = "No Pi Camera detected"
                logger.warning("Camera not connected: no Pi camera detected")
                return

            self.cam = Picamera2(camera_num=0)
            size = (640, 480)
            if self.config is not None:
                size = (self.config.width, self.config.height)
            cfg = self.cam.create_still_configuration(main={"size": size})
            self.cam.configure(cfg)
            self.cam.start()
            self.available = True
            self.last_error = None
            logger.info("Camera initialized successfully (%sx%s)", size[0], size[1])
        except Exception as exc:
            self.last_error = str(exc)
            logger.exception("Camera not connected/failed to initialize: %s", exc)
            self.cam = None
            self.available = False

    def capture_jpeg(self) -> bytes:
        if not self.cam or not self.available:
            msg = self.last_error or "Camera unavailable"
            raise RuntimeError(msg)

        path = "/tmp/chintu_latest.jpg"
        logger.debug("Capturing frame to %s", path)
        self.cam.capture_file(path)
        return Path(path).read_bytes()

    def close(self) -> None:
        if self.cam:
            try:
                self.cam.stop()
                logger.debug("Camera stopped")
            except Exception:
                pass

    def status_message(self) -> str:
        if self.available:
            return "Camera connected"
        return f"Camera not connected: {self.last_error or 'Unknown camera error'}"
