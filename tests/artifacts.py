"""Test captures live outside the checkout; export only when explicitly requested."""

import atexit
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_temp = tempfile.TemporaryDirectory(prefix="orvex-tests-")
atexit.register(_temp.cleanup)


def capture_dir(group):
    root = Path(os.environ.get("ORVEX_CAPTURE_DIR", _temp.name)).resolve()
    if root.is_relative_to(ROOT):
        raise ValueError("ORVEX_CAPTURE_DIR must be outside the source checkout")
    result = root / group
    result.mkdir(parents=True, exist_ok=True)
    return result
