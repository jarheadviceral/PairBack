"""Reviewed CSV intake; validate the whole batch before changing the live store."""
import csv
import io
import tempfile
from pathlib import Path
from pairback import PairBack, FIELDS
from data_structures import ArrayList

IMPORT_FIELDS = ["item_name", "category", "color", "brand", "location", "report_date", "report_time", "description"]
REQUIRED = {"item_name", "category", "color", "location", "report_date", "report_time"}

def parse_csv(content):
    reader = csv.DictReader(io.StringIO(content))
    if not reader.fieldnames or not REQUIRED.issubset(reader.fieldnames):
        raise ValueError("Use the CSV template headers. Required: " + ", ".join(sorted(REQUIRED)))
    rows = []
    for index, row in enumerate(reader, 2):
        if index > 501:
            raise ValueError("Import at most 500 rows at a time.")
        if None in row or any(value is None for value in row.values()):
            raise ValueError(f"Row {index}: column count does not match the headers.")
        rows.append({field: row.get(field, "").strip() for field in IMPORT_FIELDS})
    if not rows:
        raise ValueError("The CSV has no data rows.")
    return rows

def fingerprint(row):
    return tuple(row.get(field, "").strip().casefold() for field in IMPORT_FIELDS)

def prepare_batch(store, rows):
    seen = {fingerprint(r) for r in store.all_records() if r["report_type"] == "Lost"}
    added, skipped = [], 0
    with tempfile.TemporaryDirectory() as directory:
        staged = PairBack(Path(directory) / "records.json", seed=False)
        staged.records = ArrayList(dict(r) for r in store.all_records())
        for index, row in enumerate(rows, 2):
            key = fingerprint(row)
            if key in seen:
                skipped += 1
                continue
            payload = dict(row, report_type="Lost", intake_channel="Online Lost Items Report Form")
            try:
                added.append(staged.add(payload))
            except ValueError as error:
                raise ValueError(f"Row {index}: {error}") from error
            seen.add(key)
    return added, skipped

def commit_batch(store, rows):
    added, skipped = prepare_batch(store, rows)
    previous = store.records
    store.records = ArrayList(store.all_records() + added)
    try:
        store._save()
    except OSError:
        store.records = previous
        raise
    return len(added), skipped
