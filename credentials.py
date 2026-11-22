"""Resolve the OpenRouter key from the environment or macOS Keychain."""

import logging
import os
import subprocess
import sys

logger = logging.getLogger(__name__)


def get_api_key() -> str | None:
    """Read OPENAI_API_KEY, falling back to the matching Keychain service.

    Returns:
        The credential, or None when it is unavailable or access is denied.
    """
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if api_key:
        return api_key
    if sys.platform != "darwin":
        return None

    try:
        result = subprocess.run(
            ["/usr/bin/security", "find-generic-password", "-s", "OPENAI_API_KEY", "-w"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        # Exception text may contain command output; log only the error class.
        logger.warning("Keychain credential unavailable: %s", type(exc).__name__)
        return None
    return result.stdout.strip() or None
