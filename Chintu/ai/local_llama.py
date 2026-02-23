from __future__ import annotations

import requests

from core.config import AIConfig


class LocalLlama:
    def __init__(self, config: AIConfig):
        self.cfg = config

    def ask(self, prompt: str) -> str:
        payload = {"model": self.cfg.ollama_model, "prompt": prompt, "stream": False}
        try:
            r = requests.post(self.cfg.ollama_url, json=payload, timeout=self.cfg.request_timeout_s)
            r.raise_for_status()
            return r.json().get("response", "") or "I could not generate a response right now."
        except Exception:
            return "Local model is unavailable right now."
