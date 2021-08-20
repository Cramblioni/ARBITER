
# utf8 or extended ascii
# ARBITER core with nicer pseudo-pythonic code
from lexing import Lexer,dataclass,Token,re
import sys,os
from copy import copy

class APEL:

  class col_rep:
    def __init__(self,pattern):
      self.pat = pattern
  class col_xor:
    def __init__(self,a,b):
      self.a,self.b = a,b

  def __init__(self):
    self.__lexer = Lexer()
    self.__lexer.rules = {
                   "ident":r"[a-zA-Z_]+",
                   "define":r"\:","enddef":r"\;",
                   "expr":r"\*",
                   "keyword":r"\^[a-zA-Z]+",
                   "token":r"~.",
                   "tag":r"\-",
                   "name":r"\&",
                   "dtag":r"\'\-.",
                   "dname":r"\'\&[a-zA-Z]",
                   "codbod":r"[\£\#]",
                   "xor":r"\|",
                   "srep":r"\[","erep":r"\]",
                   "sprg":r"\<","eprg":r"\>"
                 }
    self.__lexer.skips = r"\#.*?\#"
    self.__enum = self.__lexer.enum
    self._scene = {}
    self._binds = {}
    self.rans = {}

  def clearRans(self):
    self.rans.clear()
    
  def datwmtecar(self):
    return self._scene,self._binds
  def caalrifwr(self):
    return self.__enum
  
  def getNamespace(self,name):
    if name not in self._scene:
      self._scene[name]=out={}
      self._binds[name]=otb={}
    else:
      out = self._scene.get(name)
      otb = self._binds.get(name)
    return out,otb

  def buildEnv(self,*sources,arb=False):
    out = [self._scene.get(" BASE ")]
    otb = [self._binds.get(" BASE ")]
    for i in sources:
      out.insert(0,self._scene.get(i))
      otb.insert(0,self._binds.get(i))
    if arb:
      out.append(self._scene.get(" BASE  A"))
      otb.append(self._binds.get(" BASE  A"))
      for i in sources:
        out.insert(0,self._scene.get(i+" A"))
        otb.insert(0,self._binds.get(i+" A"))
    return out,otb
  def _parse_internal(self,itr):
    """  this is to parse a tokenstream to ensure shit works"""
    cur = []
    for ct in itr:
      if ct.type is self.__enum.xor:
        cur.append(self.col_xor(cur.pop(-2),cur.pop()))
      elif ct.type is self.__enum.srep:
        trt = []
        sct = next(itr)
        while sct.type is not self.__enum.erep: trt.append(sct) ; sct = next(itr)
        cur.append(self.col_rep(self._parse_internal(trt)))
      else: cur.append(ct)
    return cur
      
  def _parse_single(self,itr):
    out = {" initial":[]}
    cur = out.get(" initial")
    if next(itr).type is not self.__enum.define:raise SyntaxError(f"expected definition on line {com.lineno}")
    while True:
      ct = next(itr)
      if   ct.type is self.__enum.enddef: return out
      elif ct.type is self.__enum.define:
        mod = next(itr)
        out[mod.lexeme]=cur=[]
      elif ct.type is self.__enum.ident: raise SyntaxError(f"unexpected ident on line {ct.lineno}")
      elif ct.type is self.__enum.xor:
        cur.append(self.col_xor(cur.pop(-2),cur.pop()))
      elif ct.type is self.__enum.srep:
        trt = []
        sct = next(itr)
        while sct.type is not self.__enum.erep: trt.append(sct) ; sct = next(itr)
        cur.append(self.col_rep(self._parse_internal(trt)))
      else: cur.append(ct)
    
    
  def parse(self,text,entry=" BASE "):
    currns = entry
    self.clearRans()
    self.rans.update({entry:[]})
    tokstream,_= self.__lexer(text)
    itr = iter(tokstream)
    out,bnd = self.getNamespace(entry)
    parsing = True
    while parsing:
      try:
        rule = next(itr)
        if rule.type is self.__enum.ident:
          srule = rule.lexeme
          pats = self._parse_single(itr)
          if srule in out:
            pats.pop(" initial")
          else:
            out[srule]={}
          out.get(srule).update(pats)
          if srule not in bnd:
            bnd.update({srule:"c_" + srule})
            self.rans.get(currns).append(srule)

        elif rule.type is self.__enum.sprg:

          mode = next(itr)
          if mode.type is not self.__enum.ident :raise SyntaxError("expected mode on line {mode.lineno}")

          elif mode.lexeme == "namespace":
            name = next(itr).lexeme
            if name == "_" : name = entry
            elif name=="__": name = " BASE "
            temp = next(itr) ; sta,sol = False,False
            while temp.type is not self.__enum.eprg:
              if temp.lexeme.upper() == "ARBITER": sta = True
              elif temp.lexeme.upper() == "OVERLOAD": sol = True
              temp = next(itr)
            currns = name + " A"*sta
            out,bnd = self.getNamespace(name + " A"*sta)
            if currns not in self.rans: self.rans.update({currns:[]})
            if sol: clear()
          
          elif mode.lexeme == "bind":
            target = next(itr).lexeme
            source = next(itr).lexeme
            next(itr)
            bnd.update({target:source})
            self.rans.get(currns).append(target)

          elif mode.lexeme == "require":
            requires = []
            tmp = next(itr)
            if next(itr).lexeme == "source":
              src = next(itr).lexeme
              next(itr)
            else:
              src = tmp.lexeme

            if tmp.lexeme not in self._scene:
              try:
                self.Backend.getnload(src)
              except NameError:pass
            
        else:
          raise SyntaxError(f"expected identity or pragma on line {rule.lineno}")
        
      except StopIteration:
        parsing = False
        


