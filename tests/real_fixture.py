"""Build an ORVEX-owned native process in a temporary directory, never a game."""

import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path


def build_fixture(root, code=0):
    windows = sys.platform == "win32"
    compiler = shutil.which("cl" if windows else "cc")
    if not compiler:
        reason = "Native C compiler unavailable; native process fixture not executed"
        if os.environ.get("ORVEX_REQUIRE_NATIVE_FIXTURE") == "1":
            raise RuntimeError(reason)
        raise unittest.SkipTest(reason)
    folder = Path(root) / "controlled app with spaces"
    folder.mkdir(exist_ok=True)
    source = Path(__file__).parent / "fixtures/controlled_app.c"
    target = folder / ("ORVEX controlled app.exe" if windows else "ORVEX controlled app")
    if windows:
        args = [
            compiler,
            "/nologo",
            "/TC",
            "/W3",
            "/std:c11",
            "/DEXIT_CODE=" + str(code),
            str(source),
            "/Fe" + str(target),
            "/Fo" + str(folder / "controlled.obj"),
        ]
    else:
        args = [compiler, "-DEXIT_CODE=" + str(code), str(source), "-o", str(target)]
    subprocess.run(args, check=True, capture_output=True, cwd=folder)
    return target
