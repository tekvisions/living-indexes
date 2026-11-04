import json
from pathlib import Path
import unittest
import shutil
import tempfile
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

    def test_public_projection_excludes_reviewed_identities_and_has_all_seventeen_sites(self):
        data=json.loads((ROOT/'catalog.json').read_text())
        self.assertEqual(len(data['indexes']),17)
        for row in data['indexes']:
            top=row.get('top')
            if top:
                from summary_policy import REVIEWED_REFERENCES
                self.assertNotIn(str(top.get('name','')).casefold(),REVIEWED_REFERENCES)
            if row['key']=='mcp':self.assertIn('coverage_note',row)
        self.assertIn('dated upstream summaries',data['meaning'])

    def test_valid_replacement_top_is_allowed_for_previously_reviewed_sites(self):
        from summary_policy import REVIEWED_REFERENCES
        for key in ('skill','voice','dataset'):
            for excluded in REVIEWED_REFERENCES:
                with self.subTest(key=key,excluded=excluded):
                    snapshot={'generated_at':'2026-11-04T08:00:00Z','items':[{'full_name':excluded.upper(),'momentum':99},{'full_name':'morluto/rea','momentum':87}]}
                    result=summarize(snapshot,{'key':key})
                    self.assertEqual(result['top'],{'name':'morluto/rea','momentum':87})
                    self.assertEqual(result['count'],1)
                    self.assertEqual(result['generated_at'],snapshot['generated_at'])
                    self.assertIn('review_note',result)
                    self.assertEqual(len(snapshot['items']),2)

    def test_all_excluded_has_no_top_and_retains_explanation(self):
        from summary_policy import REVIEWED_REFERENCES
        result=summarize({'generated_at':'2026-11-04','items':[{'full_name':n} for n in REVIEWED_REFERENCES]},{'key':'voice'})
        self.assertIsNone(result['top']);self.assertEqual(result['count'],0)
        self.assertIn('review_note',result)

    def test_unaffected_summary_is_not_marked_as_withheld(self):
        result=summarize({'generated_at':'2026-11-04','items':[{'full_name':'org/valid','momentum':0}]},{'key':'skill'})
        self.assertEqual(result['top'],{'name':'org/valid','momentum':0})
        self.assertNotIn('review_note',result)

    def test_public_render_accepts_valid_replacements_and_still_withholds_reviewed_identities(self):
        from render_home import render
        from summary_policy import REVIEWED_REFERENCES
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)/'hub'
            shutil.copytree(ROOT,root,ignore=shutil.ignore_patterns('.git','__pycache__'))
            data=json.loads((root/'data.json').read_text())
            data['generated_at']='2026-11-04T18:00:00Z'
            for row in data['indexes']:
                if row['key'] in ('skill','voice','dataset'):
                    row.update(top={'name':'morluto/rea','momentum':87},generated_at='2026-11-04T08:00:00Z')
            (root/'data.json').write_text(json.dumps(data))
            render(root)
            projected=json.loads((root/'catalog.json').read_text())
            self.assertEqual(len(projected['indexes']),17)
            for row in projected['indexes']:
                if row['key'] in ('skill','voice','dataset'):
                    self.assertEqual(row['top']['name'],'morluto/rea')
                    self.assertEqual(row['generated_at'],'2026-11-04T08:00:00Z')
            for row in data['indexes']:
                if row['key']=='skill':row['top']={'name':next(iter(REVIEWED_REFERENCES)).upper(),'momentum':99}
            (root/'data.json').write_text(json.dumps(data))
            render(root)
            skill=next(row for row in json.loads((root/'catalog.json').read_text())['indexes'] if row['key']=='skill')
            self.assertIsNone(skill['top']);self.assertIn('review_note',skill)

if __name__=='__main__':unittest.main()
