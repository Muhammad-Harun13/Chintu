from __future__ import annotations

from dataclasses import dataclass

from core.state_manager import Emotion


@dataclass(frozen=True)
class EmotionProfile:
    eye_open: float
    pupil_size: float
    glow: float
    blink_min_s: float
    blink_max_s: float
    brow_tilt: float
    tilt_l: float = 0.0      # Left eye tilt in radians
    tilt_r: float = 0.0      # Right eye tilt in radians
    squash_x: float = 1.0    # Horizontal scale
    squash_y: float = 1.0    # Vertical scale
    brow_y: float = 0.0      # Vertical offset for eyebrows
    mouth_width: float = 0.0 # 0.0 to 1.0
    mouth_curve: float = 0.0 # -1.0 (frown) to 1.0 (smile)


EMOTION_PROFILES: dict[Emotion, EmotionProfile] = {
    Emotion.IDLE: EmotionProfile(1.0, 1.0, 0.5, 3.0, 6.0, 0.0, mouth_width=0.3, mouth_curve=0.1), 
    Emotion.LISTENING: EmotionProfile(1.15, 1.0, 0.7, 2.5, 4.5, -0.05, tilt_l=-0.05, tilt_r=0.05, squash_x=1.1, squash_y=1.0, mouth_width=0.4, mouth_curve=0.2),
    Emotion.THINKING: EmotionProfile(0.85, 0.9, 0.6, 2.0, 3.5, 0.05, tilt_l=0.1, tilt_r=-0.1, squash_x=0.9, squash_y=1.25, brow_y=5, mouth_width=0.2, mouth_curve=0.0),
    Emotion.HAPPY: EmotionProfile(0.95, 1.1, 0.45, 1.5, 3.0, -0.25, tilt_l=-0.1, tilt_r=0.1, squash_x=1.35, squash_y=0.75, brow_y=-10, mouth_width=0.6, mouth_curve=0.8),
    Emotion.SAD: EmotionProfile(0.75, 1.0, 0.2, 4.0, 7.0, 0.3, tilt_l=0.12, tilt_r=-0.12, squash_x=0.85, squash_y=0.9, brow_y=8, mouth_width=0.3, mouth_curve=-0.6),
    Emotion.CURIOUS: EmotionProfile(1.05, 1.0, 0.3, 2.0, 4.0, -0.1, tilt_l=-0.3, tilt_r=-0.1, squash_x=1.15, brow_y=-5, mouth_width=0.2, mouth_curve=0.1),
    Emotion.ANGRY: EmotionProfile(0.8, 0.7, 0.2, 1.0, 2.5, 0.45, tilt_l=0.2, tilt_r=-0.2, squash_x=0.8, squash_y=0.85, brow_y=12, mouth_width=0.5, mouth_curve=-0.4),
    Emotion.SLEEPY: EmotionProfile(0.3, 0.8, 0.1, 6.0, 12.0, 0.15, squash_y=0.4, brow_y=5, mouth_width=0.1, mouth_curve=0.0),
    Emotion.SCANNING: EmotionProfile(1.0, 0.95, 0.3, 2.8, 5.0, -0.1, tilt_l=-0.02, tilt_r=0.02, squash_y=0.9, mouth_width=0.4, mouth_curve=0.0),
    Emotion.MOVING: EmotionProfile(1.0, 1.0, 0.2, 2.2, 4.0, 0.0, squash_x=0.95, squash_y=1.1, mouth_width=0.3, mouth_curve=0.1),
    Emotion.ERROR: EmotionProfile(0.9, 0.8, 0.1, 0.4, 0.8, 0.35, tilt_l=0.45, tilt_r=0.45, squash_x=1.2, squash_y=0.8, brow_y=5, mouth_width=0.4, mouth_curve=-0.2),
}
