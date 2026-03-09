from __future__ import annotations


def lerp(current: float, target: float, alpha: float) -> float:
    return current + (target - current) * alpha


def smooth_damp(current: float, target: float, dt: float, speed: float = 8.0) -> float:
    alpha = max(0.0, min(1.0, dt * speed))
    return lerp(current, target, alpha)
