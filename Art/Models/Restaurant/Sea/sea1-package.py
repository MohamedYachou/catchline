"""Current brighter exact-periodic sea1 exporter; SEA-1C supersedes prior tiles."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('sea1c-package.py')),run_name='__main__')
