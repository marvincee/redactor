"""Native macOS clipboard helpers."""

from __future__ import annotations

import subprocess


class ClipboardError(RuntimeError):
    """Raised when the macOS clipboard tools are unavailable or fail."""


def read_clipboard() -> str:
    """Read text from the macOS clipboard using `pbpaste`."""
    try:
        completed_process = subprocess.run(
            ["pbpaste"],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise ClipboardError("macOS clipboard tools are not available on this system.") from exc
    except subprocess.CalledProcessError as exc:
        raise ClipboardError("Unable to read from the clipboard.") from exc

    return completed_process.stdout


def write_clipboard(text: str) -> None:
    """Write text to the macOS clipboard using `pbcopy`."""
    try:
        subprocess.run(
            ["pbcopy"],
            check=True,
            text=True,
            input=text,
        )
    except FileNotFoundError as exc:
        raise ClipboardError("macOS clipboard tools are not available on this system.") from exc
    except subprocess.CalledProcessError as exc:
        raise ClipboardError("Unable to write to the clipboard.") from exc
