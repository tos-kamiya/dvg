import sys

from . import dvg
from . import dvgi

__doc__ = """
Usage: 
  python3 -m dvg dvg [--help] ...
  python3 -m dvg dvgi [--help] ...
"""

if len(sys.argv) <= 1:
    print(__doc__)
    sys.exit(0)

if sys.argv[1] == "dvg":
    del sys.argv[1]
    dvg.main()
elif sys.argv[1] == "dvgi":
    del sys.argv[1]
    dvgi.main()
else:
    print(__doc__)
    sys.exit(1)

