
#ARBITER list module
from pclasses import dataclass,BaseCommand,exprProxy



# command classes
@dataclass()
class c_list(BaseCommand):
  cr_name:object
  gt_src:object
  gt_ind:object
  gt_trg:object
  ap_trg:object
  ap_val:object
  def exec(self,arb,proc):
    if self.cr_name:
      proc.env.update({self.cr_name.lexeme:[]})
    if self.gt_src:
      tmp = proc.env.get(self.gt_src.lexeme)
      ind = int(self.gt_ind.Solve(proc.env))
      proc.env.update({self.gt_trg.lexeme:tmp[ind]})
    if self.ap_trg:
      tmp = proc.env.get(self.ap_trg.lexeme)
      tmp.append(self.ap_val.Solve(proc.env))

@dataclass()
class c_foreach(BaseCommand):
  target:object
  values:object
  body:list
  def on_Parse(self,backend):
    self.body = backend.getParser()(self.body)
    self.pbind = backend.getBinding("set")
  def exec(self,arb,proc):
    tmp = proc.env.get(self.values.lexeme)
    # cheating with brute force
    for i in tmp[::-1]:
      proc.addprocedure([self.pbind(self.target,exprProxy(i))]+self.body)
      


syntax = """
<namespace _ >
list::create&:get&*&:append&*;
foreach:&^in&£;
"""

def module_init(backend):
  print("Lists enabled",file=backend.bout)
