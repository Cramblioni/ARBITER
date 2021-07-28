
# ARBITER Arbiter new parser for introducing pieramperakat
#ignore the clunky python

# parser building code
# syntax
## name: initial ;
## name: initial : mod :...;
### *  - expression
### ^  - keyword [multiple char]
### &  - name
### ~  - token [single char]
### -  - tag [Token that's passed through as a parameter]
### £  - code body
### [] - repeatative
### '- - Defaulted Tag
### '& - Defaulted name
### |  - either of [the previous two]

import sys
import os

class vfile:
  cont:str = ""
  def write(self,data,*args):
    self.cont += data
  def print(self):
    print(self.cont.expandtabs(8),end="")
    self.cont = ""
vf = vfile() 

from dataclasses import dataclass
#from pclasses import*
from copy import copy
from itertools import chain

class liter:
  def __init__(self,llist):
    self.list = llist
  def __iter__(self) : return self
  def __next__(self):
    if self.list:
      return self.list.pop(0)
    else: raise StopIteration
  def __repr__(self): return repr(self.list)
  def peek(self):
    if self.list: return self.list[0]
    else: raise StopIteration
  def peekd(self,default):
    if self.list: return self.list[0]
    else: return default

@dataclass()
class re_iter:
  cond:object
  itr:iter
  __tmp = iter([])
  def __next__(self):
    try: return next(self.__tmp)
    except StopIteration:
      if self.cond(): self.__tmp = copy(self.itr) ; return next(self)
      else:raise StopIteration

class dsp(type):
  def __repr__(self): return self.__name__ + "()"
def gener(x):
  g = f"@dataclass(frozen=True)\nclass {x}:pass"
  exec(g,globals())

def sgener(x):
  x,*dta = x
  if dta[-1][0] == True: rf,rfv = dta[-1] ; dta.pop()
  else: rf = False
  g = f"@dataclass(frozen=True)\nclass {x}(metaclass=dsp):\n  "
  g+= "\n  ".join(map(lambda x: f"{x[0]}:{x[1].__name__}",dta))
  if rf == True: g+=f"\n  def Solve(self):return self.{rfv}"
  exec(g,globals())

[*map(gener,["t_expr", # b 
             "t_cb",   # b
             "t_eo", # either of
             "t_or",
             "t_cr",
             "t_df",
             "t_ed"])
]

[*map(sgener,[("t_token",("tok",chr)),              # s
              ("t_tag",("default",chr)),            # s
              ("t_name",("default",str)),           # s
              ("t_repeat",("toks",list)),           # b
              ("t_tor",("a",object),("b",object)),  # b
              ("t_keyword",("wrd",str)),            # s
              ("t_ident",("wrd",str))
              ])
]


def i_lexer(txt):
  itr = iter(txt.strip())
  cc  = next(itr,None)
  # func
  def extract():
    nonlocal itr,cc
    tmp = ""
    while cc and cc.isalpha(): tmp += cc ; cc = next(itr,None)
    return tmp
  def step():
    nonlocal itr,cc  
    cc = next(itr,None)
    if cc in [" ","\t","\n","\r"]:step()
    return cc
  # func
  out = []
  while cc:
    assert cc not in [" ","\t","\n","\r"]
    if   cc == "*"    : out.append(t_expr()) ; step()
    elif cc == "&"    : out.append(t_name(None)) ; step()
    elif cc == "^"    : step() ; out.append(t_keyword(extract()));
    elif cc == "~"    : step() ; out.append(t_token(cc)) ; step()
    elif cc == "-"    : out.append(t_tag(None)) ; step()
    elif cc == "£"    : out.append(t_cb()) ; step()
    elif cc == "["    : out.append(t_or()) ; step()
    elif cc == "]"    : out.append(t_cr()) ; step()
    elif cc == ":"    : out.append(t_df()) ; step()
    elif cc == ";"    : out.append(t_ed()) ; step()
    elif cc == "'"    :
      if step() == "-":
        out.append(t_tag(step())) ; step()
      elif cc == "&":
        step()
        out.append(t_name(extract()))
    elif cc == "|":
      b,a = out.pop(),out.pop()
      out.append(t_tor(a,b)) ;step()
    elif cc.isalpha() : out.append(t_ident(extract()))

  return out

