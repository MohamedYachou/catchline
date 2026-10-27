import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import review
review.individual(stems={'WindowFlowerBox','HangingHerbs','BarBottleShelf','ReedVase'})
review.grid()
