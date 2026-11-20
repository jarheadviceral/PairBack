"""PairBack service: DSWS-aligned reports, matching, release, and undo."""

import csv
import json
from datetime import date, time
from pathlib import Path

from data_structures import ArrayList, UndoStack, heap_sort, quick_sort
from locations import compose_location, location_key


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "records.json"

FIELDS = [
    "report_id",
    "report_type",
    "item_name",
    "description",
    "category",
    "color",
    "brand",
    "location",
    "report_date",
    "report_time",
    "intake_channel",
    "custody_location",
    "status",
]

LOST_INTAKE_CHANNELS = {
    "In Person - MVP 101",
    "Online Lost Items Report Form",
    "Email",
}
FOUND_INTAKE_CHANNELS = {
    "In Person - MVP 101",
    "OADSA Turnover - Xavier Hall",
}
CUSTODY_LOCATIONS = {"MVP 101", "OADSA - Xavier Hall"}

SAMPLE_RECORDS = [
    {
        "report_id": "L001",
        "report_type": "Lost",
        "item_name": "Blue water bottle",
        "description": "Blue insulated bottle with a silver lid",
        "category": "Bottle",
        "color": "Blue",
        "brand": "Hydro Flask",
        "location": "New Rizal Library · Floor 3",
        "report_date": "2026-11-15",
        "report_time": "14:30",
        "intake_channel": "Online Lost Items Report Form",
        "custody_location": "",
        "status": "open",
    },
    {
        "report_id": "F001",
        "report_type": "Found",
        "item_name": "Blue bottle",
        "description": "Insulated bottle with silver cap left on a study table",
        "category": "Bottle",
        "color": "Blue",
        "brand": "Hydro Flask",
        "location": "New Rizal Library · Floor 3",
        "report_date": "2026-11-16",
        "report_time": "09:15",
        "intake_channel": "In Person - MVP 101",
        "custody_location": "MVP 101",
        "status": "available",
    },
    {
        "report_id": "L002",
        "report_type": "Lost",
        "item_name": "Black umbrella",
        "description": "Folding umbrella with curved handle",
        "category": "Umbrella",
        "color": "Black",
        "brand": "Generic",
        "location": "SEC A · Escaler Hall",
        "report_date": "2026-11-17",
        "report_time": "17:00",
        "intake_channel": "Email",
        "custody_location": "",
        "status": "open",
    },
    {
        "report_id": "F002",
        "report_type": "Found",
        "item_name": "Black umbrella",
        "description": "Compact black folding umbrella",
        "category": "Umbrella",
        "color": "Black",
        "brand": "Generic",
        "location": "Gonzaga Cafeteria · GONZ 2",
        "report_date": "2026-11-17",
        "report_time": "18:10",
        "intake_channel": "OADSA Turnover - Xavier Hall",
        "custody_location": "OADSA - Xavier Hall",
        "status": "available",
    },
    {
        "report_id": "L003",
        "report_type": "Lost",
        "item_name": "Red notebook",
        "description": "Small red spiral notebook",
        "category": "Notebook",
        "color": "Red",
        "brand": "Muji",
        "location": "SOM · 201",
        "report_date": "2026-11-12",
        "report_time": "11:20",
        "intake_channel": "In Person - MVP 101",
        "custody_location": "",
        "status": "open",
    },
    {
        "report_id": "F003",
        "report_type": "Found",
        "item_name": "Red notebook",
        "description": "Red notebook with spiral binding",
        "category": "Notebook",
        "color": "Red",
        "brand": "Muji",
        "location": "SOM · 201",
        "report_date": "2026-11-13",
        "report_time": "08:40",
        "intake_channel": "In Person - MVP 101",
        "custody_location": "MVP 101",
        "status": "available",
    },
]


