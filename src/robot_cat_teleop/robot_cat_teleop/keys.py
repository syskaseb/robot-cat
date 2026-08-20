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

STOP = "stop"
QUIT = "quit"

_ESC = 0x1B
_CTRL_C = 0x03


def decode_keys(data: bytes) -> tuple[list[str], bytes]:
    """Turn a chunk of raw terminal input into key events.

    Args:
        data: Bytes read from the terminal, possibly several keystrokes and
            possibly ending mid-escape-sequence.

    Returns:
        ``(events, leftover)``. ``events`` are names from :data:`ARROWS` plus
        :data:`STOP` and :data:`QUIT`. ``leftover`` is a trailing partial
        escape sequence, which the caller must prepend to the next chunk -
        otherwise a keystroke split across two reads is lost.
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
            events.append(STOP)
        elif byte in (_CTRL_C, 0x71, 0x51):  # Ctrl-C, q, Q
            events.append(QUIT)
        i += 1

    return events, b""
