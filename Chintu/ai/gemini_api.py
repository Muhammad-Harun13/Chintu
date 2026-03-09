from __future__ import annotations
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
        
        sys_prompt = "You are Chintu, a brilliant robot. Summarize the answer to the user's question accurately and concisely. Keep it under 15 words and be friendly."
        payload = {"contents": [{"parts": [{"text": sys_prompt + prompt}]}]}
        
        try:
            r = requests.post(self._endpoint(), json=payload, timeout=self.cfg.request_timeout_s)
            r.raise_for_status()
            data = r.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {e}")
