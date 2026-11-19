"""PairBack application service: matching, records, persistence, and undo."""
import csv, json
from pathlib import Path
from datetime import date
from data_structures import ArrayList, UndoStack, merge_sort, binary_search

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "records.json"
FIELDS = ["report_id", "report_type", "item_name", "description", "category",
          "color", "brand", "location", "report_date", "status"]

SAMPLE_RECORDS = [
 {"report_id":"L001","report_type":"Lost","item_name":"Blue water bottle","description":"Blue insulated bottle with a silver lid","category":"Bottle","color":"Blue","brand":"Hydro Flask","location":"Library","report_date":"2026-11-15","status":"open"},
 {"report_id":"F001","report_type":"Found","item_name":"Blue bottle","description":"Insulated bottle with silver cap left on a study table","category":"Bottle","color":"Blue","brand":"Hydro Flask","location":"Library","report_date":"2026-11-16","status":"available"},
 {"report_id":"L002","report_type":"Lost","item_name":"Black umbrella","description":"Folding umbrella with curved handle","category":"Umbrella","color":"Black","brand":"Generic","location":"Main Gate","report_date":"2026-11-17","status":"open"},
 {"report_id":"F002","report_type":"Found","item_name":"Black umbrella","description":"Compact black folding umbrella","category":"Umbrella","color":"Black","brand":"Generic","location":"Cafeteria","report_date":"2026-11-17","status":"available"},
 {"report_id":"L003","report_type":"Lost","item_name":"Red notebook","description":"Small red spiral notebook","category":"Notebook","color":"Red","brand":"Muji","location":"Classroom Building","report_date":"2026-11-12","status":"open"},
 {"report_id":"F003","report_type":"Found","item_name":"Red notebook","description":"Red notebook with spiral binding","category":"Notebook","color":"Red","brand":"Muji","location":"Classroom Building","report_date":"2026-11-13","status":"available"},
 {"report_id":"F004","report_type":"Found","item_name":"White USB-C charger","description":"White wall adapter","category":"Electronics","color":"White","brand":"Anker","location":"Library","report_date":"2026-11-18","status":"available"},
]

class PairBack:
    WEIGHTS = {"category":30, "color":25, "brand":20, "location":15, "date":10}
    def __init__(self, data_file=DATA_FILE, seed=True):
        self.data_file = Path(data_file)
        self.records = ArrayList()
        self.history = UndoStack()
        self.load(seed=seed)

    def _save(self):
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        temp = self.data_file.with_suffix(".tmp")
        temp.write_text(json.dumps(self.records.to_list(), indent=2), encoding="utf-8")
        temp.replace(self.data_file)

    def load(self, seed=True):
        if self.data_file.exists():
            try: data = json.loads(self.data_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError): data = []
        else: data = SAMPLE_RECORDS if seed else []
        self.records = ArrayList(data)
        if not self.data_file.exists() and seed: self._save()

    def all_records(self): return self.records.to_list()

    def sorted_index(self):
        return merge_sort(self.all_records(), key=lambda r: r["report_id"])

    def find(self, report_id):
        return binary_search(self.sorted_index(), report_id.strip())

    def add(self, payload):
        required = ["report_type","item_name","category","color","location","report_date"]
        clean = {key: str(payload.get(key, "")).strip() for key in FIELDS}
        for key in required:
            if not clean[key]: raise ValueError(f"{key.replace('_',' ').title()} is required.")
        if clean["report_type"] not in ("Lost", "Found"): raise ValueError("Report type must be Lost or Found.")
        try: date.fromisoformat(clean["report_date"])
        except ValueError: raise ValueError("Enter a valid report date.")
        clean["report_id"] = clean["report_id"] or self._next_id(clean["report_type"])
        if self.find(clean["report_id"]): raise ValueError("That report ID already exists.")
        clean["status"] = "open" if clean["report_type"] == "Lost" else "available"
        self.records.append(clean); self._save()
        return clean

    def _next_id(self, kind):
        prefix = "L" if kind == "Lost" else "F"
        nums = [int(r["report_id"][1:]) for r in self.records
                if r["report_id"].startswith(prefix) and r["report_id"][1:].isdigit()]
        return f"{prefix}{max(nums, default=0)+1:03d}"

    def set_status(self, report_id, status):
        record = self.find(report_id)
        if not record: raise ValueError("Report not found.")
        if status not in ("open","available","released","resolved"): raise ValueError("Invalid status.")
        if record["status"] == status: return False
        self.history.push({"report_id":report_id,"previous":record["status"],"current":status})
        record["status"] = status
        self._save()
        return True

    def undo(self):
        change = self.history.pop()
        if not change: return None
        record = self.find(change["report_id"])
        if record:
            record["status"] = change["previous"]
            self._save()
        return change

    def matches(self, lost_id):
        lost = self.find(lost_id)
        if not lost or lost["report_type"] != "Lost": raise ValueError("Choose a valid lost-item report.")
        candidates = []
        for found in self.records:
            if found["report_type"] != "Found" or found["status"] != "available": continue
            reasons, score = [], 0
            for field, weight in self.WEIGHTS.items():
                a, b = lost.get(field,"").strip().casefold(), found.get(field,"").strip().casefold()
                matched = bool(a and b and a == b)
                if matched: score += weight
                reasons.append({"field":field.title(),"matched":matched,"weight":weight,
                                "lost":lost.get(field) or "Not provided","found":found.get(field) or "Not provided"})
            candidates.append({"record":found,"score":score,"reasons":reasons})
        # Descending score, then ascending report ID; merge sort is student implementation.
        return merge_sort(candidates, key=lambda c: (-c["score"], c["record"]["report_id"]))

    def export_csv(self, destination):
        with open(destination, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader(); writer.writerows(self.all_records())
