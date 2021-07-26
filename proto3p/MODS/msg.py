
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
        self._presps.update({c.wrd:parser(r)})
    #print(self._presps)

  def on_Init(self,arb,proc):
    global CPID,PNS
    if not isinstance(self.name,str):
      proc.env.update({"pname":self.name.wrd,"pid":CPID})
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
    dat = arb.env.get(f"MSG {pid} {self.command.wrd}").pop()
    proc.env.update({self.target.wrd:dat})

@dataclass()
class c_unpack(BaseCommand):
  source:object
  targets:list
  def exec(self,arb,proc):
    global UPD
    val = proc.env.get(self.source.wrd)
    #print(*copy(val.message))
    targs = map(lambda x:x if isinstance(x,str) else x.wrd,self.targets)
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
    return PNS.get(self.target.wrd,-1)
  def on_Parse(self,backend):
    if self.message == None: self.message = []
  def exec(self,arb,proc):
    sob = Event(proc.env.get("pid"),iter([*map(lambda x:x.Solve(proc.env),self.message)]))
    trg = self.gtrg(proc)
    #print(f"MSG {trg} {self.command.wrd}")
    arb.invoke(f"MSG {trg} {self.command.wrd}","*")
    arb.env.get(f"MSG {trg} {self.command.wrd}").append(sob)

class c_msg_var(c_msg):
  def gtrg(self,proc):
    tmp = self.target.Solve(proc.env)
    try:return int(tmp)
    except ValueError:PNS.get(tmp,-1)
# loading requirements
@dataclass()
class Event:
  sender:int
  message:iter

syntax = """
msg:&&:data[*];
register:&-|:response[&£];
msgv:*&:data[*];
recieve:&&;
unpack:&[&'-_|];
"""

commands = {"c_msg":c_msg,
            "c_msgv":c_msg_var,
            "c_register":c_register,
            "c_recieve":c_recieve,
            "c_unpack":c_unpack}

modvars = {"Event":Event,
           "PNS":{},
           "CPID":0}

def module_init(backend):
  iparser = backend.getIParser()
  print("messaging module loaded",file=backend.bout)
  
