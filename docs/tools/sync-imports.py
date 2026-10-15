"""Copy verified Unity import settings/library back from the scratch project."""
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[2]
scratch = root.parent / "Catchline-sim"
for meta in (scratch / "Assets/Art").rglob("*.meta"):
    target = root / meta.relative_to(scratch)
    if Path(str(target)[:-5]).exists():
        text = "\n".join(line.rstrip() for line in meta.read_text().splitlines()) + "\n"
        current = "\n".join(line.rstrip() for line in target.read_text().splitlines()) + "\n" if target.exists() else ""
        if text != current:
            target.write_text(text)
shutil.copy2(scratch / "Assets/Resources/ArtLibrary.asset", root / "Assets/Resources/ArtLibrary.asset")
print("Copied verified art import metadata and ArtLibrary from Catchline-sim")
