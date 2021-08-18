
# tkinter interface for ARBITER
from pclasses import BaseCommand,exprProxy,dataclass,prepInvoke
import tkinter as tk

# classes
class managedWindow:
  def __init__(self):
    self.root = tk.Tk()
    self._senv = {}
  def __getitem__(self,key):
    return self._senv[key]
  def __setitem__(self,key,value):
    self._senv.update({key:value})

# duty functions for the two modes
def tk_single(arb):
  tmp = arb.env.get("_tk_data") 
  try:
    tmp.root.update()
    tmp.root.update_idletasks()
  except tk.TclError:
    arb.invoke("WindowClosed")
    arb.releaseDutyFunc()
  
def tk_multi(arb):
  tmp = arb.env.get("_tk_data")
  for i in tmp[:]:
    try:
      i.root.update()
      i.root.update_idletasks()
    except tk.TclError:
      i.procref.invoke("WindowClosed")
      tmp.remove(i)
# normal module stuff

@dataclass()
class c_tk_init(BaseCommand):
  mode:object
  def on_Parse(self,backend): 
    self.mode = self.mode.lexeme
  def on_Init(self,arb,proc):
    im=arb.env["_tk_mode"] = self.mode == "multi"
    arb.env["_tk_data"] = [] if im else managedWindow()
    proc.releaseCurrent()
    arb.registerDutyFunc(tk_multi if im else tk_single)

@dataclass()
class c_tk_element(BaseCommand):
  name:object
  type:object
  setup:list
  def on_Parse(self,backend):
    backend.setParserSet("_element")
    parser = backend.getParser()
    self.setup = parser(self.setup)
    backend.unsetParserSet()
  
  def exec(self,arb,proc):
    root = proc.env.get(" window",arb.env.get("_tk_data"))
    if isinstance(root,list):
      tmp = root
      proc.env[" window"]=root = managedWindow()
      root.procref = proc
      tmp.append(root)
    elem = eval(f"tk.{self.type.lexeme}")(root.root)
    if self.name.lexeme != "_":
      root[self.name.lexeme] = elem
    proc.env.update({" prevele":elem})
    proc.addprocedure(self.setup)

@dataclass()
class c_tk_call(BaseCommand):
  target:object
  command:object
  args:list
  kwargs:list
  dest:object
  def on_Parse(self,backend):
    self.target = self.target.lexeme
    if self.kwargs:
      self.kwargs = zip(map(lambda x: x.lexeme,self.kwargs[::2]),self.kwargs[1::2])
    else:
      self.kwargs = {}
    if self.args:pass
    else:self.args = []
  def exec(self,arb,proc):
    ref = proc.env.get(" window",arb.env.get("_tk_data"))
    self.kwargs.update(zip(self.kwargs.keys(),
                       map(lambda x: x.Solve(proc.env),self.kwargs.values())))
    args = map(lambda x: x.Solve(proc.env),self.args)
    tmp = ref[self.target]
    tmp = eval(f"dave.{self.command.Solve(proc.env)}",None,{"dave":tmp})
    out = tmp(*args,**self.kwargs)
    if self.dest:
      proc.env.update({self.dest.lexeme:out})
  
# tcl based commands [ for setting up stuff ]
@dataclass()
class c_tk_el_pack(BaseCommand):
  config:list
  def on_Parse(self,backend):
    self.config = dict(zip(map(lambda x:x.lexeme,self.config[::2]),
                           self.config[1::2])) if self.config else {}
  def exec(self,arb,proc):
    for k,v in self.config.items(): self.config[k] = v.Solve(proc.env)
    proc.env.get(" prevele").pack(**self.config)
@dataclass()
class c_tk_el_grid(BaseCommand):
  row:object
  column:object
  config:list
  def on_Parse(self,backend):
    self.config = dict(zip(map(lambda x:x.lexeme,self.config[::2]),
                           self.config[1::2])) if self.config else {}
  def exec(self,arb,proc):
    for k,v in self.config.items(): self.config[k] = v.Solve(proc.env)
    proc.env.get(" prevele").grid(row=int(self.row.Solve(proc.env)),
                                  column=int(self.column.Solve(proc.env)),
                                **self.config)
@dataclass()
class c_tk_el_con(BaseCommand):
  config:list
  def exec(self,arb,proc):
    params = {}
    for k,v in zip(self.config[::2],self.config[1::2]):
      params[k.lexeme] = v.Solve(proc.env)
    if "command" in params:
      params["command"] = prepInvoke(proc,params["command"])
    globals().update({"prevelem":params})
    proc.env.get(" prevele").config(**params)

@dataclass()
class c_tk_el_bind(BaseCommand):
    tcl_event:object
    arb_event:object
    def exec(self,arb,proc):
      tmp = proc.env.get(" prevele")
      tmp.bind(self.tcl_event.Solve(proc.env),prepInvoke(proc,self.arb_event.lexeme))
# 

syntax = """
# process commands #
  element:&-|&£; <bind element c_tk_element>
  call:&*:args[*]:kwargs[&~=*]:out&; <bind call c_tk_call>
# Arbiter specific commands #
<namespace _ arbiter>
  init:&; <bind init c_tk_init>

# commands for defining elements #
<namespace _element>
  pack::config[&~=*]; <bind pack c_tk_el_pack>
  grid:**:config[&~=*]; <bind grid c_tk_el_grid>
  config:[&~=*]; <bind config c_tk_el_con>
  bind:*&; <bind bind c_tk_el_bind>
"""

modvars = {"tk":tk,"tk_single":tk_single,"tk_multi":tk_multi,"managedWindow":managedWindow}

def module_init(backend):
  print("tkinter now available",file=backend.bout)