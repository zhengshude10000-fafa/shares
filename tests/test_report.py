import os,sys,unittest
sys.path.insert(0,os.path.join(os.path.dirname(__file__),"..","src"))
from report import build
class ReportTest(unittest.TestCase):
 def setUp(self):
  self.data={"generated_at":"2026-07-14T15:40:00+08:00","quality":{"ok":2,"total":2},"indices":[{"name":"上证指数","ok":True,"change_pct":1.2}],"watchlist":[{"code":"000636","name":"风华高科","industry":"电子元件","ok":True,"price":70,"change_pct":3.1}]}
 def test_pre(self): self.assertEqual(build("pre-market",self.data)["type"],"pre-market")
 def test_after(self): self.assertTrue(build("after-market",self.data)["next_actions"])
if __name__=="__main__":unittest.main()
