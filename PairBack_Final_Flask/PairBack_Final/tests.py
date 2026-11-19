import tempfile, unittest
from pathlib import Path
from pairback import PairBack, SAMPLE_RECORDS
from data_structures import ArrayList, UndoStack, merge_sort, binary_search

class PairBackTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.app=PairBack(Path(self.temp.name)/"records.json",seed=False)
    def tearDown(self): self.temp.cleanup()

    def test_arraylist_growth_and_bounds(self):
        a=ArrayList()
        for i in range(1000): a.append(i)
        self.assertEqual(list(a),list(range(1000)))
        self.assertGreaterEqual(a.capacity,1000)
        with self.assertRaises(IndexError): _=a[-1]

    def test_stack_lifo(self):
        s=UndoStack()
        for i in range(10): s.push(i)
        self.assertEqual(s.peek(),9)
        self.assertEqual([s.pop() for _ in range(10)],list(reversed(range(10))))
        self.assertTrue(s.isEmpty())

    def test_merge_sort_and_binary_search(self):
        data=[{"report_id":x} for x in ["F3","F1","F2"]]
        ordered=merge_sort(data,key=lambda r:r["report_id"])
        self.assertEqual([r["report_id"] for r in ordered],["F1","F2","F3"])
        self.assertEqual(binary_search(ordered,"F2")["report_id"],"F2")
        self.assertIsNone(binary_search(ordered,"X"))

    def test_add_duplicate_validation_and_persistence(self):
        data={"report_type":"Lost","item_name":"Bottle","category":"Bottle","color":"Blue","location":"Library","report_date":"2026-11-19"}
        first=self.app.add(data)
        self.assertEqual(first["report_id"],"L001")
        with self.assertRaises(ValueError): self.app.add(dict(data,report_id="L001"))
        reopened=PairBack(self.app.data_file,seed=False)
        self.assertEqual(reopened.find("L001")["item_name"],"Bottle")

    def test_matching_weights_ties_and_released_exclusion(self):
        for r in SAMPLE_RECORDS: self.app.records.append(dict(r))
        self.app._save()
        matches=self.app.matches("L001")
        self.assertEqual(matches[0]["record"]["report_id"],"F001")
        self.assertEqual(matches[0]["score"],90)
        self.app.set_status("F001","released")
        self.assertNotIn("F001",[m["record"]["report_id"] for m in self.app.matches("L001")])

    def test_undo_restores_previous_status(self):
        for r in SAMPLE_RECORDS: self.app.records.append(dict(r))
        self.app.set_status("F001","released")
        change=self.app.undo()
        self.assertEqual(change["previous"],"available")
        self.assertEqual(self.app.find("F001")["status"],"available")
        self.assertIsNone(self.app.undo())

if __name__=="__main__": unittest.main(verbosity=2)
