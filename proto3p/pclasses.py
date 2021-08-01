

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
  value:object
  def Solve(self,env):
    return self.value


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
      proc.env.update({self.target.wrd:tmp})
    else:
      proc.env.update({self.target.wrd:self.value.Solve(proc.env)})

@dataclass()
class c_get(BaseCommand):
  source:object
  target:object
  def exec(self,arb,proc):
    proc.env.update({self.target.wrd:arb.env.get(self.source.wrd)})

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
    self.orelse = parser(self.orelse)
  def exec(self,arb,proc):
    if self.test.Solve(proc.env) > 0:
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
  scope:chr
  def exec(self,arb,proc):
    if self.scope == "_":
      proc.invoke(self.name.wrd)
    else:
      arb.invoke(self.name.wrd,self.scope)

@dataclass()
class c_await(BaseCommand):
  event:object
  def exec(self,arb,proc):
    try:proc.currentawait(self.event.wrd)
    except AttributeError:
      proc.currentawait(self.event)

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
    proc.registerEvent(self.name.wrd,self.body)

@dataclass()
class c_end(BaseCommand):
  def exec(self,arb,proc):
    proc.kill()

@dataclass()
class c_ext(BaseCommand):
  set_target:object
  set_value:object
  def exec(self,arb,proc):
    arb.env.update({self.set_target.wrd:self.set_value.Solve(proc.env)})
  
# Arbiter based commands
@dataclass()
class c_ref(BaseCommand):
  name:object
  body:list
  source:object
  def on_Parse(self,backend):
    if self.source: backend.setParserSet(self.source.wrd)
    backend.setParserMode(1)
    self.body = backend.getParser()(self.body)
    backend.setParserMode(0)
    if self.source:backend.unsetParserSet()
  def on_Init(self,arb,proc):
    arb.registerReference(self.name.wrd,self.body)
    arb.releaseCurrent()

@dataclass()
class c_union(BaseCommand):
  source:object
  alias:object
  # very basic union function [PATH = ./]
  def on_Parse(self,backend):
    if self.alias: ret = self.alias.wrd
    else: ret = self.source.wrd
    backend.getnloadModule(self.source.wrd,ret)
  def on_Init(self,arb,proc): # expecting arb == proc
    proc.releaseCurrent()
@dataclass()
class c_unionise(BaseCommand):
  m_a:object
  m_b:object
  m_n:object
  def on_Parse(self,backend):
    tmp = backend.extra.get(self.m_a.wrd)
    tmp += backend.extra.get(self.m_b.wrd)
    backend.registerSet(self.m_n.wrd,tmp)
  def on_init(self,arb,proc):
    proc.releaseCurrent()
@dataclass()
class c_create(BaseCommand):
  source:object
  pinput:list

  def exec(self,arb,proc):
    iev = {}
    if self.pinput:
      for n,v in zip(self.pinput[::2],self.pinput[1::2]):
        iev.update({n.wrd:v.Solve(proc.env)})
    arb.createProcess(self.source.wrd,iev)

@dataclass()
class c_see(BaseCommand):
  path:list
  def on_Parse(self,backend):
    backend.PATH.extend(map(lambda x:x.Solve({}),self.path))
  def on_Init(self,arb,proc):
    proc.releaseCurrent()
# ARBITER module requirements

syntax = """
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
"""

syntax_a = """
  ref:&£:using&;
  create:&:with[&~=*];
  union:&:as&;
  unionise:&&^as&;
  see:[*];
"""

# lookup table with keys following ARBITER command class naming convention
# and the respective command classes
commands = {"c_set":c_set,
            "c_ext":c_ext,
            "c_get":c_get,
            "c_print":c_print,
            "c_if":c_if,
            "c_while":c_while,
            "c_invoke":c_invoke,
            "c_await":c_await,
            "c_single":c_single,
            "c_event":c_event,
            "c_end":c_end,
            "c_ref":c_ref,
            "c_create":c_create,
            "c_union":c_union,
            "c_unionise":c_unionise,
            "c_see":c_see}

modvars = {"BaseCommand":BaseCommand,
           "exprProxy":exprProxy,
           "dataclass":dataclass}

def module_init(backend):
  print("Base Module Loaded",file=backend.bout)
