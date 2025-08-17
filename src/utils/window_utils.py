"""
Window‑utility helpers for cross‑platform Tk layouts.
Pure functions—no hidden windows, no side effects.
"""

from __future__ import annotations

import subprocess
import tkinter as tk
from typing import Optional, Tuple
import platform

_XRANDR_TIMEOUT_S = 2
_FALLBACK_GEOM: Tuple[int, int, int, int] = (0, 0, 1920, 1080)


def _parse_xrandr_geometry(line: str) -> Optional[Tuple[int, int, int, int]]:
    """Return (x, y, w, h) if *line* contains a valid <WxH+X+Y> geometry."""
    for token in line.split():
        if "x" not in token or "+" not in token:
            continue
        geo = token.split("+")
        if len(geo) != 3:
            continue
        size = geo[0].split("x")
        if len(size) != 2:
            continue
        try:
            width, height = map(int, size)
            x, y = map(int, geo[1:])
        except ValueError:
            continue
        return x, y, width, height
    return None


def get_primary_monitor_geometry(
    fallback: Tuple[int, int, int, int] = _FALLBACK_GEOM,
) -> Tuple[int, int, int, int]:
    """
    Geometry of the primary monitor as ``(x, y, width, height)``.
    Uses ``xrandr``. Falls back to *fallback* if unavailable.
    """
    try:
        res = subprocess.run(
            ["xrandr", "--query"],
            capture_output=True,
            text=True,
            timeout=_XRANDR_TIMEOUT_S,
            check=False,
        )
    except Exception:
        return fallback

    for line in res.stdout.splitlines():
        if " primary " not in line or " connected " not in line:
            continue
        parsed = _parse_xrandr_geometry(line)
        if parsed:
            return parsed

    return fallback


def center_window_on_primary_monitor(window: tk.Tk, width: int, height: int) -> None:
    """
    Place *window* centred on the primary monitor with given *width*, *height*.
    """
    mon_x, mon_y, mon_w, mon_h = get_primary_monitor_geometry()
    x = mon_x + (mon_w - width) // 2
    y = mon_y + (mon_h - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")


def restore_window_to_front(window: tk.Misc) -> None:
    """Restore and focus a Tk window with platform-specific activation.

    This is the single point for app activation/focus behavior.
    """
    try:
        if platform.system() == "Darwin":
            try:
                from AppKit import (
                    NSRunningApplication,
                    NSApplicationActivateIgnoringOtherApps,
                )

                NSRunningApplication.currentApplication().activateWithOptions_(
                    NSApplicationActivateIgnoringOtherApps
                )
            except Exception:
                pass

        window.deiconify()
        window.lift()
        try:
            window.focus_force()
        except Exception:
            pass
    except Exception:
        pass


def restore_app_to_front() -> None:
    """Restore the running app and its root Tk window if available."""
    try:
        root = getattr(tk, "_default_root", None)
        if root is not None:
            restore_window_to_front(root)
    except Exception:
        pass
