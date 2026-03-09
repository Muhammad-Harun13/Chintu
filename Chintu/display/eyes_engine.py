from __future__ import annotations

import math
import random
import threading
from time import monotonic

import pygame

from core.state_manager import Emotion, StateManager
from display.animations import smooth_damp
from display.emotions import EMOTION_PROFILES
from display.eye_renderer import EyeRenderer
from utils.logger import get_logger

logger = get_logger(__name__)


class EyesEngine:
    def __init__(self, state: StateManager, width: int = 800, height: int = 480, fps: int = 60, fullscreen: bool = True):
        self.state = state
        self.width = width
        self.height = height
        self.fps = fps
        self.fullscreen = fullscreen
        self._running = False
        self._thread: threading.Thread | None = None

        self._pupil_x = 0.0
        self._pupil_y = 0.0
        self._target_x = 0.0
        self._target_y = 0.0
        self._blink_t = 0.0
        self._next_blink_s = random.uniform(3, 6)
        self._open = 1.0
        self._swirl = -1.0
        self._phase = 0.0

    def start(self) -> None:
        self._running = True
        self._thread = threading.Thread(target=self._run, name="eyes-engine", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)

    def _run(self) -> None:
        pygame.init()
        flags = pygame.FULLSCREEN if self.fullscreen else 0
        screen = pygame.display.set_mode((self.width, self.height), flags)
        clock = pygame.time.Clock()
        renderer = EyeRenderer(self.width, self.height)
        t_prev = monotonic()

        while self._running:
            dt = max(0.001, monotonic() - t_prev)
            t_prev = monotonic()
            self._phase += dt

            state = self.state.state
            emotion = state.emotion
            profile = EMOTION_PROFILES[emotion]
            self._animate_targets(emotion, dt)

            self._pupil_x = smooth_damp(self._pupil_x, self._target_x, dt, 4.0)
            self._pupil_y = smooth_damp(self._pupil_y, self._target_y, dt, 4.0)

            self._blink_t += dt
            if self._blink_t > self._next_blink_s:
                self._open = smooth_damp(self._open, 0.05, dt, 20)
                if self._open < 0.2:
                    self._blink_t = 0
                    self._next_blink_s = random.uniform(profile.blink_min_s, profile.blink_max_s)
            else:
                self._open = smooth_damp(self._open, profile.eye_open, dt, 8)

            screen.fill(renderer.bg)
            base_radius = 105 + int(4 * math.sin(self._phase * 2.2))
            lx = self.width // 2 - 140
            rx = self.width // 2 + 140
            cy = self.height // 2

            swirl = self._phase * 5 if emotion == Emotion.THINKING else -1.0
            error_on = emotion == Emotion.ERROR and int(self._phase * 8) % 2 == 0
            scanning = emotion == Emotion.SCANNING
            is_listening = emotion == Emotion.LISTENING

            # Draw Eyes
            renderer.draw_eye(screen, (lx, cy), base_radius, (self._pupil_x, self._pupil_y), self._open,
                              profile.pupil_size, profile.glow, profile.brow_tilt, 
                              angle=profile.tilt_l, scale=(profile.squash_x, profile.squash_y),
                              swirl=swirl, error_outline=error_on,
                              scanning_line=scanning, is_listening=is_listening, audio_level=state.audio_level)
            renderer.draw_eyebrow(screen, lx, cy, profile.brow_tilt, profile.brow_y, base_radius)

            right_open = self._open * (0.85 if emotion == Emotion.CURIOUS else 1.0)
            renderer.draw_eye(screen, (rx, cy), base_radius, (self._pupil_x, self._pupil_y), right_open,
                              profile.pupil_size, profile.glow, profile.brow_tilt, 
                              angle=profile.tilt_r, scale=(profile.squash_x, profile.squash_y),
                              swirl=swirl, error_outline=error_on,
                              scanning_line=scanning, is_listening=is_listening, audio_level=state.audio_level)
            renderer.draw_eyebrow(screen, rx, cy, -profile.brow_tilt, profile.brow_y, base_radius)

            # Draw Mouth
            renderer.draw_mouth(screen, self.width // 2, cy, self._open)

            # Draw Deck and Handle Interactions
            hitboxes = renderer.draw_deck(screen, state.ui_ask_ai, state.ui_commands)
            renderer.draw_status_text(screen, state.transcript_query, state.transcript_response)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mpos = pygame.mouse.get_pos()
                    if hitboxes["ask"].collidepoint(mpos):
                        print(f"{self.state._colors['cyan']}[UI]{self.state._colors['reset']} Ask button clicked")
                        self.state._bus.publish("ui_ask_ai", None)
                    elif hitboxes["command"].collidepoint(mpos):
                        print(f"{self.state._colors['yellow']}[UI]{self.state._colors['reset']} Command button clicked")
                        self.state._bus.publish("ui_commands", None)

            pygame.display.flip()
            clock.tick(self.fps)

        pygame.quit()
        logger.info("Eyes engine stopped")

    def _animate_targets(self, emotion: Emotion, dt: float) -> None:
        if emotion in (Emotion.IDLE, Emotion.SLEEPY):
            if random.random() < dt * 0.5:
                self._target_x = random.uniform(-0.3, 0.3)
                self._target_y = random.uniform(-0.2, 0.2)
        elif emotion == Emotion.SCANNING:
            self._target_x = math.sin(self._phase * 2.0) * 0.8
            self._target_y = -0.05
        elif emotion == Emotion.THINKING:
            self._target_x = 0.0
            self._target_y = -0.2
        elif emotion == Emotion.MOVING:
            self._target_x = random.uniform(-0.08, 0.08)
            self._target_y = random.uniform(-0.05, 0.05)
        elif emotion == Emotion.CURIOUS:
            self._target_x = math.sin(self._phase * 3.0) * 0.6
        elif emotion == Emotion.HAPPY:
            self._target_y = -0.15
        elif emotion == Emotion.ANGRY:
            self._target_x = 0.0
            self._target_y = 0.02
        elif emotion == Emotion.ERROR:
            self._target_x = random.uniform(-0.4, 0.4)
            self._target_y = random.uniform(-0.2, 0.2)