@dataclass()
class csd:
  name:str
  initial:list
  mods:list

def i_parse_single(tokstream):
  #subroutines
  def step(): nonlocal ct,itr ; ct = next(itr,None)
  def exre():
    nonlocal itr, ct
    cp = []
    while ct and ct != t_cr():
      cp.append(ct)
      step()

    step()
    return t_repeat(cp)
  #mainfunc
  name,verif,*toks=tokstream # for processing boi
  name = name.wrd
  initial,mods = [],{} # for populating the object
  assert verif == t_df()
  itr = iter(toks)
  ct = None ;step()
  # doing the initial parse
  while ct not in [t_df(),t_ed()]:
    if ct == t_or(): step() ; initial.append(exre())
    else: initial.append(ct) ; step()
  if ct == t_ed(): return csd(name,initial,mods),itr
  cn,cp = None,[]
  while ct != t_ed():
    
    if ct == t_df():
      if cn != None: mods[cn] = cp 
      cp = []
      step();cn = ct.wrd; step() 
    elif ct == t_or(): step() ; cp.append(exre())
    else: cp.append(ct) ; step()
  else: mods[cn] = cp
  return csd(name,initial,mods),itr
      
def i_parse(tokstream):
  if tokstream == []: return []
  fp,nt = i_parse_single(tokstream)
  out = [fp]
  toks = list(nt)
  while toks:
    fp,nt = i_parse_single(toks)
    toks = list(nt)
    out.append(fp)
  return out





# The lexer for ARBITER
## Token Classes
@dataclass(frozen=True)
class Name:
  wrd:str
@dataclass(frozen=True)
class String:
  value:str
  def Solve(self,env):return self.value
@dataclass(frozen=True)
class Number:
  value:float
  def Solve(self,env): return self.value
class ocb:pass
class ccb:pass
def OCB(): return ocb
def CCB(): return ccb


## daver
def a_lexer(txt):
  out = []
  itr = iter(txt)
  cc = next(itr,None)
  assert cc # There should be something to parse

  ## sub functions
  def eStr():
    nonlocal itr,cc
    tmp = ""
    cc = next(itr)
    while cc and cc != '"':
      tmp += cc
      cc = next(itr,None)
    cc = next(itr,None)
    return String(eval(f'"{tmp}"'))
  def eName():
    nonlocal itr,cc
    tmp = ""
    while cc and (cc.isalpha() or cc.isdigit()):
      tmp += cc
      cc = next(itr,None)
    return Name(tmp)
  def eNum():
    nonlocal itr,cc
    tmp,dd = ("0",0)[:2] if cc == "." else ("",0)
    while cc and (cc == "." or cc.isdigit()):
      if cc == ".":
        if dd == 1: break
        else: dd+=1;tmp+=cc
      else:
        tmp+=cc
      cc = next(itr,None)
    return Number(float(tmp))
  def strip_comment():
    nonlocal itr,cc
    tmp = next(itr,None)
    while tmp and tmp != "#":
      tmp = next(itr,None)
    cc = next(itr,None)
  ## mainloop
  while cc:
    if cc in " \t\n" : cc = next(itr,None)
    elif cc.isalpha(): out.append(eName())
    elif cc == "#": strip_comment()
    elif cc == "\""  : out.append(eStr())
    elif cc == "." or cc.isdigit() : out.append(eNum())
    elif cc == "[": out.append(OCB()) ; cc = next(itr,None)
    elif cc == "]": out.append(CCB()) ; cc = next(itr,None)
    elif cc in "+=-*/,()<>&|_~": out.append(cc) ; cc = next(itr,None)
  return out

#ARBITER parsing
# defining every expression class
@dataclass()
class UnOp:
  op:chr
  c:object
  def Solve(self,env):
    if   self.op=='-':return self.c.Solve(env).__neg__()
    elif self.op=='+':return self.c.Solve(env).__pos__()

