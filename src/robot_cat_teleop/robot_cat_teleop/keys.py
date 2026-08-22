"""Decoding of terminal key input. Pure byte manipulation, no ROS, no I/O.

Arrow keys do not arrive as characters. Each one is a three-byte escape
sequence, and which sequence depends on the terminal's cursor-key mode:

===============  =========
mode             up arrow
===============  =========
normal (CSI)     ``ESC [ A``
application(SS3) ``ESC O A``
===============  =========

Terminals switch between the two freely - tmux, screen, vim and most curses
applications leave the terminal in application mode - so both are accepted.

Input must be read from the raw file descriptor with :func:`os.read`, not
through ``sys.stdin``. Python's buffered text reader pulls the whole escape
sequence into its own buffer on the first one-byte read, after which
``select()`` on the descriptor reports nothing pending and the rest of the
sequence is silently lost - which looks exactly like the arrow keys not
working.
"""

from __future__ import annotations

#: Final byte of an arrow-key sequence -> event name.
ARROWS: dict[str, str] = {"A": "up", "B": "down", "C": "right", "D": "left"}

#: Byte that follows ESC. ``[`` is normal cursor-key mode, ``O`` application.
INTRODUCERS: tuple[bytes, ...] = (b"[", b"O")

#: Space steps the tail through its sweep. It used to mean "stop", which was
#: always redundant: the body already halts within `key_hold_timeout` of the
#: arrows being released, and the gait watchdog stops it again 0.5 s later.
TAIL_STEP = "tail_step"
QUIT = "quit"

#: Cycles the Gazebo camera: free -> third-person -> first-person -> free.
CAMERA_CYCLE = "camera_cycle"

#: Plays a meow through the host's speakers - Gazebo itself has no audio.
MEOW = "meow"

#: WASD drives the head, not the body, so its events get their own names
#: rather than reusing "up"/"down"/"left"/"right" from the arrows.
HEAD_UP = "head_up"
HEAD_DOWN = "head_down"
HEAD_LEFT = "head_left"
HEAD_RIGHT = "head_right"

#: Plain ASCII, both cases - unlike the arrows these are single bytes, no
#: escape sequence involved.
WASD: dict[int, str] = {
    ord("w"): HEAD_UP,
    ord("W"): HEAD_UP,
    ord("s"): HEAD_DOWN,
    ord("S"): HEAD_DOWN,
    ord("a"): HEAD_LEFT,
    ord("A"): HEAD_LEFT,
    ord("d"): HEAD_RIGHT,
    ord("D"): HEAD_RIGHT,
}

_ESC = 0x1B
_CTRL_C = 0x03


def decode_keys(data: bytes) -> tuple[list[str], bytes]:
    """Turn a chunk of raw terminal input into key events.

    Args:
        data: Bytes read from the terminal, possibly several keystrokes and
            possibly ending mid-escape-sequence.

    Returns:
        ``(events, leftover)``. ``events`` are names from :data:`ARROWS` and
        :data:`WASD` plus :data:`TAIL_STEP` and :data:`QUIT`. ``leftover`` is
        a trailing partial escape sequence, which the caller must prepend to
        the next chunk - otherwise a keystroke split across two reads is
        lost.
    """
    events: list[str] = []
    i = 0
    end = len(data)

    while i < end:
        byte = data[i]

        if byte == _ESC:
            # Need three bytes for a complete sequence; if they have not all
            # arrived yet, hand the fragment back rather than dropping it.
            if i + 2 >= end:
                return events, data[i:]
            if data[i + 1 : i + 2] not in INTRODUCERS:
                i += 1  # bare ESC, or an escape sequence we do not care about
                continue
            arrow = ARROWS.get(chr(data[i + 2]))
            if arrow is not None:
                events.append(arrow)
            i += 3
            continue

        if byte == 0x20:  # space
            events.append(TAIL_STEP)
        elif byte in (_CTRL_C, 0x71, 0x51):  # Ctrl-C, q, Q
            events.append(QUIT)
        elif byte in (0x76, 0x56):  # v, V
            events.append(CAMERA_CYCLE)
        elif byte in (0x6D, 0x4D):  # m, M
            events.append(MEOW)
        elif byte in WASD:
            events.append(WASD[byte])
        i += 1

    return events, b""
