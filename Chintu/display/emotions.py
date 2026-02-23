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


EMOTION_PROFILES: dict[Emotion, EmotionProfile] = {
    Emotion.IDLE: EmotionProfile(1.0, 1.0, 0.0, 3.0, 6.0, 0.0),
    Emotion.LISTENING: EmotionProfile(1.08, 1.0, 0.5, 2.8, 5.0, -0.1),
    Emotion.THINKING: EmotionProfile(1.0, 0.9, 0.6, 2.5, 4.0, -0.05),
    Emotion.HAPPY: EmotionProfile(0.95, 1.05, 0.35, 2.0, 4.0, -0.2),
    Emotion.SAD: EmotionProfile(0.75, 1.0, 0.0, 4.0, 7.0, 0.2),
    Emotion.CURIOUS: EmotionProfile(1.0, 0.95, 0.2, 2.5, 5.0, -0.05),
    Emotion.ANGRY: EmotionProfile(0.9, 0.7, 0.0, 2.0, 3.5, 0.35),
    Emotion.SLEEPY: EmotionProfile(0.45, 0.9, 0.0, 5.0, 8.0, 0.15),
    Emotion.SCANNING: EmotionProfile(0.98, 0.9, 0.15, 2.8, 5.0, -0.1),
    Emotion.MOVING: EmotionProfile(1.0, 0.95, 0.05, 2.5, 4.5, 0.0),
    Emotion.ERROR: EmotionProfile(0.9, 0.8, 0.0, 0.8, 1.5, 0.25),
}
