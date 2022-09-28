import sys

from pathlib import Path


outfile = Path(sys.argv[1])
outfile.write_text('# Some build-time configuration data')
