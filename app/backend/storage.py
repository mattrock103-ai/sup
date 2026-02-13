from __future__ import annotations

from pathlib import Path
from typing import Final

APP_ROOT: Final[Path] = Path(__file__).resolve().parents[1]
DATA_DIR: Final[Path] = APP_ROOT / "data"
UPLOADS_DIR: Final[Path] = DATA_DIR / "uploads"
OUTPUTS_DIR: Final[Path] = DATA_DIR / "outputs"
TEMPLATE_PATH: Final[Path] = DATA_DIR / "template.docx"
DEFAULT_TEMPLATE_PATH: Final[Path] = APP_ROOT / "templates" / "base_template.docx"

MAX_TEMPLATE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_CV_SIZE = 12 * 1024 * 1024  # 12MB


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    DEFAULT_TEMPLATE_PATH.parent.mkdir(parents=True, exist_ok=True)


def template_exists() -> bool:
    return TEMPLATE_PATH.exists()


def get_template_path() -> Path:
    if TEMPLATE_PATH.exists():
        return TEMPLATE_PATH
    return DEFAULT_TEMPLATE_PATH
