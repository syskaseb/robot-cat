"""Meow rate limiting, and that the clip is actually shipped and playable.

The rate limit is the whole point of the class: autorepeat fires ~30 times a
second while `m` is held, and without it each repeat would spawn its own
player process.
"""

import wave

import pytest

from robot_cat_teleop.meow import SOUND, Meower


def test_the_clip_is_present_in_the_package():
    assert SOUND.exists(), f"missing sound file: {SOUND}"


def test_the_clip_is_a_short_audible_mono_wav():
    with wave.open(str(SOUND)) as w:
        assert w.getnchannels() == 1
        assert w.getsampwidth() == 2
        duration = w.getnframes() / w.getframerate()
    assert 0.2 < duration < 2.0, "one meow, not the whole source recording"


def test_the_clip_is_neither_silent_nor_clipped():
    """Trimming and normalising is easy to get wrong in both directions - too
    quiet to hear over a fan, or squared off into buzz."""
    import struct

    with wave.open(str(SOUND)) as w:
        n = w.getnframes()
        samples = struct.unpack(f"<{n}h", w.readframes(n))
    peak = max(abs(s) for s in samples)
    assert peak > 16000, "too quiet"
    assert sum(1 for s in samples if abs(s) >= 32700) == 0, "clipped"


def test_the_clip_does_not_start_or_end_on_a_click():
    """A hard cut mid-waveform pops. The clip is faded at both ends."""
    import struct

    with wave.open(str(SOUND)) as w:
        n = w.getnframes()
        samples = struct.unpack(f"<{n}h", w.readframes(n))
    assert abs(samples[0]) < 500
    assert abs(samples[-1]) < 500


@pytest.fixture
def meower():
    m = Meower(min_interval=1.0)
    m._command = ["true"]  # available, but harmless when spawned
    return m


def test_first_press_plays(meower):
    assert meower.should_play(100.0)


def test_a_repeat_inside_the_interval_is_dropped(meower):
    meower.should_play(100.0)
    assert not meower.should_play(100.5)


def test_a_press_after_the_interval_plays(meower):
    meower.should_play(100.0)
    assert meower.should_play(101.5)


def test_a_held_key_produces_one_meow_per_interval(meower):
    """Autorepeat at 30 Hz for two seconds must not give 60 meows."""
    played = sum(1 for i in range(60) if meower.should_play(100.0 + i / 30.0))
    assert played == 2


def test_a_dropped_press_does_not_reset_the_clock(meower):
    meower.should_play(100.0)
    meower.should_play(100.3)  # dropped
    assert not meower.should_play(100.9), "the 0.3 press must not have re-armed"


def test_meow_reports_false_when_no_player_exists():
    m = Meower()
    m._command = None
    assert not m.available
    assert not m.meow(100.0)
