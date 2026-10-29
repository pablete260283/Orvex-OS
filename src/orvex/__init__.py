"""ORVEX's custom QML controls require a customizable cross-platform Qt style."""
import os

os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Basic")
__version__ = "0.4.0"
