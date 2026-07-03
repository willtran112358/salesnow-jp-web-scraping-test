"""Load company seed list."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import SRC


def load_companies() -> list[dict[str, Any]]:
    path = SRC / "companies.json"
    return json.loads(path.read_text(encoding="utf-8"))
