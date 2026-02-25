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

    def draw_eye(self, surf: pygame.Surface, x: int, y: int, openness: float, 
                 pupil_offset: tuple[float, float], base_r: int, 
                 pupil_size_mult: float, glow_mult: float, brow_tilt: float, 
                 angle: float = 0.0, scale: tuple[float, float] = (1.0, 1.0),
                 error_outline: bool = False, audio_level: float = 0.0, 
                 is_listening: bool = False):
        
        # Pixar eyes are friendly rounded boxes
        # Using 2x super-sampling for high quality anti-aliased edges
        os_scale = 2
        eye_w = int(base_r * 2.2 * scale[0])
        eye_h = int(base_r * 1.8 * scale[1] * max(0.05, openness))
        radius = int(eye_h * 0.45)
        
        # Oversized surface for supersampling
        w, h = (eye_w + 60) * os_scale, (eye_h + 60) * os_scale
        eye_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        ec = (w // 2, h // 2)
        eye_rect = pygame.Rect(30 * os_scale, 30 * os_scale, eye_w * os_scale, eye_h * os_scale)
        # 1. Outer Bloom (Digital Screen Glow)
        glow_c = (0, 160, 255, 30)
        for i in range(3):
            inf = (i + 1) * 3 * os_scale
            glow_rect = eye_rect.inflate(inf, inf)
            pygame.draw.rect(eye_surf, (0, 160, 255, 35 - i*10), glow_rect, border_radius=os_radius + inf//2)

        # 2. Main Cyan Eye Body with Advanced Lid Masking
        # Create a temporary surface for the gradient eye
        eye_temp = pygame.Surface((eye_w * os_scale, eye_h * os_scale), pygame.SRCALPHA)
        
        # Draw vertical gradient
        for y_grad in range(eye_h * os_scale):
            alpha_grad = y_grad / (eye_h * os_scale)
            r = int(self.eye_color_top[0] * (1 - alpha_grad) + self.eye_color_bot[0] * alpha_grad)
            g = int(self.eye_color_top[1] * (1 - alpha_grad) + self.eye_color_bot[1] * alpha_grad)
            b = int(self.eye_color_top[2] * (1 - alpha_grad) + self.eye_color_bot[2] * alpha_grad)
            pygame.draw.line(eye_temp, (r, g, b), (0, y_grad), (eye_w * os_scale, y_grad))

        # 3. Create Mask (Pill shape + Emotional Lids)
        mask_surf = pygame.Surface((eye_w * os_scale, eye_h * os_scale), pygame.SRCALPHA)
        # Base Pill
        pygame.draw.rect(mask_surf, (255, 255, 255, 255), (0, 0, eye_w * os_scale, eye_h * os_scale), border_radius=os_radius)
        
        # Expressive Brow/Lid Cutting (Cozmo style geometry)
        if abs(brow_tilt) > 0.02:
            lid_surf = pygame.Surface((eye_w * os_scale, eye_h * os_scale), pygame.SRCALPHA)
            b_y = int(eye_h * 0.3 * os_scale) - int(brow_tilt * 40 * os_scale)
            ew_os = eye_w * os_scale
            eh_os = eye_h * os_scale
            
            if brow_tilt > 0: # Angry/Focused (Inward Tilt)
                pts = [(0, b_y), (ew_os, b_y + int(25*os_scale)), (ew_os, -eh_os), (0, -eh_os)]
            else: # Concerned/Curious (Outward Tilt)
                pts = [(0, b_y + int(25*os_scale)), (ew_os, b_y), (ew_os, -eh_os), (0, -eh_os)]
            
            # Subtractive drawing (Alpha 0) to cut the mask
            pygame.draw.polygon(mask_surf, (0, 0, 0, 0), pts)

        # Apply mask to gradient
        eye_temp.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        
        # 4. Premium Horizontal Glint
        glint_h = max(2, int(eye_h * 0.14 * os_scale))
        glint_w = int(eye_w * 0.7 * os_scale)
        glint_y = int(eye_h * 0.18 * os_scale)
        glint_x = (eye_w * os_scale - glint_w) // 2
        # Use rounded rect for the glint too
        pygame.draw.rect(eye_temp, self.glint_color, (glint_x, glint_y, glint_w, glint_h), border_radius=glint_h//2)
        
        # Blit final eye to main surface
        eye_surf.blit(eye_temp, (30 * os_scale, 30 * os_scale))

        # Scale down for anti-aliasing (Quality Boost)
        eye_surf = pygame.transform.smoothscale(eye_surf, (eye_w + 60, eye_h + 60))

        # Rotate the entire eye for independent tilts (Wall-E signature look)
        rotated_eye = pygame.transform.rotate(eye_surf, math.degrees(angle))
        rot_rect = rotated_eye.get_rect(center=(x, y))
        surf.blit(rotated_eye, rot_rect)

        # Listening Visual (Soft white pulses for Pixar theme)
        if is_listening:
            ring_count = 3
            for i in range(ring_count):
                r_speed = 0.006 + audio_level * 0.015
                r_phase = (pygame.time.get_ticks() * r_speed + i * (math.pi/2))
                pulse_r = int(base_r * (2.0 + math.sin(r_phase) * 0.5 * (1.0 + audio_level * 4)))
                alpha = int(120 * (1.0 - i/ring_count))
                if pulse_r > 1:
                    s = pygame.Surface((pulse_r*2, pulse_r*2), pygame.SRCALPHA)
                    pygame.draw.circle(s, (255, 255, 255, alpha), (pulse_r, pulse_r), pulse_r, 2)
                    surf.blit(s, (x - pulse_r, y - pulse_r))

    def draw_deck(self, surf: pygame.Surface, ask_ai_active: bool = False, commands_active: bool = False):
        deck_h = 80
        deck_y = self.height - deck_h
        
        # Simple Black Deck (matches background)
        # No line or colored rect needed if it's all black, but keeping surf for icon placement
        
        # Ask AI Icon (Bottom Left)
        ai_x = 60
        icon_y = self.height - 60
        self._draw_icon(surf, (ai_x, icon_y), "Ask AI", ask_ai_active)
        
        # Commands Icon (Bottom Right)
        cmd_x = self.width - 60
        self._draw_icon(surf, (cmd_x, icon_y), "Commands", commands_active)

    def _draw_icon(self, surf: pygame.Surface, pos: tuple[int, int], label: str, active: bool):
        x, y = pos
        radius = 30
        color = (255, 255, 255) if active else (255, 200, 150)
        bg_color = (180, 60, 20, 140) if active else (120, 40, 10, 80)
        
        # Icon Background
        s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, bg_color, (radius, radius), radius)
        if active:
            pygame.draw.circle(s, (255, 255, 255, 80), (radius, radius), radius + 5, 2)
        surf.blit(s, (x - radius, y - radius))
        
        # Icon Symbol
        if label == "Ask AI":
            # Brain/AI symbol concept: Hexagon with dots
            self._draw_hex(surf, color, (x, y), 15, 2)
            pygame.draw.circle(surf, color, (x, y), 4)
        else:
            # Commands symbol concept: Square with arrows
            pygame.draw.rect(surf, color, (x - 12, y - 12, 24, 24), 2)
            pygame.draw.line(surf, color, (x - 6, y), (x + 6, y), 2)
            pygame.draw.line(surf, color, (x, y - 6), (x, y + 6), 2)

        # Label Text (Clear UI labels)
        txt_surf = self.font_main.render(label, True, color)
        txt_rect = txt_surf.get_rect(center=(x, y + radius + 15))
        
        # Subtle label backdrop for readability
        bg_pax = 8
        lbg_rect = txt_rect.inflate(bg_pax*2, 4)
        lbg_s = pygame.Surface((lbg_rect.width, lbg_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(lbg_s, (160, 60, 0, 80 if not active else 120), (0, 0, lbg_rect.width, lbg_rect.height), border_radius=10)
        surf.blit(lbg_s, lbg_rect.topleft)
        surf.blit(txt_surf, txt_rect)

    def draw_status_text(self, surf: pygame.Surface, query: str, response: str):
        if not query and not response:
            return

        margin = 40
        max_w = self.width - margin * 2
        
        # Render Query (Top)
        if query:
            q_txt = query
            q_surf = self.font_main.render(q_txt, True, (255, 255, 255))
            q_rect = q_surf.get_rect(center=(self.width // 2, 60))
            
            # Bubble background (Themed Orange/White)
            pad = 15
            bg_rect = q_rect.inflate(pad*2, pad)
            s = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(s, (220, 100, 20, 180), (0, 0, bg_rect.width, bg_rect.height), border_radius=15)
            pygame.draw.rect(s, (255, 255, 255, 100), (0, 0, bg_rect.width, bg_rect.height), 2, border_radius=15)
            surf.blit(s, bg_rect.topleft)
            surf.blit(q_surf, q_rect)

        # Render Response (Center-Bottom, above deck)
        if response:
            # Wrap text if too long
            words = response.split()
            lines = []
            curr_line = "Chintu: "
            for word in words:
                test_line = curr_line + word + " "
                if self.font_bold.size(test_line)[0] < max_w - 40:
                    curr_line = test_line
                else:
                    lines.append(curr_line)
                    curr_line = word + " "
            lines.append(curr_line)
            
            # Draw Response box (Themed White/Orange)
            line_h = 30
            box_h = len(lines) * line_h + 20
            box_y = self.height - 80 - box_h - 20 # Above deck
            
            s = pygame.Surface((max_w, box_h), pygame.SRCALPHA)
            pygame.draw.rect(s, (255, 255, 255, 230), (0, 0, max_w, box_h), border_radius=12)
            pygame.draw.rect(s, (220, 100, 20, 150), (0, 0, max_w, box_h), 2, border_radius=12)
            surf.blit(s, (margin, box_y))
            
            for i, line in enumerate(lines):
                color = (40, 45, 60) if i > 0 else (220, 80, 0)
                l_surf = self.font_bold.render(line.strip(), True, color)
                l_rect = l_surf.get_rect(topleft=(margin + 20, box_y + 10 + i * line_h))
                surf.blit(l_surf, l_rect)
