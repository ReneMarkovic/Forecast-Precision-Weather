import csv
from pathlib import Path
from typing import List, Dict, Iterable


DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


def save_records(filename: str, records: Iterable[Dict]) -> None:
    """Save a list of dictionaries to CSV."""
    path = DATA_DIR / filename
    if not records:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)


def load_records(filename: str) -> List[Dict]:
    """Load records from a CSV file."""
    path = DATA_DIR / filename
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)
