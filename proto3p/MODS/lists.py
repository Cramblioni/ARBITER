
#ARBITER list module
from pclasses import dataclass,BaseCommand,c_set,exprProxy



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
      proc.env.update({self.cr_name.wrd:[]})
    if self.gt_src:
      tmp = proc.env.get(self.gt_src.wrd)
      ind = int(self.gt_ind.Solve(proc.env))
      proc.env.update({self.gt_trg.wrd:tmp[ind]})
    if self.ap_trg:
      tmp = proc.env.get(self.ap_trg.wrd)
      tmp.append(self.ap_val.Solve(proc.env))

@dataclass()
class c_foreach(BaseCommand):
  target:object
  values:object
  body:list
  def on_Parse(self,backend):
    self.body = backend.getParser()(self.body)
  def exec(self,arb,proc):
    tmp = proc.env.get(self.values.wrd)
    # cheating with brute force
    for i in tmp[::-1]:
      proc.addprocedure([c_set(self.target,exprProxy(i))]+self.body)
      
#loading requirements
commands = {"c_list":c_list,
            "c_foreach":c_foreach}

syntax = """
list::create&:get&*&:append&*;
foreach:&^in&£;
"""

def module_init(backend):
  print("Lists enabled",file=backend.bout)
