"""Top-level test configuration.

Set environment BEFORE any ``app`` import so the cached Settings singleton picks
up test values (offline LLM, SQLite, deterministic secrets).
"""
import os
import pathlib
import tempfile

_TEST_DB_PATH = pathlib.Path(tempfile.gettempdir()) / "veritas_test.db"

os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{_TEST_DB_PATH.as_posix()}")
os.environ.setdefault("ANTHROPIC_API_KEY", "")  # offline: deterministic fallbacks
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("DEMO_USERNAME", "demo")
os.environ.setdefault("DEMO_PASSWORD", "veritas")
os.environ.setdefault("STORAGE_DIR", str(pathlib.Path(tempfile.gettempdir()) / "veritas_uploads"))
