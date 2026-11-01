"""Supply Chain Digital Twin backend application."""

import sys
import os

_current = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.dirname(_current)
_root_dir = os.path.dirname(_backend_dir)

for _p in [_root_dir, _backend_dir, _current]:
    if _p not in sys.path:
        sys.path.insert(0, _p)
