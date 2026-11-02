#!/usr/bin/env python3
"""Run repository tests from any current directory; fail if discovery is empty."""
from pathlib import Path
import sys
import unittest
root = Path(__file__).resolve().parents[1]
suite = unittest.TestLoader().discover(str(root / "tests"))
if suite.countTestCases() == 0:
    sys.exit("STOP: no tests discovered")
result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
