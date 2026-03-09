from __future__ import annotations
import pygame
from core.state_manager import StateManager, Emotion
from utils.logger import get_logger

logger = get_logger(__name__)

class Dashboard:
    def __init__(self, width: int, height: int, state: StateManager):
        self.width = width
        self.height = height
        self.state = state
        self.font_title = pygame.font.SysFont("segoeui", 28, bold=True)
        self.font_small = pygame.font.SysFont("segoeui", 18)
        self.font_mono = pygame.font.SysFont("consolas", 16)
        
        self.bg_color = (15, 20, 30)
        self.panel_color = (25, 35, 50)
        self.accent_color = (0, 190, 255)
        self.text_color = (220, 230, 240)
        
        # UI Regions
        self.transcript_rect = pygame.Rect(20, 70, 360, 280)
        self.controls_rect = pygame.Rect(400, 70, 380, 280)
        self.logs_rect = pygame.Rect(20, 370, 760, 90)

    def draw(self, screen: pygame.Surface):
        screen.fill(self.bg_color)
        
        # Header
        title = self.font_title.render("CHINTU COMMAND CENTER", True, self.accent_color)
        screen.blit(title, (20, 20))
        
        status = self.state.state.emotion.value
        status_txt = self.font_small.render(f"STATUS: {status}", True, (255, 255, 0))
        screen.blit(status_txt, (self.width - status_txt.get_width() - 20, 25))

        self.draw_transcript(screen)
        self.draw_controls(screen)
        self.draw_logs(screen)
        self.draw_hardware_info(screen)

    def draw_transcript(self, screen: pygame.Surface):
        pygame.draw.rect(screen, self.panel_color, self.transcript_rect, border_radius=10)
        label = self.font_small.render("LIVE TRANSCRIPT", True, self.accent_color)
        screen.blit(label, (30, 80))
        
        state = self.state.state
        
        # Audio Level Bar (Visual Feedback)
        if state.emotion == Emotion.LISTENING:
            vol_w = int(state.audio_level * 100)
            pygame.draw.rect(screen, (50, 255, 50), (180, 85, vol_w, 10), border_radius=5)
            pygame.draw.rect(screen, (255, 255, 255, 50), (180, 85, 100, 10), 1, border_radius=5)

        query = state.last_query
        response = state.last_response
        
        y = 120
        if query:
            self._render_wrapped_text(screen, f"USER: {query}", (40, y), 320, (255, 255, 255))
            y += 60
        if response:
            self._render_wrapped_text(screen, f"ROBOT: {response}", (40, y), 320, self.accent_color)

    def draw_controls(self, screen: pygame.Surface):
        pygame.draw.rect(screen, self.panel_color, self.controls_rect, border_radius=10)
        label = self.font_small.render("MANUAL CONTROL", True, self.accent_color)
        screen.blit(label, (410, 80))
        
        # Grid of buttons
        btn_w, btn_h = 80, 60
        cx, cy = 400 + 190, 70 + 140
        self.btn_fwd = pygame.Rect(cx - btn_w//2, cy - btn_h*1.5, btn_w, btn_h)
        self.btn_left = pygame.Rect(cx - btn_w*1.5, cy - btn_h//2, btn_w, btn_h)
        self.btn_stop = pygame.Rect(cx - btn_w//2, cy - btn_h//2, btn_w, btn_h)
        self.btn_right = pygame.Rect(cx + btn_w//2, cy - btn_h//2, btn_w, btn_h)
        self.btn_back = pygame.Rect(cx - btn_w//2, cy + btn_h//2, btn_w, btn_h)
        
        self._draw_btn(screen, self.btn_fwd, "FWD")
        self._draw_btn(screen, self.btn_left, "LEFT")
        self._draw_btn(screen, self.btn_stop, "STOP", (200, 50, 50))
        self._draw_btn(screen, self.btn_right, "RIGHT")
        self._draw_btn(screen, self.btn_back, "BACK")

    def draw_logs(self, screen: pygame.Surface):
        pygame.draw.rect(screen, (10, 15, 20), self.logs_rect, border_radius=5)
        logs = self.state.state.logs or []
        display_logs = logs[-4:]
        for i, log in enumerate(display_logs):
            txt = self.font_mono.render(f"> {log}", True, (150, 160, 170))
            screen.blit(txt, (30, 380 + i * 20))

    def draw_hardware_info(self, screen: pygame.Surface):
        hw = self.state.state.hardware_status or {}
        info = f"BAT: {hw.get('battery', 100)}% | TEMP: {hw.get('temp', 35)}C | Wi-Fi: {hw.get('wifi', 'OK')}"
        txt = self.font_small.render(info, True, (100, 120, 140))
        screen.blit(txt, (self.width - txt.get_width() - 20, self.height - 25))

    def _draw_btn(self, screen: pygame.Surface, rect: pygame.Rect, text: str, color=None):
        if color is None: color = (40, 60, 90)
        pygame.draw.rect(screen, color, rect, border_radius=8)
        pygame.draw.rect(screen, self.accent_color, rect, width=2, border_radius=8)
        txt = self.font_small.render(text, True, (255, 255, 255))
        screen.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))

    def _render_wrapped_text(self, screen: pygame.Surface, text: str, pos: tuple[int, int], max_w: int, color: tuple):
        words = text.split()
        lines = []
        curr = ""
        for w in words:
            if self.font_small.size(curr + w)[0] < max_w:
                curr += w + " "
            else:
                lines.append(curr)
                curr = w + " "
        lines.append(curr)
        for i, line in enumerate(lines):
            t_surf = self.font_small.render(line.strip(), True, color)
            screen.blit(t_surf, (pos[0], pos[1] + i * 22))

    def handle_click(self, pos: tuple[int, int], bus):
        if self.btn_fwd.collidepoint(pos): bus.publish("move", "forward")
        if self.btn_left.collidepoint(pos): bus.publish("move", "left")
        if self.btn_right.collidepoint(pos): bus.publish("move", "right")
        if self.btn_back.collidepoint(pos): bus.publish("move", "backward")
        if self.btn_stop.collidepoint(pos): bus.publish("move", "stop")
