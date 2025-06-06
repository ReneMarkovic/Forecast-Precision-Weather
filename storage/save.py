from pathlib import Path
import csv
from typing import Dict, List, Iterable

# Create main data directories if not exist
Path("data").mkdir(exist_ok=True)
Path("data/daily_forecasts").mkdir(exist_ok=True)
Path("data/hourly_forecasts").mkdir(exist_ok=True)
Path("data/actual_data").mkdir(exist_ok=True)


def save_records(filename: str, records: Iterable[Dict], subfolder: str = "") -> None:
    """
    Save a list of dictionaries to a CSV file.
    Automatically creates a subfolder if specified.
    """
    folder = Path("data") / subfolder if subfolder else Path("data")
    folder.mkdir(exist_ok=True)
    path = folder / filename

    if not records:
        return

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)