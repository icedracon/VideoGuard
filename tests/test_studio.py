import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import studio as s
class StudioTests(unittest.TestCase):
    def project(self):
        return {'duration':5,'identities':[{'id':'p','version':'1','locked':{'coat':'red'},'reference_id':'r','approved':True}],'shots':[{'id':'s','duration':5,'purpose':'ad','subject':'person','action':'walk','camera':'static','lighting':'day','opening':'a','ending':'b','prompt':'Person walks.','cast':{'p':{'version':'1','attributes':{'coat':'red'}}}}]}
    def test_story(self): self.assertEqual(s.storyboard(self.project())['verdict'],'READY_FOR_REVIEW')
    def test_drift(self):
        p=self.project();p['shots'][0]['cast']['p']['attributes']['coat']='blue';self.assertEqual(s.storyboard(p)['verdict'],'BLOCK')
    def test_stale(self):
        p=self.project();p['shots'][0]['cast']['p']['version']='0';self.assertEqual(s.storyboard(p)['verdict'],'BLOCK')
    def test_duration(self):
        p=self.project();p['duration']=10;self.assertEqual(s.storyboard(p)['verdict'],'BLOCK')
    def test_unknown_attr(self):
        p=self.project();p['shots'][0]['cast']['p']['attributes']={};self.assertEqual(s.storyboard(p)['verdict'],'REVIEW')
    def test_no_evidence(self): self.assertEqual(s.quality({'phase':'output','observations':{'identity':{'status':'PASS'}}})['checks'][0]['status'],'UNKNOWN')
    def test_qa_fail(self): self.assertEqual(s.quality({'phase':'output','observations':{'identity':{'status':'FAIL','evidence':'changed face'}}})['verdict'],'BLOCK')
    def test_qa_ready(self): self.assertEqual(s.quality({'phase':'brief','observations':{k:{'status':'PASS','evidence':'review record'} for k in s.QA['brief']}})['verdict'],'READY_FOR_REVIEW')
    def test_route(self):
        p={'cap':10,'unit':'credits','options':[{'id':'a','price':3,'unit':'credits','attempts':1,'retries':1,'capability_status':'PASS','capability_source':'fixture','quote_source':'fixture'},{'id':'b','price':1,'unit':'credits'}]};self.assertEqual(s.route(p)['recommended'],'a')
    def test_route_unknown(self): self.assertIsNone(s.route({'cap':2,'unit':'credits','options':[{'id':'a','unit':'credits'}]})['recommended'])
    def plan(self):
        p={'cap':10,'unit':'credits','stages':[{'id':'s','inputs':{'prompt':'hi'}}],'attempts':[{'id':'a','stage':'s','unit':'credits','status':'RESERVED','quote':4,'quote_source':'fixture'}]}
        p['attempts'][0]['approval']={'confirmed':True,'fingerprint':s.fingerprint(s.approval_payload(p['stages'][0],p['attempts'][0]))};return p
    def test_ledger(self): self.assertEqual(s.ledger(self.plan())['verdict'],'WITHIN_RECORDED_CAP')
    def test_ledger_stale(self):
        p=self.plan();p['stages'][0]['inputs']['prompt']='changed';self.assertEqual(s.ledger(p)['verdict'],'BLOCK')
    def test_ledger_changed_quote(self):
        p=self.plan();p['attempts'][0]['quote']=5;self.assertEqual(s.ledger(p)['verdict'],'BLOCK')
    def test_ledger_overcap(self):
        p=self.plan();p['cap']=2;self.assertEqual(s.ledger(p)['verdict'],'BLOCK')
    def test_ledger_unknown(self):
        p=self.plan();p['attempts'][0]['quote']=None;p['attempts'][0]['approval']['fingerprint']=s.fingerprint(s.approval_payload(p['stages'][0],p['attempts'][0]));self.assertEqual(s.ledger(p)['verdict'],'REVIEW')
    def test_ledger_spent(self):
        p=self.plan();p['attempts'].append({'id':'b','stage':'s','unit':'credits','status':'BILLED','actual':8});self.assertEqual(s.ledger(p)['verdict'],'BLOCK')
    def test_dep(self):
        p=self.plan();p['stages'].append({'id':'d','status':'PASS','version':'2'});p['stages'][0]['depends_on']=['d'];p['stages'][0]['dependency_versions']={'d':'1'};self.assertEqual(s.ledger(p)['verdict'],'BLOCK')
    def test_compare(self):
        base={'unit':'credits','cost':10,'attempts':2,'accepted':True,'first_attempt_accepted':False}; guard={**base,'cost':4,'attempts':1,'first_attempt_accepted':True};r=s.compare({'unit':'credits','pairs':[{'id':'p','settings_fingerprint':'fixture','baseline':base,'guard':guard}]});self.assertEqual(r['results']['guard']['cost_per_accepted'],'4')
    def test_compare_unaccepted(self):
        a={'unit':'credits','cost':10,'attempts':1,'accepted':False,'first_attempt_accepted':False};self.assertIsNone(s.compare({'unit':'credits','pairs':[{'id':'p','settings_fingerprint':'x','baseline':a,'guard':a}]})['results']['guard']['cost_per_accepted'])
    def test_duplicate(self):
        p=self.project();p['shots']*=2
        with self.assertRaises(ValueError):s.storyboard(p)
if __name__=='__main__':unittest.main()
