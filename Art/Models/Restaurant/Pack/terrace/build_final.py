import sys,runpy
sys.dont_write_bytecode=True
from pathlib import Path
O=Path(__file__).resolve().parent
m=runpy.run_path(str(O/'build.py'));m['build'](4,5)
