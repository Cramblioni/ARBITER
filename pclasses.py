

from dataclasses import dataclass
## This contains the classes the parser will use
class BaseCommand:
  def on_Parse(self,backend): # called during parsing stage
    ...
  def on_Init(self,arb,proc): # called when loaded into an executor
    ...
  def exec(self,arb,proc): # called when the executor(Arbiter or process) gets to the command
    ...

@dataclass()
class exprProxy:
  """A Proxy class for injecting specific values into a statement"""
  value:object
  def Solve(self,env):
    return self.value

def prepInvoke(proc,event,scope="_"):
  "generates a function that invokes an event [shallow]"
  if isinstance(proc,Arbiter):
    return lambda *x: proc.invoke(event,scope)
  else:
    return lambda *x: proc.invoke(event)

# Base ARBITER command classes

@dataclass()
class c_set(BaseCommand):
  target:object
  value:object
  ll:object = None
  ul:object = None
  def exec(self,arb,proc):
    if self.ll and self.ul:
      tmp = self.value.Solve(proc.env)
      ll = self.ll.Solve(proc.env)
      ul = self.ul.Solve(proc.env)
      if tmp < ll: tmp = ll
      elif tmp > ul: tmp = ul
      proc.env.update({self.target.lexeme:tmp})
    else:
      proc.env.update({self.target.lexeme:self.value.Solve(proc.env)})

@dataclass()
class c_get(BaseCommand):
  source:object
  target:object
  def exec(self,arb,proc):
    proc.env.update({self.target.lexeme:arb.env.get(self.source.lexeme)})

@dataclass()
class c_print(BaseCommand):
  args:list
  def exec(self,arb,proc):
    print(*[i.Solve(proc.env) for i in self.args],file=arb.aout)

@dataclass()
class c_if(BaseCommand):
  test:object
  body:list
  orelse:list = None
  def on_Parse(self,backend):
    parser = backend.getParser()
    self.body = parser(self.body)
    self.orelse = parser(self.orelse if self.orelse else [])
  def exec(self,arb,proc):
    tmp = self.test.Solve(proc.env)
    if tmp and tmp > 0:
      proc.addprocedure(self.body)
    else:
      proc.addprocedure(self.orelse)

@dataclass()
class c_while(BaseCommand):
  test:object
  body:list
  def on_Parse(self,backend):
    parser = backend.getParser()
    self.body = parser(self.body)
  def exec(self,arb,proc):
    cond = lambda : self.test.Solve(proc.env)
    proc.addprocedure(self.body,cond)

@dataclass()
class c_invoke(BaseCommand):
  name:object
  scope:object
  def exec(self,arb,proc):
    if self.scope.lexeme == "_":
      proc.invoke(self.name.lexeme)
    else:
      arb.invoke(self.name.lexeme,self.scope)

@dataclass()
class c_await(BaseCommand):
  event:object
  def exec(self,arb,proc):
    proc.currentawait(self.event.lexeme)

@dataclass()
class c_single(BaseCommand):
  body:list
  def on_Parse(self,backend):
    self.body = backend.getParser()(self.body)
  def exec(self,arb,proc):
    nProcInd = proc.newprocedure(self.body)
    proc.flush(nProcInd)

@dataclass()
class c_event(BaseCommand):
  name:object
  body:list
  def on_Parse(self,backend):
    self.body = backend.getParser()(self.body)
  def on_Init(self,arb,proc):
    proc.releaseCurrent()
    proc.registerEvent(self.name.lexeme,self.body)

@dataclass()
class c_end(BaseCommand):
  def exec(self,arb,proc):
    proc.kill()

@dataclass()
class c_ext(BaseCommand):
  set_target:object
  set_value:object
  def exec(self,arb,proc):
    arb.env.update({self.set_target.lexeme:self.set_value.Solve(proc.env)})
  
# Arbiter based commands
@dataclass()
class c_ref(BaseCommand):
  name:object
  body:list
  source:object
  def on_Parse(self,backend):
    if self.source: backend.setParserSet(*[i.lexeme for i in self.source])
    backend.setParserMode(1)
    self.body = backend.getParser()(self.body)
    backend.setParserMode(0)
    if self.source:backend.unsetParserSet()
  def on_Init(self,arb,proc):
    arb.registerReference(self.name.lexeme,self.body)
    arb.releaseCurrent()

