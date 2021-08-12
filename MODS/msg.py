
#ARBITER msg module

from pclasses import dataclass,BaseCommand
from copy import copy


# command classes
@dataclass()
class c_register:
  name:object
  resp:list # [com resp com resp]
  def on_Parse(self,backend):
    parser = backend.getParser()
    self._presps = {}
    if self.resp:
      for c,r in zip(self.resp[::2],self.resp[1::2]):
        self._presps.update({c.lexeme:parser(r)})
    #print(self._presps)

  def on_Init(self,arb,proc):
    global CPID,PNS
    if not isinstance(self.name,str):
      proc.env.update({"pname":self.name.lexeme,"pid":CPID})
      CPID+=1
      PNS.update({proc.env.get("pname"):proc.env.get("pid")})
    else:
      proc.env.update({"pid":CPID})
      CPID+=1
    proc.releaseCurrent()
    pid = proc.env.get("pid")
    for c,r in self._presps.items():
      proc.registerEvent(f"MSG {pid} {c}",r)
      arb.env.update({f"MSG {pid} {c}":[]})

@dataclass()
class c_recieve(BaseCommand):
  command:object
  target:object
  def exec(self,arb,proc):
    pid = proc.env.get("pid")
    dat = arb.env.get(f"MSG {pid} {self.command.lexeme}").pop()
    proc.env.update({self.target.lexeme:dat})

@dataclass()
class c_unpack(BaseCommand):
  source:object
  targets:list
  def on_Parse(self,backend):
    self.targets = [i.lexeme for i in self.targets[:]]
  def exec(self,arb,proc):
  
    val = proc.env.get(self.source.lexeme)
    #print(*copy(val.message))
    targs = iter(self.targets)
    #print(*copy(targs))
    proc.env.update({next(targs):val.sender})
    proc.env.update(zip(targs,val.message))
    for i in targs: proc.env.update({i:0.0})
      
      
@dataclass()
class c_msg(BaseCommand):
  target:object
  command:object
  message:list

  def gtrg(self,proc):
    global PNS
    return PNS.get(self.target.lexeme,-1)
  def on_Parse(self,backend):
    if self.message == None: self.message = []
  def exec(self,arb,proc):
    sob = Event(proc.env.get("pid"),iter([*map(lambda x:x.Solve(proc.env),self.message)]))
    trg = self.gtrg(proc)
    #print(f"MSG {trg} {self.command.lexeme}")
    arb.invoke(f"MSG {trg} {self.command.lexeme}","*")
    arb.env.get(f"MSG {trg} {self.command.lexeme}",[]).append(sob)

class c_msg_var(c_msg):
  def gtrg(self,proc):
    global PNS
    tmp = self.target.Solve(proc.env)
    try:return int(tmp)
    except ValueError:PNS.get(tmp,-1)

class tst(BaseCommand):
    def exec(self,arb,proc):
      if proc.env.get("pid",None) == None:
        print ("erronious data",file=arb.aout)

# loading requirements

@dataclass()
class Event:
  sender:int
  message:iter

syntax = """
<namespace _>
msg:&&:data[*];
register:&-|:response[&£];
msgv:*&:data[*];
recieve:&&;
unpack:&[-&|];
test:; <bind test tst>
<bind msgv c_msg_var>
"""

modvars = {"Event":Event,
           "PNS":{},
           "CPID":0}

def module_init(backend):
  print("messaging module loaded",file=backend.bout)
  
