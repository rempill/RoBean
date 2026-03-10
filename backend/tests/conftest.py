"""Test configuration.

These tests import internal backend packages like `scraper` using absolute imports.
When running pytest from the repo root, `backend/` isn't automatically on PYTHONPATH,
so we add it here for consistent local and CI runs.
"""

import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