class ARBITER: # working as backend aswell

  # sub classes [because you can use these as if they're namespaces]?
  class liter:
    def __init__(self,llist): self._list = list(llist)
    def __repr__(self):
      try:return repr(self._list)
      except AttributeError: return '[]'
    @property
    def list(self):return self._list
    def __iter__(self):return self
    def __next__(self):
      try:return self._list.pop(0)
      except IndexError as e: raise StopIteration from e
    def peek(self,df=StopIteration):
      if self._list: return self._list[0]
      elif df is StopIteration: raise StopIteration
      else: return df
  ## expr Types [of course using dataclasses]
  @dataclass()
  class UnOp:
    c:object ; op:str
    def Solve(self,env):
      if self.op  =="GET": return env.get(self.c)
      elif self.op=="LIT": return self.c
      tmp = self.c.Solve(env)
      if   self.op == "+": return tmp.__pos__()
      elif self.op == "-": return tmp.__neg__()
      elif self.op == "!": return float(not bool(tmp))
      elif self.op=="INT": return int(tmp)
  @dataclass()
  class BiOp:
    a:object ; b:object ; op:str
    def Solve(self,env):
      a,b = self.a.Solve(env),self.b.Solve(env)
      # arithmatic operations
      if   self.op == "+" : return a + b
      elif self.op == "-" : return a - b
      elif self.op == "*" : return a * b
      elif self.op == "/" : return a / b
      # comparitive operations
      elif self.op == ">" : return float(a >  b)
      elif self.op == ">=": return float(a >= b)
      elif self.op == "<" : return float(a <  b)
      elif self.op == "<=": return float(a <= b)
      elif self.op == "=" : return float(a == b)
      elif self.op == "!=": return float(a != b)
      # logical operations
      elif self.op == "&&": return float(bool(a) and bool(b))
      elif self.op == "||": return float(bool(a) or  bool(b))
      
  # actual class normative code
  
  def __init__(self,aperef):
    self.APEL = aperef
    self.APEL.Backend = self
    self.__lexer = Lexer()
    self.__lexer.rules = {
                   "name"   : r"[a-zA-Z]+",
                   "number" : r"\d+(\.\d*)?",
                   "string" : r'".*?"',
                   "token"  : r"[\|\&\*\+\-\\\._~\=\,\>\<\/]",
                   "oparen" : r"\(",
                   "cparen" : r"\)",
                   "ocodbo" : r"\[",
                   "ccodbo" : r"\]"
                 }
    self.__lexer.skips = r"\#.*?\#"
    self.__enum = self.__lexer.enum
    self._cobjb = {}
    self.bout = sys.stderr

    # Stuff to do with parser sharing

    self.__ems = [[]]
    self.__am = True
    # Bolter backend

    self.PATH = [".\\",".\\MODS\\"]
    
  def setParserMode(self,mode):
    self.__am = not bool(mode)
  def setParserSet(self,*pset):
    self.__ems.append(pset)
  def unsetParserSet(self):
    self.__ems.pop()

  def prog_load(self,path,entry=" BASE "):
    """ raglenran bax ffng en vawrvwithu APEL e pethdatwm o sgript Python """
    venv = {}
    with open(path,"rb") as f:
      exec(f.read().decode("utf8"),None,venv)
    syntax = venv.get("syntax","")
    self.APEL.parse(syntax,entry)
    globals().update(venv.get("modvars",{}).items())
    for ns,btu in self.APEL.rans.items():
      for v in btu:
        bname = self.APEL._binds[ns][v]
        tmp = venv[bname]
        self._cobjb.update({bname:tmp})

    venv.get("module_init",lambda x:0)(self)

  def _parse_body(self,itr):
    d = 1
    out = []
    while d > 0:
      tmp=next(itr)
      if   tmp.type is self.__enum.ocodbo: d += 1
      elif tmp.type is self.__enum.ccodbo: d -= 1
      if d == 0: break
      else: out.append(tmp)
    return out

  def _parse_expr(self,itr):
    ct = None
    # sub functions
    def step():
      nonlocal ct; ct = next(itr,None)
      return ct
    step()

    def single():
      nonlocal ct
      if   ct.type is self.__enum.number:
        res = self.UnOp(float(ct.lexeme),"LIT")
        step()
        return res
      elif ct.type is self.__enum.string:
       res = self.UnOp(eval(f'""{ct.lexeme}""'),"LIT")
       step()
       return res
      elif ct.type is self.__enum.name:
        res = self.UnOp(ct.lexeme,"GET") ; step()
        return res
      elif ct.type is self.__enum.token and ct.lexeme in "+-!":
        op=ct.lexeme ; step()
        return self.UnOp(single(),op)
      elif ct.type is self.__enum.oparen:
        step()
        tmp = logic()
        step()
        return tmp
      elif ct.type is self.__enum.token and ct.lexeme == "*":
        step()
        return self.UnOp(single(),"INT")

    def mad():
      nonlocal ct
      result = single()
      while ct and ct.type is self.__enum.token and ct.lexeme in "*/":
        op = ct.lexeme
        step()
        result = self.BiOp(result,single(),op)
      return result
    
    def aas():
      nonlocal ct
      result = mad()
      while ct and ct.type is self.__enum.token and ct.lexeme in "+-":
        op = ct.lexeme
        step()
        result = self.BiOp(result,mad(),op)
      return result
        
    def comp():
      nonlocal ct
      result = aas()
      if ct and ct.type is self.__enum.token and ct.lexeme in "!=><":
        op = ct.lexeme;step()
        if op != "=" and ct.lexeme == "=": op+="=";step()
        result = self.BiOp(result,aas(),op)
      return result

    def logic():
      nonlocal ct
      result = comp()
      while ct and ct.type is self.__enum.token and ct.lexeme in "&|":
        op = ct.lexeme
        step()
        op += ct.lexeme
        step()
        result = self.BiOp(result,comp(),op)
      return result

    out = logic()
    if ct != None:
      itr.list.insert(0,ct)
    return out

  def _mergeAPEARB(self,itr,tok,refln = -1):
    anum = self.APEL.caalrifwr()
    if   isinstance(tok,self.APEL.col_xor):
      try:
        return self._mergeAPEARB(itr,tok.a,refln)
      except SyntaxError:
        return self._mergeAPEARB(itr,tok.b,refln)

    elif isinstance(tok,self.APEL.col_rep):
      erwte = []
      for i in tok.pat:
        tmp = self._mergeAPEARB(itr,i,refln)
        if tmp != None:
          erwte.append(tmp)
      while itr.peek(None) and itr.peek().lexeme==",":
        next(itr)
        for i in tok.pat:
          tmp = self._mergeAPEARB(itr,i,refln)
          if tmp != None:
            erwte.append(tmp)
      return erwte
        
    elif tok.type is anum.keyword:##
      tmp = itr.peek()
      if tmp.type is not self.__enum.name or tmp.lexeme != tok.lexeme[1:]:
        raise SyntaxError(f"invalid syntax on line {tmp.lineno} expected {tok.lexeme[1:]}")
      next(itr)
    elif tok.type is anum.name:##
      tmp = itr.peek()
      if tmp.type is not self.__enum.name: raise SyntaxError(f"expected name/keyword on line {tmp.lineno}")
      else: next(itr) ; return tmp
    elif tok.type is anum.token:##
      tmp = itr.peek()
      if tmp.type is not self.__enum.token or tmp.lexeme != tok.lexeme[1:]:
        raise SyntaxError(f"expected {tok.lexeme[1:]} on line {tmp.lineno}")
      next(itr)
    elif tok.type is anum.tag:##
      tmp = itr.peek()
      if tmp.type is not self.__enum.token: raise SyntaxError(f"expected tag on {tmp.lineno}")
      else: next(itr); return tmp
    elif tok.type is anum.dname:##
      tmp = itr.peek(None)
      if tmp == None:return Token(self.__enum.name,tok.lexeme[2:],refln)
      if tmp.type is not self.__enum.name: return Token(self.__enum.name,tok.lexeme[2:],tmp.lineno)
      else: next(itr); return tmp
    elif tok.type is anum.dtag:##
      tmp = itr.peek(None)
      if tmp == None:return Token(self.__enum.token,tok.lexeme[2:],refln)
      elif tmp.type is not self.__enum.token: return Token(self.__enum.token,tok.lexeme[2:],tmp.lineno)
      else: next(itr); return tmp
    elif tok.type is anum.codbod:##
      if itr.peek(None) and itr.peek().type is self.__enum.ocodbo:
        next(itr)
        out = self._parse_body(itr)
        return out
      elif itr.peek(None):
        raise SyntaxError(f"expected codebody ([]) on line {itr.peek().lineno}")
      else:
        raise SyntaxError("CATASTROPHIC FAILURE")
    elif tok.type is anum.expr:##
      tmp = itr.peek()
      if (tmp.type is self.__enum.name or tmp.type is self.__enum.token or 
            tmp.type is self.__enum.number or tmp.type is self.__enum.string ):
        out = self._parse_expr(itr)
        return out
      else:
        raise SyntaxError(f"expected expression on line {tmp.lineno}")
        
  def _parse_single(self,itr,comms,cobjl):

    # finding command
    com = next(itr)
    #print("COMM ::",com)
    if com.type is not self.__enum.name:
      raise SyntaxError(f"not a command on line {com.lineno} [unrecognised entry]")
    for i,c in zip(comms,cobjl):
      if i and com.lexeme in i:
        model = {**i.get(com.lexeme)}
        for lu in cobjl[::-1]:
          if lu and com.lexeme in lu:
            output = self._cobjb[lu[com.lexeme]]
        break
    else:
      raise SyntaxError(f"Unrecognised command on line {com.lineno} [{com.lexeme}]") 
    params = []
    # parsing
    initi = model.pop(" initial")
    for i in initi:
      tmp = self._mergeAPEARB(itr,i,com.lineno)
      if tmp != None: params.append(tmp)

    for k,v in model.items():
      try:t = itr.peek()
      except StopIteration: t=Token(0,102,0)
      if t and t.lexeme == k:
        next(itr)
        for i in v:
          tmp = self._mergeAPEARB(itr,i)
          if tmp != None:
            params.append(tmp)
      else:
        params.extend([None]*len(v))
    return output,params,com.lineno
    
  def parse(self,text):
    tokstream = self.__lexer(text)
    return self._parse(tokstream[0],*self.APEL.buildEnv(arb=True))

  def _parse(self,tokstream,commands,cobjl):
    #print("TOKENS::",tokstream,"\nCOMMANDS::",*map(dict.keys,commands))
    itr = self.liter(tokstream)
    out = []
    try:
      while itr.list:
        obj,pars,ln = self._parse_single(itr,commands,cobjl)
        tmp = obj(*pars) ; tmp.on_Parse(self)
        tmp._lineno = ln
        out.append(tmp)
      return out
    except SyntaxError as e:
      raise SyntaxError(f"{e.msg} line {ln}")
    
  def getParser(self):
    return lambda x: self._parse(x,*self.APEL.buildEnv(*self.__ems[-1],arb=self.__am))

  def getBinding(self,title):
    binds = self.APEL.datwmtecar()[1]
    for i in binds.values():
      if title in i:
        return self._cobjb[i[title]]
    return None
  
  def getnloadModule(self,name,etp):
    # searching PATH for possible module o name
    for i in self.PATH:
      test = os.listdir(i)
      #print("Trying",i)
      for ext in [".py",".txt"]:
        #print("testing",i+name+ext,end="...")
        if name+ext in test:
          #print("success")
          path = i + name + ext          
          self.prog_load(path,etp if etp else name)
          return
        #else:
        #   print("failed")
    else:
      raise ImportError(f"Module {name} Not Found")
    
  def _load(self,code):
    ltok = self.__lexer(code)[0]
    ptok = self.getParser()(ltok)
    out = Arbiter()
    out._a_init(ptok)
    return out