@dataclass()
class c_union(BaseCommand):
  source:object
  alias:object
  # very basic union function [PATH = ./]
  def on_Parse(self,backend):
    if self.alias: ret = self.alias.lexeme
    else: ret = self.source.lexeme
    backend.getnloadModule(self.source.lexeme,ret)
  def on_Init(self,arb,proc): # expecting arb == proc
    proc.releaseCurrent()



@dataclass()
class c_create(BaseCommand):
  source:object
  pinput:list

  def exec(self,arb,proc):
    iev = {}
    if self.pinput:
      for n,v in zip(self.pinput[::2],self.pinput[1::2]):
        iev.update({n.lexeme:v.Solve(proc.env)})
    arb.createProcess(self.source.lexeme,iev)

@dataclass()
class c_see(BaseCommand):
  path:list
  def on_Parse(self,backend):
    backend.PATH.extend(map(lambda x:x.Solve({}),self.path))
  def on_Init(self,arb,proc):
    proc.releaseCurrent()

@dataclass()
class env_test(BaseCommand):
  cntxs:list
  body:list
  def on_Parse(self,backend):
    cntxs = [i.lexeme for i in self.cntxs]
    backend.setParserSet(*cntxs)
    self.body = backend.getParser()(self.body)
    backend.unsetParserSet()
  def on_Init(self,arb,proc):
    proc.replaceCurrent(self.body)

@dataclass()
class c_env_watchdog(BaseCommand):
  trigger:object
  response:list
  then:list
  def _tst(self,arb):
    env = {"procn":len(arb._procs),
           "running":float(arb._exec),
           **arb.env}
    return self.trigger.Solve(env)
    
  def _func_d(self,arb):
    if self._tst(arb):
      tmp = arb.newprocedure(self.response)
      arb.flush(tmp)
      arb.releaseDutyFunc()
  def _func_c(self,arb):
    if self._tst(arb):
      tmp = arb.newprocedure(self.response)
      arb.flush(tmp)
      arb.newprocedure(self.then)
  def _func_dc(self,arb):
    if self._tst(arb):
      tmp = arb.newprocedure(self.response)
      arb.flush(tmp)
      arb.releaseDutyFunc()
      arb.newprocedure(self.then)
  def _func(self,arb):
    if self._tst(arb):
      tmp = arb.newprocedure(self.response)
      arb.flush(tmp)
      
  def on_Parse(self,backend):
    self._prev = 0
    parser = backend.getParser()
    self.response = parser(self.response)
    if isinstance(self.then,list):
      self.then = parser(self.then)
    elif self.then == None:pass
    elif self.then.lexeme == "release":
      self._destroy = True
      self.then = None
    else: self.then = None
  
  def on_Init(self,arb,proc):
    proc.releaseCurrent()
    if self._destroy:
      if self.then:
        arb.registerDutyFunc(self._func_dc)
      else:
        arb.registerDutyFunc(self._func_d)
    else:
      if self.then:
        arb.registerDutyFunc(self._func_c)
      else:
        arb.registerDutyFunc(self._func)
    
# ARBITER module requirements

syntax = """
<namespace __ ><bind using env_test>
  set:&*:limit**;
  ext::set&*;
  get:&&;
  print:[*];
  if:*£:else£;
  while:*£;
  invoke:&'-*;
  await:&'-*|;
  single:£;
  event:&£;
  end:;
  using:[&]£; 
<namespace __ ARBITER>
  ref:&£:using[&];
  create:&:with[&~=*];
  union:&:as&;
  see:[*];
  watchdog:*£:then&£|;<bind watchdog c_env_watchdog>
"""


modvars = {"BaseCommand":BaseCommand,
           "exprProxy":exprProxy,
           "dataclass":dataclass,
           "prepInvoke":prepInvoke}

def module_init(backend):
  print("Base Module Loaded",file=backend.bout)
