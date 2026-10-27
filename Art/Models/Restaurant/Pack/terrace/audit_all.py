import sys,runpy
sys.dont_write_bytecode=True
from pathlib import Path
O=Path(__file__).resolve().parent
sys.path.insert(0,str(O))
import review
review.audit()
runpy.run_path(str(O/'check_fbx.py'))
runpy.run_path(str(O/'audit_geometry.py'))