# Stuff to do with actually executing code

class re_iter:
  def __init__(self,iterator,cond):
    self.__temp = iter(iterator)
    self.__cond = cond
    self.__cur = iter([])
  def __next__(self):
    try: return next(self.__cur)
    except StopIteration:
      if self.__cond():
        self.__cur = copy(self.__temp)
        return next(self)
      else:
        raise StopIteration

class Process:

  # now handling initialisations as transactions
  def _init_new(self,ntks=[]):
    self._init_tstack.append([self._init_db,self._init_tks,self._init_ind,self._init_rb])
    self._init_db = []
    self._init_tks = ntks
    self._init_ind = 0
    self._init_rb = []

  def _init_push(self):
    self._init_db,self._init_tks,self._init_ind,self._init_rb = self._init_tstack.pop()

  def releaseCurrent(self):
    self._init_db.append(self._init_ind)
  def replaceCurrent(self,code):
    self._init_rb.append((self._init_ind,code))
  def initialise(self,toks):
    self._init_new(toks)
    for self._init_ind,x in enumerate(self._init_tks):
        x.on_Init(self.arb,self) # primary initialise
    for i in self._init_db[::-1]:#clearing
      del self._init_tks[i]
    for i,c in self._init_rb[::-1]:
      #calculate offset
      pil = 0
      for o in self._init_db[::-1]:
        if o < i: break
        else:pil+=1
      tmp = self.initialise(c)
      #del self._init_tks[i+pil]
      self._init_tks = self._init_tks[:i+pil]+tmp+self._init_tks[i+pil+1:]
      
    out = self._init_tks
    self._init_push()
    return out

  # regular class code
  def registerEvent(self,name,body):
    self._events.update({name:self.initialise(body)})

  def __init__(self,arb,penv):
    self._init_tstack = []
    self._init_db,self._init_rb = [[]],[[]]
    self._init_tks = []
    self._init_ind = 0

    self.env = penv
    self.arb = arb

    self._events = {}

    #execution stuff
    self._csfeq  = 0  # for keeping track of where in the execution queue we are
    self._equeue = []
    self._astack = []

    self._esur = [] # execution stack update responses
    
    self._exec = True

  def kill(self):
    self._exec = False
    
  def _a_init(self,code):
    tmp = self.initialise(code)
    self.newprocedure(code)

  def newprocedure(self,code):
    ncb = self.initialise(code)
    self._astack.append(None)
    self._equeue.append([iter(ncb)])
    return len(self._astack) - 1

  def addprocedure(self,code,cond=None):
    if cond != None:
      self._equeue[self._csfeq].append(re_iter(code,cond))
    else:
      self._equeue[self._csfeq].append(iter(code))
  
  def _getnext(self):
    si = len(self._astack) - 1
        
    while si >= 0:
      if self._astack[si] != None: si -= 1
      else: break
    else: return None

    if si != self._csfeq:
      self._csfeq = si
      for i in self._esur:i(self)

    try:ss = self._equeue[si]
    except IndexError: return None

    while ss:
      try: return next(ss[-1])
      except StopIteration: ss.pop()
    self._equeue.pop(si)
    self._astack.pop(si)
    return self._getnext()

  def updateResponse(self,func):
    self._esur.append(func)

  def getExecIndex(self):
    return self._csfeq
  
  def currentawait(self,event):
    self._astack[self._csfeq] = event
    
  def __next__(self):
    tmp = self._getnext()
    if tmp: tmp.exec(self.arb,self)
    return self._exec

  def invoke(self,event):
    for i,x in enumerate(self._astack[:]):
      if x == event or x == "*": self._astack[i] = None
    ev = self._events.get(event,False)
    if ev: self.newprocedure(ev)

  def flush(self,ind):
    ses = self._equeue[ind]
    while ses:
      try: tmp = next(ses[-1])
      except StopIteration: ses.pop() ; continue
      else: tmp.exec(self.arb,self)
    self._equeue.pop(ind)
    self._astack.pop(ind)

