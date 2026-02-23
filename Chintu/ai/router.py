from __future__ import annotations

from dataclasses import dataclass

from ai.gemini_api import GeminiAPI
from ai.local_llama import LocalLlama


DIRECT_MAP = {
    "forward": "forward",
    "backward": "backward",
    "stop": "stop",
    "turn left": "left",
    "turn right": "right",
    "what time": "time",
    "scan": "scan",
    "sleep": "sleep",
}


@dataclass
class RouteResult:
    kind: str
    action: str | None = None
    response: str | None = None


class AIRouter:
    def __init__(self, local_ai: LocalLlama, gemini: GeminiAPI):
        self.local_ai = local_ai
        self.gemini = gemini

    def route(self, text: str) -> RouteResult:
        t = text.strip().lower()
        for key, action in DIRECT_MAP.items():
            if key in t:
                return RouteResult(kind="DIRECT", action=action)

        if len(t.split()) <= 6:
            return RouteResult(kind="LOCAL", response=self.local_ai.ask(text))

        try:
            return RouteResult(kind="GEMINI", response=self.gemini.ask_text(text))
        except Exception:
            return RouteResult(kind="LOCAL_FALLBACK", response=self.local_ai.ask(text))
