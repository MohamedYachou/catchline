import sys,runpy
sys.dont_write_bytecode=True
from pathlib import Path
B=runpy.run_path(str(Path(__file__).resolve().parent/'build.py'),run_name='decor2_build')
B['build'](3,4)
B['build'](5,6)
B['build'](7,8)
