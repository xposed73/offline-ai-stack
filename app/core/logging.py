import logging
import sys
from pathlib import Path
from rich.logging import RichHandler
from app.config.settings import settings

# Ensure logs folder exists
LOG_DIR = settings.data_path / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "offline_stack.log"

def setup_logger(name: str = "offline-ai-stack", level: int = logging.INFO) -> logging.Logger:
    """Sets up a dual-handler logger (Rich Terminal UI + Persistent File)."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Clean existing handlers
    if logger.handlers:
        logger.handlers.clear()

    # Formatter
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # 1. Rich Handler for Terminal Output
    rich_handler = RichHandler(
        rich_tracebacks=True,
        markup=True,
        show_time=True,
        show_path=False,
        omit_repeated_times=False
    )
    rich_handler.setLevel(level)
    logger.addHandler(rich_handler)

    # 2. File Handler for persistent logging
    try:
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)  # File gets verbose logs
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        # Fallback to sys.stderr if log file is unwritable
        print(f"[Warning] Failed to initialize file logging: {e}", file=sys.stderr)

    return logger

# Export standard logger
logger = setup_logger()
