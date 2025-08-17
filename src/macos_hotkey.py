from __future__ import annotations

import platform
from typing import Callable, Optional
import logging
import threading


def register_ctrl_shift_t(
    on_hotkey: Callable[[], None],
) -> Optional[Callable[[], None]]:
    """Register a global Ctrl+Shift+T hotkey. Returns a stopper function or None."""
    if platform.system() != "Darwin":
        return None

    from Quartz import (
        CGEventTapCreate,
        kCGSessionEventTap,
        kCGHeadInsertEventTap,
        CGEventMaskBit,
        kCGEventKeyDown,
        CGEventTapEnable,
        CGEventGetFlags,
        CGEventGetIntegerValueField,
        kCGKeyboardEventKeycode,
        kCGEventFlagMaskShift,
        kCGEventFlagMaskControl,
    )
    from CoreFoundation import (
        CFMachPortCreateRunLoopSource,
        CFRunLoopAddSource,
        CFRunLoopGetCurrent,
        CFRunLoopRun,
        CFRunLoopStop,
        kCFRunLoopCommonModes,
    )

    CTRL_SHIFT = int(kCGEventFlagMaskControl) | int(kCGEventFlagMaskShift)
    KEYCODE_T = 17  # ANSI T

    state = {"tap": None, "runloop": None, "thread": None}

    def _run_loop_thread():
        try:

            def _tap_cb(proxy, type_, event, refcon):  # noqa: N803
                try:
                    if type_ != kCGEventKeyDown:
                        return event
                    flags = int(CGEventGetFlags(event))
                    keycode = int(
                        CGEventGetIntegerValueField(event, kCGKeyboardEventKeycode)
                    )
                    if (flags & CTRL_SHIFT) == CTRL_SHIFT and keycode == KEYCODE_T:
                        logging.debug("Hotkey Ctrl+Shift+T detected")
                        try:
                            threading.Thread(target=on_hotkey, daemon=True).start()
                        except Exception:
                            on_hotkey()
                        return None
                except Exception:
                    pass
                return event

            tap = CGEventTapCreate(
                kCGSessionEventTap,
                kCGHeadInsertEventTap,
                0,
                CGEventMaskBit(kCGEventKeyDown),
                _tap_cb,
                None,
            )
            if not tap:
                logging.warning(
                    "CGEventTapCreate returned NULL; hotkey unavailable (permissions?)"
                )
                return

            rl = CFRunLoopGetCurrent()
            src = CFMachPortCreateRunLoopSource(None, tap, 0)
            CFRunLoopAddSource(rl, src, kCFRunLoopCommonModes)
            CGEventTapEnable(tap, True)
            logging.debug("CGEventTap enabled for Ctrl+Shift+T")

            state["tap"] = tap
            state["runloop"] = rl
            CFRunLoopRun()
        except Exception as e:
            logging.exception("Hotkey runloop error: %s", e)

    listener_thread = threading.Thread(
        target=_run_loop_thread, name="macos-hotkey", daemon=True
    )
    listener_thread.start()
    state["thread"] = listener_thread

    def _stop() -> None:
        try:
            tap = state.get("tap")
            rl = state.get("runloop")
            if tap is not None:
                try:
                    CGEventTapEnable(tap, False)
                except Exception:
                    pass
            if rl is not None:
                try:
                    CFRunLoopStop(rl)
                except Exception:
                    pass
        finally:
            thread_obj = state.get("thread")
            if thread_obj and thread_obj.is_alive():
                try:
                    thread_obj.join(timeout=0.5)
                except Exception:
                    pass

    return _stop


def maybe_register_ctrl_shift_t(
    on_hotkey: Callable[[], None],
) -> Optional[Callable[[], None]]:
    """Register Ctrl+Shift+T if on macOS. Returns stopper or None."""
    if platform.system() != "Darwin":
        return None
    stop_listener = register_ctrl_shift_t(on_hotkey)
    if stop_listener:
        logging.info("Registered macOS global hotkey: ctrl+shift+t")
    else:
        logging.warning("Global hotkey unavailable (permissions or environment)")
    return stop_listener
