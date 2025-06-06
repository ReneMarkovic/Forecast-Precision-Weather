from pathlib import Path
import csv
from typing import Dict, List

def load_records(filename: str, subfolder: str = "") -> List[Dict]:
    """
    Load records from a CSV file located in a subfolder.
    """
    folder = Path("data") / subfolder if subfolder else Path("data")
    path = folder / filename

    if not path.exists():
        return []

    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)