class Arbiter(Process):

  def __init__(self):
    Process.__init__(self,self,{"VERSION":"proto4p"})
    self._refs = {}
    self.aout = sys.stdout
    self._procs = []
    self._adf = []

    # simple expansion
    

  def registerReference(self,name,body):
    self._refs.update({name:body})
  def registerDutyFunc(self,func):
    self._adf.append(func)
  def _invoke(self,event):
    Process.invoke(self,event)
  def invoke(self,event,scope="*"):
    if scope in ["~","_"]:
      self._invoke(event)
    else:
      self._invoke(event)
      for i in self._procs: i.invoke(event)

  def createProcess(self,ref,iev):
    if ref not in self._refs:
      raise SyntaxError(f"process reference '{ref}' doesn't exist") 
    tmp = Process(self,iev)
    self._procs.append(tmp)
    tmp._a_init(self._refs.get(ref)[:])
    tmp._from = ref
    
  def releaseDutyFunc(self):
    self._adf.remove(self._tmp)
  
  def __next__(self):
    for self._tmp in self._adf[:]:self._tmp(self)
    if self._exec:
      tmp = self._getnext()
      if tmp: tmp.exec(self,self)

    delbuff = []
    for i,x in enumerate(self._procs):
      if not next(x): delbuff.append(i)
    for i in delbuff[::-1]:
      del self._procs[i]

    return self._exec or bool(self._procs)

def run(proc,func=None):
    try:
      if func:
        func()
        while next(proc): func()
      else:
        while next(proc):pass
    except KeyboardInterrupt: print("suspended execution",file=sys.stderr)

if __name__ == "__main__":
  e = APEL()
  b = ARBITER(e)
  b.prog_load(r".\pclasses.py")
  lex = lambda x: b._ARBITER__lexer(x)[0]
  alex = lambda x:e._APEL__lexer(x)[0]
  arb = Arbiter()
  
  

  def extrc(proc):
    out = []
    for s in proc._equeue:
      tmp = []
      for i in s:
        tmp.append(list(copy(i)))
      out.append(tmp)
    return out,proc.env,proc._events

  def load(code):
    arb._a_init(b.getParser()(lex(code)))
    
    
