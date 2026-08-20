"""Arrow keys are three-byte escape sequences, and getting that wrong fails
silently - the cat simply ignores you. These tests pin the decoder down."""

import pytest

from robot_cat_teleop.keys import ARROWS, QUIT, STOP, decode_keys


@pytest.mark.parametrize("introducer", [b"[", b"O"])
@pytest.mark.parametrize(
    "final,expected",
    [(b"A", "up"), (b"B", "down"), (b"C", "right"), (b"D", "left")],
)
def test_each_arrow_decodes_in_both_cursor_key_modes(introducer, final, expected):
    """`ESC [ A` is normal cursor-key mode, `ESC O A` is application mode.
    Terminals switch between them freely, so both must work."""
    events, leftover = decode_keys(b"\x1b" + introducer + final)
    assert events == [expected]
    assert leftover == b""


def test_autorepeat_burst_is_not_coalesced():
    """Holding a key produces a stream; every repeat must refresh the hold."""
    assert decode_keys(b"\x1b[A" * 5)[0] == ["up"] * 5


def test_several_distinct_keys_in_one_chunk():
    """A single read can contain a whole burst of different keys."""
    events, _ = decode_keys(b"\x1b[A\x1b[D\x1bOB \x1b[C")
    assert events == ["up", "left", "down", STOP, "right"]


# --- the bug that made the arrow keys do nothing ------------------------
# Reading via sys.stdin.read(1) pulled all three bytes into Python's buffer,
# after which select() reported nothing pending and the rest of the sequence
# was dropped. Reading the raw fd fixes it, but chunk boundaries can still
# split a sequence - hence the carry.


@pytest.mark.parametrize("split", [1, 2])
def test_sequence_split_across_two_reads_is_not_lost(split):
    head, tail = b"\x1b[A"[:split], b"\x1b[A"[split:]
    events, leftover = decode_keys(head)
    assert events == []
    assert leftover == head, "incomplete sequence must be handed back, not dropped"
    assert decode_keys(leftover + tail)[0] == ["up"]


def test_chunk_ending_mid_sequence_keeps_only_the_fragment():
    events, leftover = decode_keys(b"\x1b[A\x1b[")
    assert events == ["up"]
    assert leftover == b"\x1b["


def test_complete_input_leaves_no_carry():
    assert decode_keys(b"\x1b[A\x1b[B")[1] == b""


# --- other keys ---------------------------------------------------------


def test_space_stops_and_q_quits():
    assert decode_keys(b" ")[0] == [STOP]
    assert decode_keys(b"q")[0] == [QUIT]
    assert decode_keys(b"Q")[0] == [QUIT]


def test_ctrl_c_quits():
    assert decode_keys(b"\x03")[0] == [QUIT]


def test_unknown_escape_sequence_is_ignored():
    assert decode_keys(b"\x1b[Z")[0] == []


def test_bare_escape_is_ignored_not_carried_forever():
    """A lone ESC followed by ordinary text must not swallow the text."""
    assert decode_keys(b"\x1bXq")[0] == [QUIT]


def test_unrelated_characters_are_ignored():
    assert decode_keys(b"hello")[0] == []


def test_arrow_table_covers_all_four_directions():
    assert sorted(ARROWS.values()) == ["down", "left", "right", "up"]
