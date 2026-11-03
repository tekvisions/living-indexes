import json
from pathlib import Path
import unittest
from summary_policy import curate,summarize
ROOT=Path(__file__).resolve().parents[1]

class SummaryPolicyTests(unittest.TestCase):
    def test_reviewed_references_are_not_promoted_and_source_date_is_preserved(self):
        source={'key':'voice','generated_at':'2026-11-01','count':285,'top':{'name':'harry0703/MoneyPrinterTurbo'}}
        result=curate(source)
        self.assertIsNone(result['top']);self.assertIn('unranked',result['review_note'])
        self.assertEqual(result['generated_at'],'2026-11-01');self.assertEqual(result['count'],285)
        self.assertIsNotNone(source['top'])

    def test_tracker_count_uses_actual_rows_and_preserves_zero_score(self):
        result=summarize({'generated_at':'2026-11-02','repos':[{'repo':'org/tool','momentum':0}]},{'key':'stack'})
        self.assertEqual(result['count'],1);self.assertEqual(result['top']['momentum'],0)

    def test_model_and_mcp_have_distinct_honest_scope(self):
        self.assertIn('trending',curate({'key':'model'})['blurb'])
        mcp=curate({'key':'mcp','blurb':'Every server'})
        self.assertNotIn('Every',mcp['blurb']);self.assertIn('not proof',mcp['coverage_note'])

    def test_reviewed_public_projection_keeps_notes_and_has_all_seventeen_sites(self):
        data=json.loads((ROOT/'catalog.json').read_text())
        self.assertEqual(len(data['indexes']),17)
        for row in data['indexes']:
            if row['key'] in ('skill','voice','dataset'):self.assertIsNone(row['top']);self.assertIn('review_note',row)
            if row['key']=='mcp':self.assertIn('coverage_note',row)
        self.assertIn('dated upstream summaries',data['meaning'])

if __name__=='__main__':unittest.main()
