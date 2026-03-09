from __future__ import annotations

from collections import defaultdict
from threading import Lock
from typing import Any, Callable


class EventBus:
    """Simple thread-safe pub/sub bus."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable[[Any], None]]] = defaultdict(list)
        self._lock = Lock()

    def subscribe(self, topic: str, handler: Callable[[Any], None]) -> None:
        with self._lock:
            self._handlers[topic].append(handler)

    def publish(self, topic: str, payload: Any = None) -> None:
        with self._lock:
            handlers = list(self._handlers.get(topic, []))
        for handler in handlers:
            handler(payload)
