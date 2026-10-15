"""Create only missing Unity GUID files before importing additive art/code."""
from hashlib import md5
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for folder in (ROOT / "Assets/Art", ROOT / "Assets/Editor", ROOT / "Assets/Scripts/Game"):
    for path in sorted(folder.rglob("*")):
        if path.suffix == ".meta":
            continue
        meta = Path(str(path) + ".meta")
        if meta.exists():
            continue
        relative = path.relative_to(ROOT).as_posix()
        guid = md5(relative.encode()).hexdigest()
        text = f"fileFormatVersion: 2\nguid: {guid}\n"
        if path.is_dir():
            text += "folderAsset: yes\nDefaultImporter:\n  externalObjects: {}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n"
        meta.write_text("\n".join(line.rstrip() for line in text.splitlines()) + "\n")
        print(relative)
