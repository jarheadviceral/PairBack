import tempfile
import unittest
import random
from pathlib import Path

from data_structures import ArrayList, UndoStack, insertion_sort, quick_sort
from pairback import PairBack, SAMPLE_RECORDS


class PairBackTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.app = PairBack(
            Path(self.temporary_directory.name) / "records.json",
            seed=False,
        )

    def tearDown(self):
        self.temporary_directory.cleanup()

    def lost_payload(self):
        return {
            "report_type": "Lost",
            "item_name": "Bottle",
            "description": "Blue insulated bottle",
            "category": "Bottle",
            "color": "Blue",
            "brand": "Hydro Flask",
            "location": "Library",
            "report_date": "2026-11-19",
            "report_time": "10:30",
            "intake_channel": "Online Lost Items Report Form",
        }

    def found_payload(self):
        return {
            "report_type": "Found",
            "item_name": "Bottle",
            "description": "Blue insulated bottle",
            "category": "Bottle",
            "color": "Blue",
            "brand": "Hydro Flask",
            "location": "Library",
            "report_date": "2026-11-19",
            "report_time": "11:00",
            "intake_channel": "In Person - MVP 101",
            "custody_location": "MVP 101",
        }

    def test_linear_search_empty_unsorted_and_missing_ids(self):
        self.assertIsNone(self.app.find("F001"))
        records = [{"report_id": value} for value in ["F003", "F001", "F002"]]
        for record in records:
            self.app.records.append(record)
        for record in records:
            self.assertIs(self.app.find(record["report_id"]), record)
        self.assertIs(self.app.find(" F001 "), records[1])
        self.assertIsNone(self.app.find("F004"))
        self.assertIsNone(self.app.find("f001"))

    def test_arraylist_growth_and_bounds(self):
        values = ArrayList()
        for number in range(1000):
            values.append(number)
        self.assertEqual(list(values), list(range(1000)))
        self.assertGreaterEqual(values.capacity, 1000)
        with self.assertRaises(IndexError):
            _ = values[-1]
        for number in reversed(range(1000)):
            self.assertEqual(values.pop_last(), number)
        with self.assertRaises(IndexError):
            values.pop_last()
        values.append("reused")
        self.assertEqual(values[0], "reused")

    def test_undo_stack_lifo(self):
        stack = UndoStack()
        for number in range(10):
            stack.push(number)
        self.assertEqual(stack.peek(), 9)
        self.assertEqual(
            [stack.pop() for _ in range(10)],
            list(reversed(range(10))),
        )
        self.assertTrue(stack.is_empty())
        self.assertIsNone(stack.pop())
        self.assertIsNone(stack.peek())

    def test_randomized_sorting_preserves_input_and_all_candidates(self):
        rng = random.Random(42)
        for size in [0, 1, 2, 17, 100, 1000]:
            values = [rng.randrange(20) for _ in range(size)]
            original = values[:]
            self.assertEqual(quick_sort(values, key=lambda x: x), sorted(values))
            self.assertEqual(values, original)
            candidates = [
                {"score": value, "record": {"report_id": f"F{i:04d}"}}
                for i, value in enumerate(values)
            ]
            rng.shuffle(candidates)
            original_candidates = candidates[:]
            self.assertEqual(
                insertion_sort(candidates, self.app._candidate_has_higher_priority),
                sorted(
                    candidates,
                    key=lambda item: (
                        -item["score"],
                        item["record"]["report_id"],
                    ),
                ),
            )
            self.assertEqual(candidates, original_candidates)

    def test_application_undo_reverses_changes_in_lifo_order(self):
        first = self.app.add(self.lost_payload())
        second = self.app.add(self.lost_payload())
        self.app.set_status(first["report_id"], "resolved")
        self.app.set_status(second["report_id"], "resolved")
        self.app.undo()
        self.assertEqual(second["status"], "open")
        self.assertEqual(first["status"], "resolved")
        self.app.undo()
        self.assertEqual(first["status"], "open")
        self.assertIsNone(self.app.undo())

    def test_quick_sort_orders_records_without_changing_input(self):
        records = [
            {"report_id": "F003"},
            {"report_id": "F001"},
            {"report_id": "F002"},
        ]
        ordered = quick_sort(records, key=lambda item: item["report_id"])
        self.assertEqual(
            [item["report_id"] for item in ordered],
            ["F001", "F002", "F003"],
        )
        self.assertEqual(records[0]["report_id"], "F003")

    def test_quick_sort_handles_limits_and_adversarial_partitions(self):
        self.assertEqual(quick_sort([], key=lambda value: value), [])
        self.assertEqual(quick_sort([1], key=lambda value: value), [1])
        self.assertEqual(
            quick_sort([5, 3, 5, 1, 3], key=lambda value: value),
            [1, 3, 3, 5, 5],
        )

        # Arrange values so the middle pivot is repeatedly the smallest
        # remaining value. The former recursive implementation exceeded
        # Python's recursion limit on this valid 1,100-item input.
        count = 1100
        positions = list(range(count))
        adversarial = [None] * count
        for value in range(count):
            middle = len(positions) // 2
            adversarial[positions.pop(middle)] = value

        self.assertEqual(
            quick_sort(adversarial, key=lambda value: value),
            list(range(count)),
        )

    def test_insertion_sort_orders_score_then_smaller_id(self):
        def higher(first, second):
            if first["score"] != second["score"]:
                return first["score"] > second["score"]
            return first["id"] < second["id"]

        candidates = [
            {"id": "F003", "score": 60},
            {"id": "F002", "score": 90},
            {"id": "F001", "score": 90},
        ]
        ordered = insertion_sort(candidates, higher)
        self.assertEqual(
            [candidate["id"] for candidate in ordered],
            ["F001", "F002", "F003"],
        )

    def test_insertion_sort_handles_empty_and_large_inputs(self):
        def higher(first, second):
            return first > second

        self.assertEqual(insertion_sort([], higher), [])
        values = list(range(5001))
        self.assertEqual(
            insertion_sort(values, higher),
            list(range(5000, -1, -1)),
        )

    def test_insertion_sort_is_stable_and_linear_on_ordered_input(self):
        calls = []
        values = [
            {"score": score, "order": index}
            for index, score in enumerate([3, 3, 2, 1])
        ]

        def higher(a, b):
            calls.append(1)
            return a["score"] > b["score"]

        self.assertEqual(insertion_sort(values, higher), values)
        self.assertEqual(len(calls), len(values) - 1)
        shuffled = [values[2], values[0], values[3], values[1]]
        self.assertEqual(insertion_sort(shuffled, higher), values)

    def test_add_duplicate_validation_and_persistence(self):
        first = self.app.add(self.lost_payload())
        self.assertEqual(first["report_id"], "L001")
        with self.assertRaises(ValueError):
            self.app.add(dict(self.lost_payload(), report_id="L001"))

        reopened = PairBack(self.app.data_file, seed=False)
        self.assertEqual(reopened.find("L001")["item_name"], "Bottle")

    def test_dsws_intake_rules(self):
        invalid_lost = dict(
            self.lost_payload(),
            intake_channel="OADSA Turnover - Xavier Hall",
        )
        with self.assertRaises(ValueError):
            self.app.add(invalid_lost)

        invalid_found = dict(
            self.found_payload(),
            intake_channel="OADSA Turnover - Xavier Hall",
            custody_location="MVP 101",
        )
        with self.assertRaises(ValueError):
            self.app.add(invalid_found)

    def test_matching_uses_correct_date_weight_and_insertion_order(self):
        lost = self.app.add(self.lost_payload())
        first = self.app.add(self.found_payload())
        second = self.app.add(
            dict(
                self.found_payload(),
                brand="Other",
                location="Cafeteria",
                report_time="12:00",
            )
        )

        matches = self.app.matches(lost["report_id"])
        self.assertEqual(matches[0]["record"]["report_id"], first["report_id"])
        self.assertEqual(matches[0]["score"], 100)
        self.assertEqual(matches[1]["record"]["report_id"], second["report_id"])
        self.assertEqual(matches[1]["score"], 65)

    def test_release_requires_id_proof_and_mvp_101(self):
        found = self.app.add(self.found_payload())

        invalid_attempts = [
            (False, False, "MVP 101"),
            (True, True, "OADSA - Xavier Hall"),
        ]
        for valid_id, proof, location in invalid_attempts:
            with self.assertRaises(ValueError):
                self.app.release(
                    found["report_id"],
                    valid_id,
                    proof,
                    location,
                )

        self.app.release(found["report_id"], True, True, "MVP 101")
        self.assertEqual(
            self.app.find(found["report_id"])["status"],
            "released",
        )

    def test_released_item_is_excluded_and_undo_restores_it(self):
        for record in SAMPLE_RECORDS:
            normalized = self.app._normalize_record(dict(record))
            self.app.records.append(normalized)

        before = [
            item["record"]["report_id"]
            for item in self.app.matches("L001")
        ]
        self.assertIn("F001", before)

        self.app.release("F001", True, True, "MVP 101")
        after = [
            item["record"]["report_id"]
            for item in self.app.matches("L001")
        ]
        self.assertNotIn("F001", after)

        change = self.app.undo()
        self.assertEqual(change["previous"], "available")
        self.assertEqual(self.app.find("F001")["status"], "available")


if __name__ == "__main__":
    unittest.main(verbosity=2)
