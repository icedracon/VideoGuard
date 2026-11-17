import unittest,sys,json
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import guard as g
import higgsfield_quote as h
class GuardTests(unittest.TestCase):
    def test_first_question(self): self.assertEqual(g.interview({})['next']['id'],'kind')
    def test_image_no_duration(self): self.assertNotIn('duration',g.interview({'kind':'image'})['remaining'])
    def test_reference_branch(self): self.assertIn('reference',g.interview({'kind':'video','mode':'image-to-video'})['remaining'])
    def test_answer_not_repeated(self): self.assertNotIn('kind',g.interview({'kind':'video'})['remaining'])
    def test_empty_prompt(self): self.assertEqual(g.lint({})[0]['level'],'BLOCK')
    def test_conflict(self): self.assertIn('CONFLICT',[x['code'] for x in g.lint({'prompt':'static camera 360 orbit'})])
    def test_overload(self): self.assertIn('OVERLOAD',[x['code'] for x in g.lint({'prompt':'x','kind':'video','duration':5,'actions':['a','b','c']})])
    def test_lock(self): self.assertIn('LOCK_CONFLICT',[x['code'] for x in g.lint({'prompt':'x','preserve':['Logo'],'change':['logo']})])
    def test_unknown_model(self): self.assertTrue(g.capabilities({'model':'unknown'}))
    def test_cap_limit(self): self.assertEqual(g.capabilities({'model':'x','duration':7,'verified_capabilities':{'source':'example','checked_at':'2026-11-17','durations':[5]}})[0]['level'],'BLOCK')
    def test_cap_unverified(self): self.assertIn('CAP_SOURCE',[x['code'] for x in g.capabilities({'model':'x','verified_capabilities':{'durations':[5]}})])
    def test_handoff_crop(self): self.assertIn('CROP',[x['code'] for x in g.handoff({'mode':'image-to-video','aspect':'9:16','reference':{'width':1920,'height':1080}})])
    def test_handoff_unknown(self): self.assertEqual(g.handoff({'mode':'image-to-video'})[0]['level'],'UNKNOWN')
    def test_handoff_pass(self): self.assertEqual(g.handoff({'mode':'image-to-video','aspect':'9:16','reference':{'width':900,'height':1600,'inspected':True,'approved':True}}),[])
    def test_handoff_unseen(self): self.assertIn('UNSEEN',[x['code'] for x in g.handoff({'mode':'image-to-video','reference':{},'reveal_unseen':True,'preserve':['geometry']})])
    def test_compile(self): self.assertIn('HELLO',[g.compile_image({'exact_text':'HELLO'})['prompt'].split(': ')[1]])
    def test_compile_preserves(self): self.assertIn('logo',g.compile_image({'preserve':['logo']})['prompt'])
    def test_tokens(self): self.assertEqual(g.token_plan({'cap':10,'blocks':[{'id':'must','tokens':8,'required':True},{'id':'opt','tokens':4}]})['skip'],['opt'])
    def test_tokens_block(self): self.assertEqual(g.token_plan({'cap':5,'blocks':[{'id':'must','tokens':8,'required':True}]})['status'],'BLOCK')
    def test_tokens_reserve(self): self.assertEqual(g.token_plan({'cap':5,'output_reserve':6})['status'],'BLOCK')
    def test_debug(self):
        r=g.debug({'stages':[{'id':'a','status':'FAIL'},{'id':'b','status':'FAIL','depends_on':['a']},{'id':'c','status':'PASS'}]});self.assertEqual(r['candidate_roots'],['a']);self.assertEqual(r['revalidate'],['a','b']);self.assertEqual(r['preserve'],['c'])
    def test_cycle(self):
        with self.assertRaises(ValueError):g.debug({'stages':[{'id':'a','depends_on':['a']}]})
    def test_missing_dep(self):
        with self.assertRaises(ValueError):g.debug({'stages':[{'id':'a','depends_on':['b']}]})
    def test_quote_preview(self): self.assertEqual(h.command({'model':'seedance_2_5','params':{'duration':5}}),['higgsfield','generate','cost','seedance_2_5','--duration','5'])
    def test_quote_bad_model(self):
        with self.assertRaises(ValueError):h.command({'model':'--help','params':{}})
    def test_quote_bad_flag(self):
        with self.assertRaises(ValueError):h.command({'model':'abc','params':{'execute':True}})
    def test_preflight_unknown_cost(self):
        b=json.loads((Path(__file__).parent/'example-brief.json').read_text());r=g.preflight(b);self.assertEqual(r['verdict'],'REVIEW');self.assertFalse(r['authorization']);self.assertEqual(r['budget']['status'],'UNKNOWN')
    def test_preflight_overcap(self):
        b=json.loads((Path(__file__).parent/'example-brief.json').read_text());b['cost_plan']['steps'][0]['price']=80;self.assertEqual(g.preflight(b)['verdict'],'BLOCK')
    def test_preflight_ready(self):
        b=json.loads((Path(__file__).parent/'example-brief.json').read_text());b['cost_plan']['steps'][0]['price']=20;b['verified_capabilities']={'source':'test fixture','checked_at':'2026-11-17','modes':['image-to-video'],'aspects':['9:16'],'durations':[5]};self.assertEqual(g.preflight(b)['verdict'],'READY_FOR_REVIEW')
if __name__=='__main__': unittest.main()