@dataclass(frozen=True)
class BiOp:
  op:chr
  a:object ; b:object
  def Solve(self,env):
    if   self.op=='-'  :
      out = self.a.Solve(env).__sub__(self.b.Solve(env))
      if isinstance(out,type(NotImplemented)):
        return self.b.Solve(env).__rsub__(self.a.Solve(env))
      else: return out
    elif self.op=='+'  :
        out = self.a.Solve(env).__add__(self.b.Solve(env))
        if isinstance(out,type(NotImplemented)):
          return self.b.Solve(env).__radd__(self.a.Solve(env))
        else: return out
    elif self.op=='/'  :
        out = self.a.Solve(env).__truediv__(self.b.Solve(env))
        if isinstance(out,type(NotImplemented)):
          return self.b.Solve(env).__rtruediv__(self.a.Solve(env))
        else: return out
    elif self.op=='*'  :
        out = self.a.Solve(env).__mul__(self.b.Solve(env))
        if isinstance(out,type(NotImplemented)):
          return self.b.Solve(env).__rmul__(self.a.Solve(env))
        else: return out
    elif self.op=='='  : return float(self.a.Solve(env).__eq__(self.b.Solve(env)))
    elif self.op=='!=' : return float(self.a.Solve(env).__ne__(self.b.Solve(env)))
    elif self.op=='>'  : return float(self.a.Solve(env).__gt__(self.b.Solve(env)))
    elif self.op=='>=' : return float(self.a.Solve(env).__ge__(self.b.Solve(env)))
    elif self.op=='<'  : return float(self.a.Solve(env).__lt__(self.b.Solve(env)))
    elif self.op=='<=' : return float(self.a.Solve(env).__le__(self.b.Solve(env)))
    elif self.op=='&&' : return float(bool(self.a.Solve(env)) and bool(self.b.Solve(env)))
    elif self.op=='||' : return float(bool(self.a.Solve(env)) or  bool(self.b.Solve(env)))

@dataclass(frozen=True)
class RefOp:
  name:str
  def Solve(self,env):
    return env.get(self.name)
# arbiter parsing



arb2ape = {Number: t_expr, String: t_expr, UnOp: t_expr, BiOp:t_expr, RefOp:t_expr,
           OCB():t_cb,
           str:[t_token,t_tag],
           Name:[t_keyword,t_name]
          }# ARBITER -> APEL Token reference
ape2arb = {t_expr     :(Number,String,Name,*"+-("),
           t_cb       :(OCB(),),
           t_token    :(str,),         t_tag  :(str,),
           t_keyword  :(Name,),        t_name :(Name,),
           t_repeat   : None,
           t_tor      : None
           }# APEL -> ARBITER Token reference [For parsing]
           

def a_parse_expr(itr): # five tier expression parser [unary,high binary,low binary,comp,logic]
  cc = None
  def step():
    nonlocal cc ; cc = next(itr,None)
    return cc
  step()
  
  def unary():
    nonlocal cc
    if isinstance(cc,Number) or isinstance(cc,String):
      result = cc ; step()
      return result
    elif isinstance(cc,Name):
      result = RefOp(cc.wrd) ; step()
      return result
    elif cc == "(":
      step()
      result = logic()
      step()#;step()
      return result
    elif cc in ["+","-"]:
      op = cc
      step()
      result = UnOp(op,unary())
      #step()
      return result
      
  def hbinary():
    nonlocal cc
    result = unary()
    while cc and cc in ["*","/"]:
      op = cc
      step()
      result = BiOp(op,result,unary())
    return result

  def lbinary():
    nonlocal cc
    result = hbinary()
    while cc and cc in ["+","-"]:
      op = cc
      step()
      result = BiOp(op,result,hbinary())
    return result
  
  def comp():
    nonlocal cc,itr
    result = lbinary()
    if cc in ["=","!","<",">"]:
      op = cc
      if cc != "=" and itr.peek() == "=":
        op += step()
      step()
      result = BiOp(op,result,lbinary())
    return result      

  def logic():
    nonlocal cc
    result = comp()
    while cc and cc in ["|","&"]:
      op = cc + step()
      step()
      result = BiOp(op,result,comp())
    return result

  out = logic()
  itr.list.insert(0,cc)
  return out

