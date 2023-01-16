import sys

from . import dvg

__doc__ = """
Usage:
  python3 -m dvg [--help] ...
"""

if len(sys.argv) <= 1:
    print(__doc__)
    sys.exit(0)

dvg.main()
