### faf
from copy import copy
from dataclasses import dataclass

def peek(iterator,default=StopIteration):
  o = copy(iterator)
  out = next(o) if default == StopIteration else next(o,default)
  del o
  return out

## Token Classes
@dataclass(frozen=True)
class Name:
  wrd:str
@dataclass(frozen=True)
class String:
  value:str
@dataclass(frozen=True)
class Number:
  value:float
  def Solve(self): return self.value
class ocb:pass
class ccb:pass
def OCB(): return ocb
def CCB(): return ccb
## daver
def lexer(txt):
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
  ## mainloop
  while cc:
    if cc in " \t\n" : cc = next(itr,None)
    elif cc.isalpha(): out.append(eName())
    elif cc == "\""  : out.append(eStr())
    elif cc == "." or cc.isdigit() : out.append(eNum())
    elif cc == "[": out.append(OCB()) ; cc = next(itr,None)
    elif cc == "]": out.append(CCB()) ; cc = next(itr,None)
    elif cc in "+=-*/,()<>&|_¬": out.append(cc) ; cc = next(itr,None)
  return out

## Syntax Classes
@dataclass()
class biOp:
  l:object
  r:object
  o:str
  def Solve(self):
    if self.o == "+":return self.l.Solve().__add__(self.r.Solve())
    if self.o == "-":return self.l.Solve().__sub__(self.r.Solve())
    if self.o == "*":return self.l.Solve().__mul__(self.r.Solve())
    if self.o == "/":return self.l.Solve().__truediv__(self.r.Solve())
@dataclass()
class unOp:
  n:object
  o:str
  def Solve(self):
    if self.o == "+":return self.n.Solve()
    if self.o == "-":return self.n.Solve().__neg__()
@dataclass()
class refOp:
  name:str
  env:dict
  def Solve(self): return self.env.get(self.name)
@dataclass()
class Comp:
  l:object
  r:object
  o:str
  def Solve(self):
    if self.o == "=" : return self.l.Solve().__eq__ (self.r.Solve())
    if self.o == ">" : return self.l.Solve().__gt__ (self.r.Solve())
    if self.o == "<" : return self.l.Solve().__lt__ (self.r.Solve())
    if self.o == ">=": return self.l.Solve().__ge__ (self.r.Solve())
    if self.o == "<=": return self.l.Solve().__le__ (self.r.Solve())
    if self.o == "!=": return self.l.Solve().__ne__ (self.r.Solve())
    if self.o == "||": return self.l.Solve().__or__ (self.r.Solve())
    if self.o == "&&": return self.l.Solve().__and__(self.r.Solve())

## Command Classes
@dataclass()
class c_set:
  target:Name
  value:object
  ext:bool = False
@dataclass()
class c_if:
  test:Comp
  body:list
  orelse:[list,None]
@dataclass()
class c_get:
  source:Name
  target:Name
@dataclass()
class c_single:
  body:list
@dataclass()
class c_invoke:
  id:str
  scope:int # 1 -> interactive # 2 -> arbiter # 3 -> local # default 1
@dataclass()
class c_await:
  id:str
@dataclass
class c_end:pass
@dataclass()
class c_event:
  body:list
  id:Name
  params:list[Name]
@dataclass()
class c_while:
  test:Comp
  body:list
@dataclass()
class c_bank:
  body:list
  event:dict
#arb
@dataclass()
class c_create:
  bid:str
  alias:str
@dataclass()
class c_arbiter:
  banks:dict
  body:list
  event:dict