def a_parse_body(itr): # extract body as a pure tokenstream[doesn't parse it]
  out = []
  d = 1
  cc = next(itr,None)
  while cc and d > 0:
    if cc is OCB(): d+=1
    elif cc == CCB():d-=1
    out.append(cc)
    if d == 0 : break # this preserves the next token after CCB
    cc = next(itr,None)
  return out[:-1]

def ia_comp_toks(itr,tok):

  def _eron(x,ref):
    try: return isinstance(ref,x)
    except TypeError: return x == ref
  def eron(t,ref):
    return any(map(lambda x:_eron(x,ref),ape2arb.get(t)))
    
  tt = type(tok)

  if  tt == t_expr:
    ref = itr.peek()
    if not eron(tt,ref): raise TypeError(f"{ref} :: EXPECTED EXPR")
    return a_parse_expr(itr)
  
  elif tt == t_name:
    if tok.default == None:
      if not isinstance(itr.peek(),Name) : raise TypeError
      return next(itr)
    else:
      if isinstance(itr.peek(),Name):
        return next(itr)
      else: return tok.default
  elif tt == t_keyword:
    if not isinstance(itr.peek(),Name) : raise TypeError
    elif tok.wrd != next(itr).wrd: raise ValueError

  elif tt == t_tag:
    if not isinstance(itr.peekd(None),str):
      if tok.default: return tok.default
      else: raise TypeError
    else:
      return next(itr)
  elif tt == t_token:
    if not isinstance(itr.peek(),str): raise TypeError
    elif tok.tok != next(itr): raise ValueError
    else:return

  elif tt == t_repeat:
    out = []
    for i in tok.toks:
      tmp = ia_comp_toks(itr,i)
      if tmp:out.append(tmp)
    while itr.peek() == ",":
      next(itr)
      for i in tok.toks:
        tmp = ia_comp_toks(itr,i)
        if tmp:out.append(tmp)
    return out
  elif tt == t_cb:
    assert itr.peek() == OCB()
    next(itr)
    out = a_parse_body(itr)
    return out

  elif tt == t_tor:
    try:
      out = ia_comp_toks(itr,tok.a)
    except TypeError or ValueError:
      out = ia_comp_toks(itr,tok.b)
    return out

def a_parse_single(itr,pps):
  # this makes more sense in theory
  #print("\nnew command")
  if not itr.peekd(False) : raise StopIteration
  command = next(itr).wrd
  model = None
  for i in pps:
    if model != None: continue
    #print(i.name,"=",command,i.name == command,type(model))
    if i.name == command:
      model = i
  #print(command)
  assert model != None # prove a command has been found
  #print(model)
  # initial parse
  outtype = eval("c_"+command)
  outpars = [] # this is to store the params

  for tok in model.initial:
    tmp = ia_comp_toks(itr,tok)
    if tmp != None: outpars.append(tmp)

  #secondary parse
  for k,v in model.mods.items():
    if isinstance(itr.peekd(None),Name) and itr.peek().wrd == k:
      next(itr)
      for tok in v:          
        tmp = ia_comp_toks(itr,tok)
        if tmp: outpars.append(tmp)
    else:
      outpars.extend([None for i in v])
  return outtype,outpars

def a_parse(tokenstream,pps,backend):
  #global backend
  #print("PARSERSET",*pps,sep="\n\t")
  itr = liter(tokenstream)
  out = []
  while True:
    try:
      ncom,params = a_parse_single(itr,pps)
    except StopIteration:
     break
    except AssertionError:
      raise SyntaxError
    else:
      if ncom == None: continue
      else :
        nco = ncom(*params)
        out.append(nco)
        nco.on_Parse(backend)
  return out
