"""Prepare AgriMind runtime assets without committing large datasets to GitHub."""
from pathlib import Path
import sys
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
COLOR = RAW / "color"
DOWNLOAD = ROOT / "data" / "download"
DOWNLOAD.mkdir(parents=True, exist_ok=True)

DATA_URL = "https://github.com/spMohanty/PlantVillage-Dataset/raw/master/data.zip"
SPLIT_BASE = "https://raw.githubusercontent.com/spMohanty/PlantVillage-Dataset/master/"
SPLITS = {
    "color_train.txt": SPLIT_BASE + "download/splits/color_train.txt",
    "color_test.txt": SPLIT_BASE + "download/splits/color_test.txt",
}


def fetch(url: str, dest: Path) -> None:
    print(f"Downloading {url} -> {dest}")
    with urllib.request.urlopen(url) as r, dest.open("wb") as f:
        while True:
            chunk = r.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)


def main() -> int:
    for name, url in SPLITS.items():
        dest = DOWNLOAD / name
        if not dest.exists():
            fetch(url, dest)

    if not COLOR.exists():
        archive = DOWNLOAD / "data.zip"
        if not archive.exists():
            fetch(DATA_URL, archive)
        print("Extracting PlantVillage data.zip (this may take a while)...")
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(RAW)

    if not COLOR.exists():
        print(f"ERROR: expected color dataset at {COLOR}", file=sys.stderr)
        return 1

    print("AgriMind runtime assets are ready.")
    print(f"Images: {COLOR}")
    print(f"Train manifest: {DOWNLOAD / 'color_train.txt'}")
    print(f"Test manifest: {DOWNLOAD / 'color_test.txt'}")
    print("Next: train the disease model with:")
    print("  python -m ml.train_disease")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
