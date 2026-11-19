import io
import tempfile
import unittest
from pathlib import Path
from pairback import PairBack
from intake import parse_csv, commit_batch

class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = PairBack(Path(self.tmp.name) / 'data.json', seed=False)
        self.row = dict(item_name='Bottle',category='Bottle',color='Blue',location='Library',report_date='2026-11-19',report_time='14:30')
    def tearDown(self):
        self.tmp.cleanup()
    def test_duplicate_reimport_and_reload(self):
        self.assertEqual(commit_batch(self.store,[self.row,self.row]),(1,1))
        loaded=PairBack(self.store.data_file,seed=False)
        self.assertEqual(commit_batch(loaded,[self.row]),(0,1))
    def test_invalid_batch_is_atomic(self):
        with self.assertRaises(ValueError):
            commit_batch(self.store,[self.row,dict(self.row,report_date='bad')])
        self.assertEqual(self.store.all_records(),[])
        self.assertFalse(self.store.data_file.exists())
    def test_bad_csv(self):
        with self.assertRaises(ValueError): parse_csv('name,date\nbottle,today')
    def test_preview_commit_and_expiry(self):
        import app as module
        old=module.store
        module.store=self.store
        try:
            client=module.app.test_client()
            for route in ['/', '/intake','/dsws','/reports/new?channel=email','/records','/matching','/search']:
                self.assertEqual(client.get(route).status_code,200)
            csv='item_name,category,color,location,report_date,report_time\nBottle,Bottle,Blue,Library,2026-11-19,14:30\n'
            response=client.post('/intake',data={'file':(io.BytesIO(csv.encode()),'test.csv')})
            self.assertIn(b'Review before importing',response.data)
            self.assertEqual(len(self.store.all_records()),0)
            with client.session_transaction() as session: token=session['import_token']
            self.assertEqual(client.post('/intake',data={'action':'commit','token':token}).status_code,302)
            self.assertEqual(len(self.store.all_records()),1)
            self.assertIn(b'Preview expired',client.post('/intake',data={'action':'commit','token':token}).data)
        finally: module.store=old

if __name__=='__main__': unittest.main()