# Management classes

class Backend:
  """Simple class to make parsing a lot easier
Roles include:
  - getting prepared parsers [for both ARBITER and APEL]
  - changing parsing contexts [for ARBITER]
  - Registering new contexts
  - Handles Python references [keeping neat and tidy]
  """
  def __init__(self):
    "Creates a new ARBITER backend [There should only be ONE of these]"
    self.setcntx = [None]
    self.extra = {}
    self.BASE = []
    self.BASE_ARBITER =[]
    self.mode = 0 # ARB
    self.PATH = [".\\",
                 ".\\MODS\\"]
    self.arbextf = []
    self.bout = vf
    self.getnloadModule("pclasses", True)
    
  def registerSet(self,name,pset):
    self.extra.update({name:pset})
    
  def getIParser(self):
    return lambda txt: i_parse(i_lexer(txt))
  
  def getParser(self):
    
    cntx = self.BASE[:]
    if self.mode == 0: cntx = self.BASE_ARBITER#;print("\tgetting parser using ARBITER set")
    elif self.setcntx[-1]:
      cntx.extend(self.extra.get(self.setcntx[-1],[]))
      #print("\tgetting parser using",self.setcntx[-1],"set")
    return lambda toks:a_parse(toks,cntx,self)

  def setParserMode(self,mode):
    self.mode = mode

  def setParserSet(self,pset):
    self.setcntx.append(pset)
    
  def unsetParserSet(self):
    self.setcntx.pop()

  def registerARBITERtickfunc(self,func):
    self.arbextf.append(func)
  
  def loadModule(self,path,B=False):
    global vf
    class empt: pass
    venv = {}
    with open(path,"r") as f:
      exec(f.read(),None,venv)
    tmp = venv.get("syntax")
    tmp_a = venv.get("syntax_a",False)
    tmpp = i_parse(i_lexer(tmp))
    if B == True: self.BASE.extend(tmpp) ; self.BASE_ARBITER.extend(tmpp)
    else: self.registerSet(B,tmpp)

    if tmp_a:
      tmp_ap = i_parse(i_lexer(tmp_a))
      self.BASE_ARBITER.extend(tmp_ap) 

    look = venv.get("commands",{})
    for i in tmpp:
      comcla = f"c_{i.name}"
      tmp = look.get(comcla,False)
      print("\tloading",comcla,end="...",file=vf)
      if tmp:
        globals().update({comcla:tmp})
        print("Success",file=vf)
      else: raise ImportError
    if tmp_a:
      for i in tmp_ap:
        comcla = f"c_{i.name}"
        tmp = look.get(comcla,False)
        print("ARB\tloading",comcla,end="...",file=vf)
        if tmp:
          globals().update({comcla:tmp})
          print("Success",file=vf)
        else: raise ImportError

    venv.get("module_init")(self)

    if "modvars" in venv:
      for k,v in venv.get("modvars").items():
        
        globals().update({k:v})
    
  def getnloadModule(self,name,B=False):
    # try .py .txt
    path = None
    for i in self.PATH:
      test = os.listdir(i)
      for ext in [".py",".txt"]:
        if name+ext in test:
          path = i + name + ext
          break
        if path:break
    self.loadModule(path,B)
    