class PairBack:
    WEIGHTS = {
        "category": 30,
        "color": 25,
        "brand": 20,
        "location": 15,
        "report_date": 10,
    }

    def __init__(self, data_file=DATA_FILE, seed=True):
        self.data_file = Path(data_file)
        self.records = ArrayList()
        self.history = UndoStack()
        self.load(seed=seed)

    def _normalize_record(self, raw):
        record = {field: str(raw.get(field, "")).strip() for field in FIELDS}

        # Backward compatibility for records made before the DSWS fields existed.
        if not record["report_time"]:
            record["report_time"] = ""
        if not record["intake_channel"]:
            record["intake_channel"] = "Legacy import"
        if record["report_type"] == "Found" and not record["custody_location"]:
            record["custody_location"] = "Unknown"
        return record

    def _save(self):
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.data_file.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(self.records.to_list(), indent=2),
            encoding="utf-8",
        )
        temporary.replace(self.data_file)

    def load(self, seed=True):
        if self.data_file.exists():
            try:
                raw_records = json.loads(
                    self.data_file.read_text(encoding="utf-8")
                )
            except (json.JSONDecodeError, OSError) as error:
                raise ValueError("Cannot read existing records; restore or repair the data file.") from error
        else:
            raw_records = SAMPLE_RECORDS if seed else []

        # Refresh only exact, unedited legacy demo records. User-entered or
        # modified records are never matched by ID alone.
        old_locations = {
            "L001": "Library", "F001": "Library", "L002": "Main Gate",
            "F002": "Cafeteria", "L003": "Classroom Building",
            "F003": "Classroom Building",
        }
        refreshed = False
        for raw in raw_records:
            for sample in SAMPLE_RECORDS:
                legacy = dict(sample, location=old_locations[sample["report_id"]])
                if raw == legacy:
                    raw["location"] = sample["location"]
                    refreshed = True
                    break
        self.records = ArrayList(
            self._normalize_record(record) for record in raw_records
        )
        if refreshed or (not self.data_file.exists() and seed):
            self._save()

    def all_records(self):
        return self.records.to_list()

    def sorted_records(self, records=None):
        """Use the final project's Quick Sort implementation."""
        source = self.all_records() if records is None else records
        return quick_sort(source, key=lambda record: record["report_id"])

    def find(self, report_id):
        """Linear Search: O(n) worst-case time and O(1) auxiliary space."""
        target = str(report_id).strip()
        for record in self.records:
            if record["report_id"] == target:
                return record
        return None

    def _validate_date_and_time(self, record):
        try:
            date.fromisoformat(record["report_date"])
        except ValueError as error:
            raise ValueError("Enter a valid date.") from error
        try:
            time.fromisoformat(record["report_time"])
        except ValueError as error:
            raise ValueError("Enter a valid time.") from error

    def _validate_dsws_intake(self, record):
        if record["report_type"] == "Lost":
            if record["intake_channel"] not in LOST_INTAKE_CHANNELS:
                raise ValueError(
                    "Lost reports must be received at MVP 101, through the "
                    "online Lost Items Report Form, or by DSWS email."
                )
            record["custody_location"] = ""
            return

        if record["intake_channel"] not in FOUND_INTAKE_CHANNELS:
            raise ValueError(
                "Found items must be surrendered at MVP 101 or turned over "
                "through OADSA at Xavier Hall."
            )
        if record["custody_location"] not in CUSTODY_LOCATIONS:
            raise ValueError("Select the current custody location of the item.")
        if (
            record["intake_channel"] == "In Person - MVP 101"
            and record["custody_location"] != "MVP 101"
        ):
            raise ValueError("An item received at MVP 101 must be stored at MVP 101.")
        if (
            record["intake_channel"] == "OADSA Turnover - Xavier Hall"
            and record["custody_location"] != "OADSA - Xavier Hall"
        ):
            raise ValueError(
                "An OADSA turnover must initially be recorded at Xavier Hall."
            )

    def add(self, payload):
        required = [
            "report_type",
            "item_name",
            "category",
            "color",
            "location",
            "report_date",
            "report_time",
            "intake_channel",
        ]
        clean = {
            field: str(payload.get(field, "")).strip()
            for field in FIELDS
        }
        if "building" in payload:
            clean["location"] = compose_location(
                payload.get("building", ""), payload.get("room", "")
            )

        for field in required:
            if not clean[field]:
                raise ValueError(
                    f"{field.replace('_', ' ').title()} is required."
                )
        if clean["report_type"] not in {"Lost", "Found"}:
            raise ValueError("Report type must be Lost or Found.")

        self._validate_date_and_time(clean)
        self._validate_dsws_intake(clean)

        clean["report_id"] = (
            clean["report_id"] or self._next_id(clean["report_type"])
        )
        if self.find(clean["report_id"]):
            raise ValueError("That report ID already exists.")

        clean["status"] = (
            "open" if clean["report_type"] == "Lost" else "available"
        )
        self.records.append(clean)
        self._save()
        return clean

    def _next_id(self, report_type):
        prefix = "L" if report_type == "Lost" else "F"
        numbers = [
            int(record["report_id"][1:])
            for record in self.records
            if record["report_id"].startswith(prefix)
            and record["report_id"][1:].isdigit()
        ]
        return f"{prefix}{max(numbers, default=0) + 1:03d}"

    def set_status(self, report_id, status):
        record = self.find(report_id)
        if not record:
            raise ValueError("Report not found.")
        if record["report_type"] == "Found":
            raise ValueError(
                "Found items must use the verified release process."
            )
        if status not in {"open", "resolved"}:
            raise ValueError("A lost report may only be open or resolved.")
        if record["status"] == status:
            return False

        self.history.push(
            {
                "report_id": report_id,
                "previous": record["status"],
                "current": status,
                "action": "status",
            }
        )
        record["status"] = status
        self._save()
        return True

    def release(
        self,
        report_id,
        valid_id_confirmed,
        proof_confirmed,
        release_location,
    ):
        """Release a found item only after the DSWS verification steps."""
        record = self.find(report_id)
        if not record or record["report_type"] != "Found":
            raise ValueError("Choose a valid found-item report.")
        if record["status"] != "available":
            raise ValueError("Only an available found item can be released.")
        if release_location != "MVP 101":
            raise ValueError("Found items may only be released at MVP 101.")
        if not (valid_id_confirmed or proof_confirmed):
            raise ValueError(
                "Confirm that the claimant provided sufficient proof of ownership."
            )

        self.history.push(
            {
                "report_id": report_id,
                "previous": record["status"],
                "current": "released",
                "previous_custody": record["custody_location"],
                "action": "verified release at MVP 101",
            }
        )
        record["status"] = "released"
        record["custody_location"] = "Released at MVP 101"
        self._save()
        return record

    def undo(self):
        change = self.history.pop()
        if not change:
            return None
        record = self.find(change["report_id"])
        if record:
            record["status"] = change["previous"]
            if (
                change.get("action") == "verified release at MVP 101"
                and record["report_type"] == "Found"
            ):
                record["custody_location"] = change["previous_custody"]
            self._save()
        return change

    @staticmethod
    def _candidate_has_higher_priority(first, second):
        if first["score"] != second["score"]:
            return first["score"] > second["score"]
        return (
            first["record"]["report_id"]
            < second["record"]["report_id"]
        )

    def matches(self, lost_id):
        lost = self.find(lost_id)
        if (
            not lost
            or lost["report_type"] != "Lost"
            or lost["status"] != "open"
        ):
            raise ValueError("Choose an open lost-item report.")

        candidates = []
        for found in self.records:
            if (
                found["report_type"] != "Found"
                or found["status"] != "available"
            ):
                continue

            reasons = []
            score = 0
            for field, weight in self.WEIGHTS.items():
                lost_value = lost.get(field, "").strip().casefold()
                found_value = found.get(field, "").strip().casefold()
                if field == "location":
                    lost_value = location_key(lost_value)
                    found_value = location_key(found_value)
                matched = bool(
                    lost_value
                    and found_value
                    and lost_value == found_value
                )
                if matched:
                    score += weight
                reasons.append(
                    {
                        "field": field.replace("_", " ").title(),
                        "matched": matched,
                        "weight": weight,
                        "lost": lost.get(field) or "Not provided",
                        "found": found.get(field) or "Not provided",
                    }
                )

            candidates.append(
                {"record": found, "score": score, "reasons": reasons}
            )

        return heap_sort(
            candidates,
            higher_priority=self._candidate_has_higher_priority,
        )

    def export_csv(self, destination):
        with open(
            destination,
            "w",
            newline="",
            encoding="utf-8-sig",
        ) as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(self.all_records())
