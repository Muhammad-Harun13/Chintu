from __future__ import annotations

import math
import pygame


class EyeRenderer:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        # Cozmo Style Colors (Vibrant Cyan)
        self.bg = (0, 0, 0) # Black background
        self.eye_color_top = (0, 160, 255) # Darker cyan
        self.eye_color_bot = (0, 240, 255) # Brighter cyan
        self.glint_color = (230, 250, 255) # Soft white glint
        
        pygame.font.init()
        # ... rest of init remains same or updated if needed
        self.font_main = None
        font_names = ["segoeuiuivariable", "segoeui", "arial"]
        for name in font_names:
            try:
                self.font_main = pygame.font.SysFont(name, 22, bold=False)
                self.font_bold = pygame.font.SysFont(name, 24, bold=True)
                break
            except Exception:
                continue
        if not self.font_main:
            self.font_main = pygame.font.Font(None, 24)
            self.font_bold = pygame.font.Font(None, 26)

    def _draw_rounded_rect(self, surf: pygame.Surface, color: tuple, rect: pygame.Rect, radius: int):
        """Helper to draw a soft rounded rectangle for Pixar style"""
        pygame.draw.rect(surf, color, rect, border_radius=radius)

    def _draw_hex(self, surf: pygame.Surface, color: tuple, center: tuple[int, int], radius: int, width: int = 0):
        points = []
        for i in range(6):
            angle = math.radians(60 * i + 30)
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            points.append((x, y))
        pygame.draw.polygon(surf, color, points, width)

    def draw_eye(self, surf: pygame.Surface, center: tuple[int, int], base_radius: int, 
                 pupil_offset: tuple[float, float], openness: float, 
                 pupil_size_mult: float, glow_mult: float, brow_tilt: float, 
                 angle: float = 0.0, scale: tuple[float, float] = (1.0, 1.0),
                 swirl: float = -1.0, error_outline: bool = False, 
                 scanning_line: bool = False, is_listening: bool = False, 
                 audio_level: float = 0.0):
        
        x, y = center
        # Pixar eyes are friendly rounded boxes
        os_scale = 2
        eye_w = int(base_radius * 2.2 * scale[0])
        eye_h = int(base_radius * 1.8 * scale[1] * max(0.05, openness))
        radius = int(eye_h * 0.45)
        
        # Oversized surface for supersampling
        w, h = (eye_w + 60) * os_scale, (eye_h + 60) * os_scale
        if not hasattr(self, '_eye_surf_cache') or self._eye_surf_cache.get_size() != (w, h):
            self._eye_surf_cache = pygame.Surface((w, h), pygame.SRCALPHA)
        
        eye_surf = self._eye_surf_cache
        eye_surf.fill((0, 0, 0, 0))
        
        # 1. Outer Bloom
        eye_rect = pygame.Rect(30 * os_scale, 30 * os_scale, eye_w * os_scale, eye_h * os_scale)
        for i in range(3):
            inf = (i + 1) * 3 * os_scale
            glow_rect = eye_rect.inflate(inf, inf)
            pygame.draw.rect(eye_surf, (0, 160, 255, 35 - i*10), glow_rect, border_radius=radius + inf//2)

        # 2. Main Eye Body
        eye_temp = pygame.Surface((eye_w * os_scale, eye_h * os_scale), pygame.SRCALPHA)
        for y_grad in range(eye_h * os_scale):
            alpha_grad = y_grad / (eye_h * os_scale)
            r = int(self.eye_color_top[0] * (1 - alpha_grad) + self.eye_color_bot[0] * alpha_grad)
            g = int(self.eye_color_top[1] * (1 - alpha_grad) + self.eye_color_bot[1] * alpha_grad)
            b = int(self.eye_color_top[2] * (1 - alpha_grad) + self.eye_color_bot[2] * alpha_grad)
            pygame.draw.line(eye_temp, (r, g, b), (0, y_grad), (eye_w * os_scale, y_grad))

        # 3. Mask (Pill shape)
        mask_surf = pygame.Surface((eye_w * os_scale, eye_h * os_scale), pygame.SRCALPHA)
        pygame.draw.rect(mask_surf, (255, 255, 255, 255), (0, 0, eye_w * os_scale, eye_h * os_scale), border_radius=radius)
        
        # 4. Swirl
        if swirl >= 0:
            for i in range(4):
                s_angle = swirl + i * (math.pi / 2)
                sx = eye_w * os_scale // 2 + math.cos(s_angle) * eye_w * os_scale * 0.4
                sy = eye_h * os_scale // 2 + math.sin(s_angle) * eye_h * os_scale * 0.4
                pygame.draw.circle(eye_temp, (255, 255, 255, 150), (int(sx), int(sy)), int(10 * os_scale))

        eye_temp.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        
        # 5. Glint
        glint_h = max(2, int(eye_h * 0.14 * os_scale))
        glint_w = int(eye_w * 0.7 * os_scale)
        glint_y = int(eye_h * 0.18 * os_scale)
        glint_x = (eye_w * os_scale - glint_w) // 2
        pygame.draw.rect(eye_temp, self.glint_color, (glint_x, glint_y, glint_w, glint_h), border_radius=glint_h//2)
        
        # 6. Error & Scanning
        if error_outline:
            pygame.draw.rect(eye_temp, (255, 50, 50), (0, 0, eye_w * os_scale, eye_h * os_scale), 4 * os_scale, border_radius=radius)
        if scanning_line:
            scan_y = int((math.sin(pygame.time.get_ticks() * 0.005) * 0.5 + 0.5) * eye_h * os_scale)
            pygame.draw.line(eye_temp, (255, 255, 255, 200), (0, scan_y), (eye_w * os_scale, scan_y), 2 * os_scale)

        eye_surf.blit(eye_temp, (30 * os_scale, 30 * os_scale))
        
        # 5. Pupil (Essential for expression)
        pupil_w = int(eye_w * 0.45 * pupil_size_mult * os_scale)
        pupil_h = int(eye_h * 0.55 * pupil_size_mult * os_scale)
        px_off = int(pupil_offset[0] * eye_w * 0.25 * os_scale)
        py_off = int(pupil_offset[1] * eye_h * 0.2 * os_scale)
        pupil_rect = pygame.Rect(0, 0, pupil_w, pupil_h)
        pupil_rect.center = (30 * os_scale + (eye_w * os_scale // 2) + px_off, 
                            30 * os_scale + (eye_h * os_scale // 2) + py_off)
        
        # Darker center pupil
        pygame.draw.ellipse(eye_surf, (0, 40, 80), pupil_rect)
        # Inner pupil glint
        small_glint = pupil_rect.inflate(-pupil_w*0.6, -pupil_h*0.7)
        small_glint.topleft = (pupil_rect.centerx - 2*os_scale, pupil_rect.centery - 6*os_scale)
        pygame.draw.ellipse(eye_surf, (200, 240, 255, 180), small_glint)

        # 6. Glint (Top shine)
        glint_h = max(2, int(eye_h * 0.14 * os_scale))
        glint_w = int(eye_w * 0.7 * os_scale)
        glint_y = int(30 * os_scale + eye_h * 0.18 * os_scale)
        glint_x = 30 * os_scale + (eye_w * os_scale - glint_w) // 2
        pygame.draw.rect(eye_surf, self.glint_color, (glint_x, glint_y, glint_w, glint_h), border_radius=glint_h//2)
        
        # 7. Error & Scanning
        if error_outline:
            pygame.draw.rect(eye_surf, (255, 50, 50), (30*os_scale, 30*os_scale, eye_w * os_scale, eye_h * os_scale), 4 * os_scale, border_radius=radius)
        if scanning_line:
            scan_y = int(30*os_scale + (math.sin(pygame.time.get_ticks() * 0.005) * 0.5 + 0.5) * eye_h * os_scale)
            pygame.draw.line(eye_surf, (255, 255, 255, 220), (30*os_scale, scan_y), (30*os_scale + eye_w * os_scale, scan_y), 3 * os_scale)

        eye_surf = pygame.transform.smoothscale(eye_surf, (eye_w + 60, eye_h + 60))
        
        # 8. Independent Tilts
        rotated_eye = pygame.transform.rotate(eye_surf, math.degrees(angle))
        rot_rect = rotated_eye.get_rect(center=(x, y))
        surf.blit(rotated_eye, rot_rect)

        # Listening Visual
        if is_listening:
            ring_count = 3
            for i in range(ring_count):
                r_speed = 0.006 + audio_level * 0.015
                r_phase = (pygame.time.get_ticks() * r_speed + i * (math.pi/2))
                pulse_r = int(base_radius * (1.8 + math.sin(r_phase) * 0.4 * (1.0 + audio_level * 4)))
                alpha = int(140 * (1.0 - i/ring_count))
                if pulse_r > 1:
                    s = pygame.Surface((pulse_r*2, pulse_r*2), pygame.SRCALPHA)
                    pygame.draw.circle(s, (255, 255, 255, alpha), (pulse_r, pulse_r), pulse_r, 3)
                    surf.blit(s, (x - pulse_r, y - pulse_r))

    def draw_deck(self, surf: pygame.Surface, ask_active: bool = False, cmd_active: bool = False) -> dict[str, pygame.Rect]:
        """Draws the interaction deck and returns hitboxes for buttons."""
        # Bottom corners
        ai_x = 70
        cmd_x = self.width - 70
        icon_y = self.height - 70
        
        # Ask Icon
        self._draw_icon(surf, (ai_x, icon_y), "Ask", ask_active)
        ask_rect = pygame.Rect(ai_x - 50, icon_y - 50, 100, 110)
        
        # Command Icon
        self._draw_icon(surf, (cmd_x, icon_y), "Command", cmd_active)
        cmd_rect = pygame.Rect(cmd_x - 50, icon_y - 50, 100, 110)

        return {"ask": ask_rect, "command": cmd_rect}

    def _draw_icon(self, surf: pygame.Surface, pos: tuple[int, int], label: str, active: bool):
        x, y = pos
        radius = 35
        # Brighter, high-contrast colors
        color = (255, 255, 255) if active else (0, 200, 255)
        bg_color = (0, 150, 255) if active else (0, 80, 200)
        
        # Icon Background (No transparency for maximum visibility)
        pygame.draw.circle(surf, bg_color, (x, y), radius)
        if active:
            pygame.draw.circle(surf, (255, 255, 255), (x, y), radius + 4, 3)
        else:
            pygame.draw.circle(surf, (0, 240, 255), (x, y), radius, 2)
        
        # Icon Symbol
        if label == "Ask":
            pygame.draw.circle(surf, color, (x, y), 12, 2)
            pygame.draw.circle(surf, color, (x, y), 4)
        else:
            pygame.draw.rect(surf, color, (x - 10, y - 10, 20, 20), 2)
            pygame.draw.line(surf, color, (x - 6, y), (x + 6, y), 2)

        # Label Text
        txt_surf = self.font_bold.render(label, True, (255, 255, 255))
        txt_rect = txt_surf.get_rect(center=(x, y + radius + 20))
        # Shadow for text
        shadow = self.font_bold.render(label, True, (0, 0, 0))
        surf.blit(shadow, (txt_rect.x + 2, txt_rect.y + 2))
        surf.blit(txt_surf, txt_rect)

    def draw_eyebrow(self, surf: pygame.Surface, x: int, y: int, tilt: float, y_offset: float, base_r: int):
        """Draws a thick expressive eyebrow above the eye center (x, y)"""
        bw = int(base_r * 2.3)
        bh = int(base_r * 0.22)
        
        # Use supersampling for the brow too
        os = 2
        sw, sh = bw * os + 40 * os, bh * os + 40 * os
        if not hasattr(self, '_brow_surf_cache') or self._brow_surf_cache.get_size() != (sw, sh):
            self._brow_surf_cache = pygame.Surface((sw, sh), pygame.SRCALPHA)
            
        brow_surf = self._brow_surf_cache
        brow_surf.fill((0, 0, 0, 0))
        
        # Draw rounded rect
        pygame.draw.rect(brow_surf, self.eye_color_bot, (20, 20, bw * os, bh * os), border_radius=(bh * os)//2)
        
        # Scale down for anti-aliasing
        brow_surf = pygame.transform.smoothscale(brow_surf, (bw + 20, bh + 20))
        
        # Rotate based on emotional tilt
        rotated_brow = pygame.transform.rotate(brow_surf, math.degrees(tilt))
        
        # Position above eye
        # y is eye center. Move up by base_r * 1.3
        final_y = y - int(base_r * 1.35) + int(y_offset)
        rot_rect = rotated_brow.get_rect(center=(x, final_y))
        surf.blit(rotated_brow, rot_rect)

    def draw_mouth(self, surf: pygame.Surface, x: int, y: int, openness: float):
        """Draws a simple, expressive mouth line."""
        mw = 80 # a little bigger
        y_pos = y + 130
        color = (0, 180, 255) 
        # Slight curve
        pts = [
            (x - mw//2, y_pos),
            (x, y_pos + (4 if openness > 0.5 else 0)),
            (x + mw//2, y_pos)
        ]
        pygame.draw.lines(surf, color, False, pts, 6) # slightly thicker

    def draw_status_text(self, surf: pygame.Surface, query: str, response: str):
        if not query and not response:
            return

        margin = 160 # Leave room for buttons in corners
        max_w = self.width - margin * 2
        bottom_y = self.height - 40 # Near bottom edge
        
        # Determine total height needed
        lines = []
        if response:
            words = response.split()
            curr_line = "Chintu: "
            for word in words:
                test_line = curr_line + word + " "
                if self.font_bold.size(test_line)[0] < max_w:
                    curr_line = test_line
                else:
                    lines.append(curr_line)
                    curr_line = word + " "
            lines.append(curr_line)

        if query:
            lines.insert(0, f"You: {query}")

        if not lines:
            return

        line_h = 28
        box_h = len(lines) * line_h + 20
        box_y = self.height - 20 - box_h # Bottom-aligned
        
        # Background bubble (Bottom center)
        s = pygame.Surface((max_w + 40, box_h), pygame.SRCALPHA)
        pygame.draw.rect(s, (0, 0, 0, 180), (0, 0, max_w + 40, box_h), border_radius=15)
        pygame.draw.rect(s, (0, 180, 255, 120), (0, 0, max_w + 40, box_h), 2, border_radius=15)
        surf.blit(s, (self.width // 2 - (max_w + 40) // 2, box_y))
        
        # Render lines
        for i, line in enumerate(lines):
            color = (0, 240, 255) if "Chintu:" in line else (255, 255, 255)
            l_surf = self.font_bold.render(line.strip(), True, color)
            l_rect = l_surf.get_rect(center=(self.width // 2, box_y + 15 + i * line_h))
            surf.blit(l_surf, l_rect)
