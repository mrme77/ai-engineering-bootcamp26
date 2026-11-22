"""Test credential resolution without accessing the real macOS Keychain."""

import subprocess
from unittest.mock import Mock

import pytest

import credentials


@pytest.fixture
def keychain(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Isolate environment values and replace every Keychain command."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(credentials.sys, "platform", "darwin")
    command = Mock(return_value=subprocess.CompletedProcess([], 0, stdout="test-key\n"))
    monkeypatch.setattr(credentials.subprocess, "run", command)
    return command


def test_environment_takes_precedence(monkeypatch: pytest.MonkeyPatch, keychain: Mock) -> None:
    """Avoid accessing Keychain when the environment already supplies a key."""
    monkeypatch.setenv("OPENAI_API_KEY", " env-key ")
    assert credentials.get_api_key() == "env-key"
    keychain.assert_not_called()


def test_reads_keychain_with_captured_output(keychain: Mock) -> None:
    """Read the named service without printing its password."""
    assert credentials.get_api_key() == "test-key"
    keychain.assert_called_once_with(
        ["/usr/bin/security", "find-generic-password", "-s", "OPENAI_API_KEY", "-w"],
        capture_output=True, text=True, check=True, timeout=30,
    )


@pytest.mark.parametrize("error", [
    subprocess.CalledProcessError(44, "security", stderr="private-output"),
    subprocess.TimeoutExpired("security", 30),
    OSError("security unavailable"),
])
def test_keychain_failure_returns_none(keychain: Mock, error: Exception) -> None:
    """Handle missing entries, denied access, timeouts, and unavailable commands."""
    keychain.side_effect = error
    assert credentials.get_api_key() is None


def test_non_macos_skips_keychain(monkeypatch: pytest.MonkeyPatch, keychain: Mock) -> None:
    """Allow other platforms to use environment configuration only."""
    monkeypatch.setattr(credentials.sys, "platform", "linux")
    assert credentials.get_api_key() is None
    keychain.assert_not_called()


def test_empty_keychain_value_returns_none(keychain: Mock) -> None:
    """Treat empty stored credentials as missing configuration."""
    keychain.return_value.stdout = "\n"
    assert credentials.get_api_key() is None
