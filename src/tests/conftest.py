"""
Pytest configuration for unit tests.
"""
import sys
from pathlib import Path

# Ensure src/ is in sys.path for unit tests
SRC_PATH = Path(__file__).parent.parent
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))
