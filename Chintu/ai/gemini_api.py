from __future__ import annotations

import base64

import requests

from core.config import AIConfig


class GeminiAPI:
    def __init__(self, config: AIConfig):
        self.cfg = config

    def _endpoint(self) -> str:
        return (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.cfg.gemini_model}:generateContent?key={self.cfg.gemini_api_key}"
        )

    def ask_text(self, prompt: str) -> str:
        if not self.cfg.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY missing")
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        r = requests.post(self._endpoint(), json=payload, timeout=self.cfg.request_timeout_s)
        r.raise_for_status()
        data = r.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    def ask_vision(self, prompt: str, image: bytes) -> str:
        if not self.cfg.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY missing")
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(image).decode("utf-8")}},
                    ]
                }
            ]
        }
        r = requests.post(self._endpoint(), json=payload, timeout=self.cfg.request_timeout_s)
        r.raise_for_status()
        data = r.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