class Executer: # base class for executing code
  # for initialising
  __delbuff = []

  def releaseCurrent(self):
    self.__delbuff[-1].append(self.__ind)

  def initialise(self,code):
    self.__delbuff.append([])
    
    temp = code[:]
    for self.__ind,x in enumerate(temp):
      x.on_Init(self.arb,self)
     # print("INITIALISING",x,file=vf)
    for o,i in enumerate(self.__delbuff[-1],0):
      #print("\t"*len(self.__delbuff),"removing",i-o,temp[i-o],file=vf)
      temp.pop(i-o)
    self.__delbuff.pop()
    return temp

  def registerEvent(self,name,body):
    tmp = self.initialise(body)
    self.events.update({name:tmp})
  # lol

  def __init__(self,code,arb,env={}):
    self.env = env
    self.arb = arb
    self.events = {}
    # setting up execution variables
    self._equeue = [] # a queue of stacks
    self._astack = [] # a stack of tags
    #boom init innit
    self.__curaci = 0 # current index to active equeue stack
    self.newprocedure(code)
    self.alive = True

  def _getnext(self,ind=-1):
    #first search
    if ind < -len(self._astack): return None
    if self._astack[ind] != None:
      return self._getnext(ind-1)
    self.__curaci = ind
    if self._equeue[ind] == []:
      del self._equeue[ind]
      del self._astack[ind]
      return self._getnext(ind-1)
    tmp = next(self._equeue[ind][-1],None)
    if tmp == None:
      self._equeue[ind].pop()
      return self._getnext(ind)
    else: return tmp

  def __next__(self):
    tmp = self._getnext()
    if tmp != None: tmp.exec(self.arb,self)
    return self.alive

  def __iter__(self): return self

  def invoke(self,event):
    #print("PROCESS INVOKED",event)
    for i,x in enumerate(self._astack[:]):
      if x == event or x == "*": self._astack[i] = None
    ev = self.events.get(event,False)
    if ev: self.newprocedure(ev)
      

  def newprocedure(self,code): # code isn't an iterator
    ncb = self.initialise(code)
    self._astack.append(None)
    self._equeue.append([iter(ncb)])
    return len(self._astack) - 1

  def addprocedure(self,code,cond=None):
    ncb = iter(self.initialise(code))
    self._equeue[self.__curaci].append(ncb if cond == None else re_iter(cond,ncb))

  def currentawait(self,event):
    self._astack[self.__curaci] = event

  def kill(self):
    self.alive = False

  def flush(self,nid):
    tmp = self._equeue[nid]
    while tmp:
      try:com = next(tmp[-1])
      except StopIteration: tmp.pop() ; continue
      else:
        com.exec(self.arb,self)
    self._equeue.pop(nid)
    self._astack.pop(nid)
  
class ARBITER(Executer):
  def __init__(self,code,backend):
    self.aout = vfile()
    self.ain = vfile()
    self.backend = backend
    self.procs = []
    self.refs = {}
    self.__extra = backend.arbextf
    Executer.__init__(self,code,self)

  def _invoke(self,event):
    Executer.invoke(self,event)
  def invoke(self,event,scope):
    #print("ARBITER INVOKED",event,scope)
    if scope == "~":
      self._invoke(event)
    else:
      for i in self.procs: i.invoke(event)
      self._invoke(event)

  def registerReference(self,name,body):
    self.refs.update({name:body})

  def createProcess(self,ref,iev):
    ie = {}
    for k,v in iev.items():
      ie.update({k:v})
    self.procs.append(Executer(self.refs.get(ref),self,ie))
  
  def __next__(self):
    tmp = Executer.__next__(self)
    __delbuff = []
    for i,x in enumerate(self.procs):
      if not next(x): __delbuff.append(i)
    for o,i in enumerate(__delbuff):
      del self.procs[i-o]
    for i in self.__extra: i(self)
    return tmp or bool(self.procs)

### PROGRAMMER NOTE
## TODO
#   - Create import PATH searcher ¬
#   - Create execute part of executer ¬!
#   - derive specific ARBITER class from executer ~

 
if __name__ == "__main__":
  backend = Backend()
  #backend.loadModule(".\pclasses.py",True)
  prog_t = r"""

  union tkinter as  tk
  setup single
  ref e [] using tk
  end
            """
  prog = a_lexer(prog_t)
  progd = prog[:]
  parser = backend.getParser()
  res = parser(prog)
  exe = ARBITER(res,backend)
  print(prog_t,sep="\n",file=vf)
  #vf.print()
  vf.cont = ""
  print("\n")
  while next(exe):
    #print(exe.env,*map(lambda x:x.env,exe.procs),sep="\n\t")
    print(exe.aout.cont,end="")
    exe.aout.cont = ""
