"""
Pytest configuration for integration and system tests.
"""
import sys
from pathlib import Path

# Ensure src/ is in sys.path for all tests
SRC_PATH = Path(__file__).parent.parent / 'src'
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))
