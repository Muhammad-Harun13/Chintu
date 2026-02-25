from __future__ import annotations

import logging
import os


def get_logger(name: str) -> logging.Logger:
    level_name = os.getenv("CHINTU_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    
    # Simple format for maximum terminal compatibility
    log_format = "%(asctime)s [%(levelname)s] %(message)s"
    
    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt="%H:%M:%S",
    )
    return logging.getLogger(name)
