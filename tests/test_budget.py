import unittest, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from budget import evaluate
class Tests(unittest.TestCase):
    def plan(self,price,cap=10,r=1): return {'unit':'USD','cap':cap,'steps':[{'id':'a','quantity':2,'retry_quantity':r,'price':price}]}
    def test_ok(self): self.assertEqual(evaluate(self.plan('2.50'))['total_known'],'7.50')
    def test_block(self): self.assertEqual(evaluate(self.plan(4))['status'],'BLOCK')
    def test_unknown(self): self.assertEqual(evaluate(self.plan(None))['status'],'UNKNOWN')
    def test_mixed(self):
        p=self.plan(2); p['steps'][0]['unit']='credits'
        with self.assertRaises(ValueError): evaluate(p)
    def test_negative(self):
        with self.assertRaises(ValueError): evaluate(self.plan(-1))
    def test_cap(self): self.assertEqual(evaluate(self.plan(2,6))['status'],'WITHIN_CAP')
    def test_duplicate(self):
        p=self.plan(2); p['steps']*=2
        with self.assertRaises(ValueError): evaluate(p)
if __name__=='__main__': unittest.main()
