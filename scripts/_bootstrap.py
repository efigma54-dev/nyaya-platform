"""Ensure `app` package is importable (repo layout vs Docker /app layout)."""

from __future__ import annotations

import os
import sys


def ensure_backend_on_path() -> None:
    """Make `app` importable from repo root scripts or Docker (/app + /scripts)."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, ".."))

    for candidate in (
        os.environ.get("NYAYA_BACKEND_PATH"),
        "/app",
        os.path.join(repo_root, "backend"),
        repo_root,
    ):
        if not candidate:
            continue
        if os.path.isdir(os.path.join(candidate, "app")):
            if candidate not in sys.path:
                sys.path.insert(0, candidate)
            return

    raise RuntimeError(
        "Could not find backend package (app/). Set NYAYA_BACKEND_PATH or run from repo."
    )
