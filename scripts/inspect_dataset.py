from __future__ import annotations

import argparse
from pathlib import Path
from datasets import load_dataset, load_from_disk

ROOT = Path(__file__).resolve().parents[1]


def readable(value, max_chars: int = 1000) -> str:
    text = repr(value)
    return text[:max_chars] + ("..." if len(text) > max_chars else "")


def inspect_dataset(name: str) -> None:
    local = ROOT / "data" / "raw" / name.replace("/", "__")
    dataset = load_from_disk(str(local)) if local.exists() else load_dataset(name)
    print(f"Dataset: {name}")
    for split, ds in dataset.items():
        print(f"\nSplit: {split}")
        print(f"Rows: {len(ds)}")
        print(f"Columns: {ds.column_names}")
        if len(ds):
            print("Example:")
            print(readable(ds[0]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inspect a Hugging Face dataset or downloaded snapshot.")
    parser.add_argument("name", nargs="?", default="theatticusproject/cuad")
    args = parser.parse_args()
    inspect_dataset(args.name)
