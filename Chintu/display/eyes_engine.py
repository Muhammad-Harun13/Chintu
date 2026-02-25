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
from display.dashboard import Dashboard
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
        self._brow_y = 0.0
        self._mouth_w = 0.0
        self._mouth_c = 0.0

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
        dashboard = Dashboard(self.width, self.height, self.state)
        t_prev = monotonic()

        while self._running:
            dt = max(0.001, monotonic() - t_prev)
            t_prev = monotonic()
            self._phase += dt

            ask_ai_rect = pygame.Rect(60 - 30, self.height - 60 - 30, 60, 60)
            cmds_rect = pygame.Rect(self.width - 60 - 30, self.height - 60 - 30, 60, 60)
            
            click_pos = None

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self._running = False
                        self.state._bus.publish("app_quit")
                    # Debug keys for expressions
                    elif event.key == pygame.K_h:
                        self.state.set_emotion(Emotion.HAPPY)
                    elif event.key == pygame.K_s:
                        self.state.set_emotion(Emotion.SAD)
                    elif event.key == pygame.K_a:
                        self.state.set_emotion(Emotion.ANGRY)
                    elif event.key == pygame.K_c:
                        self.state.set_emotion(Emotion.CURIOUS)
                    elif event.key == pygame.K_t:
                        self.state.set_emotion(Emotion.THINKING)
                    elif event.key == pygame.K_i:
                        self.state.set_emotion(Emotion.IDLE)
                    elif event.key == pygame.K_d:
                        self.state.set_dashboard_active(not self.state.state.dashboard_active)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Left click
                        click_pos = event.pos

            if click_pos:
                if ask_ai_rect.collidepoint(click_pos):
                    logger.info("UI: Ask AI clicked")
                    self.state.touch_interaction()
                    self.state._bus.publish("ui_ask_ai")
                elif cmds_rect.collidepoint(click_pos):
                    logger.info("UI: Commands clicked")
                    self.state.touch_interaction()
                    self.state._bus.publish("ui_commands")
            
            state = self.state.state
            if state.dashboard_active:
                if click_pos:
                    dashboard.handle_click(click_pos, self.state._bus)
                dashboard.draw(screen)
                pygame.display.flip()
                clock.tick(self.fps)
                continue

            emotion = state.emotion
            audio_level = state.audio_level
            is_listening = emotion == Emotion.LISTENING

            profile = EMOTION_PROFILES[emotion]
            self._animate_targets(emotion, dt)

            self._pupil_x = smooth_damp(self._pupil_x, self._target_x, dt, 4.0)
            self._pupil_y = smooth_damp(self._pupil_y, self._target_y, dt, 4.0)

            if self._blink_t > self._next_blink_s:
                self._open = smooth_damp(self._open, 0.05, dt, 20)
                if self._open < 0.1:
                    self._blink_t = 0
                    self._next_blink_s = random.uniform(profile.blink_min_s, profile.blink_max_s)
            else:
                self._open = smooth_damp(self._open, profile.eye_open, dt, 8)

            # Animate Eyebrows and Mouth
            self._brow_y = smooth_damp(self._brow_y, profile.brow_y, dt, 8)
            self._mouth_w = smooth_damp(self._mouth_w, profile.mouth_width, dt, 8)
            self._mouth_c = smooth_damp(self._mouth_c, profile.mouth_curve, dt, 8)

            # Pixar/Wall-E dynamic parameters
            eye_tilt_l = profile.tilt_l
            eye_tilt_r = profile.tilt_r
            sq_x = profile.squash_x
            sq_y = profile.squash_y
            
            error_on = (emotion == Emotion.ERROR)
            
            screen.fill(renderer.bg)
            base_radius = 105 + int(4 * math.sin(self._phase * 2.2))
            lx = self.width // 2 - 140
            rx = self.width // 2 + 140
            cy = self.height // 2 - 40 # Move eyes up slightly to make room for deck

            # Draw Eyes (Wall-E style with independent tilts)
            # Left Eye
            renderer.draw_eye(screen, 
                              lx, cy, 
                              self._open, (self._pupil_x, self._pupil_y), base_radius,
                              profile.pupil_size, profile.glow, profile.brow_tilt,
                              angle=eye_tilt_l, scale=(sq_x, sq_y),
                              error_outline=error_on, audio_level=audio_level,
                              is_listening=is_listening)
            
            # Right Eye
            right_open = self._open * (0.85 if emotion == Emotion.CURIOUS else 1.0)
            renderer.draw_eye(screen, 
                              rx, cy, 
                              right_open, (self._pupil_x, self._pupil_y), base_radius,
                              profile.pupil_size, profile.glow, profile.brow_tilt,
                              angle=eye_tilt_r, scale=(sq_x, sq_y),
                              error_outline=error_on, audio_level=audio_level,
                              is_listening=is_listening)

            # Draw Eyebrows (Mirrored for L/R)
            renderer.draw_eyebrow(screen, lx, cy, profile.brow_tilt, self._brow_y, base_radius)
            renderer.draw_eyebrow(screen, rx, cy, -profile.brow_tilt, self._brow_y, base_radius)

            # Draw Mouth
            m_y = cy + int(base_radius * 1.5)
            renderer.draw_mouth(screen, self.width // 2, m_y, self._mouth_w, self._mouth_c)

            # Determine which icon is "active" based on state
            renderer.draw_deck(screen, ask_ai_active=state.ask_ai_active, commands_active=state.commands_active)

            # Draw Transcript/Status Text
            renderer.draw_status_text(screen, state.last_query, state.last_response)

            pygame.display.flip()
            clock.tick(self.fps)

        pygame.quit()
        logger.info("Eyes engine stopped")

    def _animate_targets(self, emotion: Emotion, dt: float) -> None:
        # Check if we should be looking at the UI (Interaction state)
        if self.state.state.emotion == Emotion.LISTENING:
            # Look down-ish towards the center deck area
            self._target_x = 0.0
            self._target_y = 0.35 + 0.05 * math.sin(self._phase * 5)
            return

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
