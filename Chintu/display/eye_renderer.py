from __future__ import annotations

import math
import pygame


class EyeRenderer:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.bg = (12, 14, 24)

    def _gradient_circle(self, surf: pygame.Surface, center: tuple[int, int], radius: int, base: tuple[int, int, int]):
        for r in range(radius, 0, -3):
            t = r / radius
            color = tuple(min(255, int(c * (0.6 + 0.4 * t))) for c in base)
            pygame.draw.circle(surf, color, center, r)

    def draw_eye(self, surf: pygame.Surface, center: tuple[int, int], radius: int, pupil_offset: tuple[float, float],
                 openness: float, pupil_scale: float, glow: float, eyelid_bias: float, swirl_angle: float,
                 error_outline: bool = False, scanning_line: bool = False):
        cx, cy = center
        eye_h = max(10, int(radius * openness))
        eye_rect = pygame.Rect(cx - radius, cy - eye_h, radius * 2, eye_h * 2)

        pygame.draw.ellipse(surf, (235, 238, 245), eye_rect)
        self._gradient_circle(surf, (cx, cy), int(radius * 0.95), (180, 190, 210))
        pygame.draw.ellipse(surf, (245, 248, 255), eye_rect.inflate(-8, -8), 0)

        px = int(cx + pupil_offset[0] * radius * 0.35)
        py = int(cy + pupil_offset[1] * radius * 0.35)
        pupil_r = int(radius * 0.28 * pupil_scale)

        if swirl_angle >= 0:
            pygame.draw.circle(surf, (20, 25, 38), (px, py), pupil_r, 2)
            end = (int(px + math.cos(swirl_angle) * pupil_r * 0.85), int(py + math.sin(swirl_angle) * pupil_r * 0.85))
            pygame.draw.line(surf, (90, 160, 255), (px, py), end, 3)
        else:
            pygame.draw.circle(surf, (20, 20, 25), (px, py), pupil_r)

        pygame.draw.circle(surf, (255, 255, 255), (px - pupil_r // 3, py - pupil_r // 3), max(2, pupil_r // 5))

        if glow > 0:
            glow_r = int(pupil_r * (1.4 + glow * 0.8))
            glow_color = (80, 120, 255, int(80 * glow))
            glow_s = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_s, glow_color, (glow_r, glow_r), glow_r)
            surf.blit(glow_s, (px - glow_r, py - glow_r), special_flags=pygame.BLEND_ALPHA_SDL2)

        lid_h = int((1 - openness) * radius * 1.4)
        if lid_h > 0:
            pygame.draw.rect(surf, self.bg, (cx - radius - 4, cy - eye_h - 4, radius * 2 + 8, lid_h))
            pygame.draw.rect(surf, self.bg, (cx - radius - 4, cy + eye_h - lid_h + 4, radius * 2 + 8, lid_h))

        brow_y = cy - radius - 18
        pygame.draw.line(
            surf,
            (40, 45, 70),
            (cx - radius + 15, brow_y + int(eyelid_bias * 20)),
            (cx + radius - 15, brow_y - int(eyelid_bias * 20)),
            4,
        )

        if scanning_line:
            scan_x = cx + int(pupil_offset[0] * radius)
            pygame.draw.line(surf, (120, 220, 255), (scan_x, cy - radius), (scan_x, cy + radius), 2)

        if error_outline:
            pygame.draw.ellipse(surf, (255, 40, 40), eye_rect, 4)
