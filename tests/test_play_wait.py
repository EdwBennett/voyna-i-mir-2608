"""Tests for play_wait.py, the pause step between English and Russian playback."""

from unittest.mock import MagicMock

import voyna_i_mir_2608.play.play_wait as play_wait_module


def test_play_wait_sleeps_for_given_seconds(monkeypatch):
    mock_sleep = MagicMock()
    monkeypatch.setattr(play_wait_module.time, "sleep", mock_sleep)

    play_wait_module.play_wait(5)()

    mock_sleep.assert_called_once_with(5)


def test_play_wait_key_blocks_until_space_is_read(monkeypatch):
    monkeypatch.setattr(play_wait_module.sys.stdin, "fileno", MagicMock(return_value=0))
    monkeypatch.setattr(play_wait_module.termios, "tcgetattr", MagicMock(return_value="old-settings"))
    mock_tcsetattr = MagicMock()
    monkeypatch.setattr(play_wait_module.termios, "tcsetattr", mock_tcsetattr)
    monkeypatch.setattr(play_wait_module.tty, "setraw", MagicMock())
    mock_read = MagicMock(side_effect=["x", "y", " "])
    monkeypatch.setattr(play_wait_module.sys.stdin, "read", mock_read)

    play_wait_module.play_wait_key()()

    assert mock_read.call_count == 3
    mock_tcsetattr.assert_called_once_with(
        play_wait_module.sys.stdin.fileno(), play_wait_module.termios.TCSADRAIN, "old-settings"
    )


def test_play_wait_key_restores_terminal_settings_even_if_read_raises(monkeypatch):
    monkeypatch.setattr(play_wait_module.sys.stdin, "fileno", MagicMock(return_value=0))
    monkeypatch.setattr(play_wait_module.termios, "tcgetattr", MagicMock(return_value="old-settings"))
    mock_tcsetattr = MagicMock()
    monkeypatch.setattr(play_wait_module.termios, "tcsetattr", mock_tcsetattr)
    monkeypatch.setattr(play_wait_module.tty, "setraw", MagicMock())
    monkeypatch.setattr(play_wait_module.sys.stdin, "read", MagicMock(side_effect=KeyboardInterrupt))

    try:
        play_wait_module.play_wait_key()()
    except KeyboardInterrupt:
        pass

    mock_tcsetattr.assert_called_once_with(
        play_wait_module.sys.stdin.fileno(), play_wait_module.termios.TCSADRAIN, "old-settings"
    )
