"""Play the cat's meow.

Gazebo has no audio at all — there is no sound component in SDF and nothing
in gz-sim renders one — so this plays through the host instead. On macOS that
is ``afplay``, which ships with the OS.

``sounds/meow.wav`` is a real cat, trimmed to a single meow from
"Meow of a pleading cat" by Heismark on Wikimedia Commons, which is released
into the **public domain** - no attribution obligation and safe to vendor
into the repo. See ``sounds/SOURCE.md``. The first version of this was
synthesised from a harmonic stack; it was recognisably a meow and
recognisably not a cat.

Playback is fire-and-forget in a detached process. Blocking the teleop loop
for 0.6 s per meow would drop keystrokes and stall the head and tail
publishers, which run on the same thread.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

#: The clip is ~1.16 s. Retriggering faster than it just produces a stutter of
#: overlapping cats, and holding the key would spawn a process per autorepeat.
MIN_INTERVAL = 1.2

SOUND = Path(__file__).with_name("sounds") / "meow.wav"


def player_command() -> list[str] | None:
    """The command to play the clip, or None if this host cannot."""
    if not SOUND.exists():
        return None
    for exe in ("afplay", "aplay", "paplay"):
        found = shutil.which(exe)
        if found:
            return [found, str(SOUND)]
    return None


class Meower:
    """Rate-limits meows and spawns the player."""

    def __init__(self, min_interval: float = MIN_INTERVAL) -> None:
        self._min_interval = min_interval
        self._last = None
        self._command = player_command()

    @property
    def available(self) -> bool:
        return self._command is not None

    def should_play(self, now: float) -> bool:
        """True if enough time has passed since the last meow."""
        if self._last is not None and now - self._last < self._min_interval:
            return False
        self._last = now
        return True

    def meow(self, now: float) -> bool:
        """Play unless rate-limited. Returns whether a sound was started."""
        if not self.available or not self.should_play(now):
            return False
        try:
            subprocess.Popen(
                self._command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            return False
        return True