## now onto parsing


      
def sParse(tokstream,penv = {},callback=None):
  ## simple Parser [used for individual banks]
  itr = iter(tokstream)
  cc = next(itr,None)
  assert cc
  # just some subfunctions
  def _parseExpr():
    nonlocal itr,cc,penv
    def indiv():
      nonlocal itr,cc,penv
      if isinstance(cc,Number):
        result = cc
        cc = next(itr,None)
      elif isinstance(cc,Name):
          result = refOp(cc.wrd,penv)
          cc = next(itr,None)
      elif cc == "(":
        result = pam()
        assert cc == ")"
        cc = next(itr,None)
      elif cc in ["+","-"]:
        op = cc
        cc = next(itr,None)
        result = unOp(indiv(),op)
        cc = next(itr,None)
      if "result" in locals():
        return result
      else:
        print(cc)
        assert False
    def mad():
      nonlocal itr,cc
      result = indiv()
      while cc and cc in ["*","/"]:
        op = cc
        cc = next(itr,None)
        result = biOp(result,indiv(),op)
      #print("endo loop")
      return result

    result = mad()
    while cc and cc in ["+","-"]:
      op = cc
      cc = next(itr,None)
      result = biOp(result,mad(),op)
    return result

  def _parseCond():
    nonlocal _parseExpr,itr,cc,penv
    def _getcond():
      nonlocal itr,cc
      op,cc = cc,next(itr,None)
      if op == "!":
        assert cc == "="
        op += cc
        cc = next(itr,None)
      elif op in [">","<"] and cc == "=":
        op += cc
        cc = next(itr,None)
      elif op in ["&","!"]:
        assert op == cc
        op += cc
        cc = next(itr,None)
      return op

    lval = _parseExpr()
    if cc == OCB(): return lval
    op = _getcond()
    rval = _parseExpr()
    out = Comp(lval,rval,op)
    while cc and not (isinstance(cc,Name) or cc == OCB()):
      op = _getcond()
      rval = _parseExpr()
      out = Comp(out,rval,op)
    return out

  ## main parser loop
  codebod = c_bank([],{})
  out = codebod.body
  while cc and (cc != CCB()):
    assert isinstance(cc,Name)
    #print(cc.wrd)
    if   cc.wrd == "set":
      trg= next(itr)
      cc= next(itr)
      val = _parseExpr()
      out.append(c_set(trg,val))
    elif cc.wrd == "ext" and peek(itr).wrd == "set":
      cc = next(itr,None)
      trg= next(itr)
      cc= next(itr)
      val = _parseExpr()
      out.append(c_set(trg,val,True))
    elif cc.wrd == "single":
      cc = next(itr,None)
      assert cc == OCB()
      body,_ = sParse(itr,penv)
      cc = next(itr,None)
      out.append(c_single(body.body))
    elif cc.wrd == "get":
      source = next(itr,None)
      target = next(itr,None)
      cc = next(itr,None)
      out.append(c_get(source,target))
    elif cc.wrd == "if":
      cc = next(itr,None)
      cond = _parseCond()
      assert cc == OCB()
      body,_ = sParse(itr,penv)
      body = body.body
      cc = next(itr,None)
      if cc and (cc.wrd == "else" and peek(itr) == OCB()):
        cc = next(itr,None)
        orelse,_ = sParse(itr,penv)
        orelse = orelse.body
        cc = next(itr,None)
      else:
        orelse = None
      out.append(c_if(cond,body,orelse))
    elif cc.wrd == "await":
      ident,cc = next(itr,None),next(itr,None)
      out.append(c_await(ident))
    elif cc.wrd == "invoke":
      ident,cc = next(itr,None),next(itr,None)
      if cc in ["_","*","¬"]:
        out.append(c_invoke(ident.wrd,"*¬_".index(cc) + 1))
        cc = next(itr,None)
      else :out.append(c_invoke(ident.wrd,1))
    elif cc.wrd == "event":
      ident,cc = next(itr,None),next(itr,None)
      assert cc == OCB()
      body,_ = sParse(itr,penv)
      body = body.body
      codebod.event.update({ident.wrd:body})
      cc = next(itr,None)
    elif cc.wrd == "while":
      cc = next(itr,None)
      cond = _parseCond()
      body,_ = sParse(itr,penv)
      out.append(c_while(cond,body.body))
      cc = next(itr,None)
    elif cc.wrd == "end":
      out.append(c_end())
      cc = next(itr,None)
    else:
      if callback:
        cc = callback(cc,itr,penv,out)
      else: cc = next(itr,None)
  return codebod,penv
      
      
def aParse(tokstream,penv = {}):
  ## arbiters parser [for parsing piky bollocks]
  itr = iter(tokstream)
  # just some subfunctions
  def asCallback(sfcc,sfitr,sfenv,sfoa):
    nonlocal itr
    cc=None
    if sfcc.wrd == "create":
      tmp = next(itr)
      cc = next(itr,None)
      if isinstance(cc,Name) and cc.wrd == "using":
        nm,cc = next(itr),next(itr,None)
        sfoa.append(c_create(nm,tmp))
      else:
        sfoa.append(c_create(tmp,None))
        
    elif sfcc.wrd in ["ref","reference"]:
      bname,cc = next(itr),next(itr,None)
      assert cc == OCB()
      body,_ = sParse(itr,sfenv)
      cc = next(itr,None)
      codebod.banks.update({bname.wrd:body})
    if cc:
      return cc
    else : return next(itr,None)
  ## main parser loop
  codebod = c_arbiter({},[],{})
  sap,_ = sParse(itr,penv,asCallback)
  codebod.body = sap.body
  codebod.events = sap.event
  return codebod,penv
      
def update(node,env):
  nd = node.__dict__
  if "env" in nd:
    nd.update({"env":env})
  else:
    for f,d in nd.items():
      if f != "banks":
        if isinstance(d,list):
          for i in d: update(i,env)
        else:
          try:
            update(d,env)
          except AttributeError: pass

  
def scd(dic):
  if isinstance(dic,dict):
    out = dict.fromkeys(dic.keys())
    for k,v in dic.items():
      out[k] = scd(v)
    return out
  elif "__dict__" in dir(dic):
    dd = dic.__dict__
    inp = {}
    for k,v in dd.items():
      inp[k] = scd(v)
    return type(dic)(**inp)
  elif isinstance(dic,list):
    return [scd(i) for i in dic]
  else:
    return copy(dic)

def new_bank(model,nenv): # for creating a shallow copy of a code bank
  out = scd(model)
  update(out,nenv)
  return out
