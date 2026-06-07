from __future__ import annotations

from pathlib import Path
from datasets import load_dataset

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
DATASETS = [
    "theatticusproject/cuad",
    "theatticusproject/cuad-qa",
    "nielsr/funsd",
    "Voxel51/consolidated_receipt_dataset",
]


def safe_name(name: str) -> str:
    return name.replace("/", "__")


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for name in DATASETS:
        print(f"Attempting download: {name}")
        try:
            dataset = load_dataset(name)
            out = RAW_DIR / safe_name(name)
            dataset.save_to_disk(str(out))
            print(f"Downloaded {name} -> {out}")
        except Exception as exc:
            print(f"Skipped {name}: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    main()
