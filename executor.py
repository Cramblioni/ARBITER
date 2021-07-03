
# SMPL/arbiter executor
from smplparser import *

class reiter: # an iterator that loops if a condition returns True
  def __init__(self,iterator,cond):
    self.itrm,self.cond = iterator,cond
    self.__iter__() # turn this instance into an iterator
  def __iter__(self):
    if self.cond.Solve():
      self.itr = iter(self.itrm)
    else:
      self.itr = None
    return self ## return self so this object can handle reiteration
  def __next__(self):
    if self.itr == None: raise StopIteration
    try:
      return next(self.itr)
    except StopIteration:
      self.__iter__() # if the chunk finished rerun the iter function
      
def sExec(node,loc,ext,step=True):
  """executes code in an unresponsive and nonblocking way"""
  stack = [iter(node.body)] # execution stack
  while stack:
    try:
      comm = next(stack[-1]) # get next command
    except StopIteration: # unless body finished
      stack.pop() # pop code body off execution stack
      continue # move onto next cycle [handles finished execution]

    ct = type(comm)
    if ct == c_set:
      targ = comm.target.wrd
      res = comm.value.Solve()
      if comm.ext: ext.update({targ:res})
      else : loc.update({targ:res})
    elif ct == c_get:
      targ = comm.target.wrd
      sour = comm.source.wrd
      loc.update({targ:ext.get(sour)})
    elif ct == c_single:
      sExec(comm,loc,ext,False)
    elif ct == c_if:
      if comm.test.Solve():
        stack.append(iter(comm.body))
      elif comm.orelse:
        stack.append(iter(comm.orelse))
    elif ct == c_while:
      stack.append(reiter(comm.body,comm.test))
  
    if step: yield

class bExecutor:
  def __init__(self,model,ext):
    self.code = scd(model)
    self.env = {}
    self.ext = ext
    update_bank(self.code,self.env) ; self.d = 0
    self.eout = [] # this is for queing up events to be invoked elsewhere
    self.estack = [[iter(self.code.body)]] # execution stack Stores what body is being executed
    self.astack = [None] # await stack [stores if that execution level is waiting]
    self.running = True

    
  def _pushex(self,code,ind=-1):
    self.estack[ind].append(code)

  def _newex(self,code):
    self.estack.append([code])
    self.astack.append(None)

  def _popex(self,ind): # pops from estack and returns if that block still exists
    self.estack[ind].pop()
    if len(self.estack[ind]) == 0:
      self.estack.pop(ind)
      self.astack.pop(ind)
      return False
    else: return True
      
  def _await(self,event,ind=-1):
    self.astack[-1] = event

  def _invoke(self,event):
    for i,v in enumerate(self.astack[:]):
      if v == event or v == "*": self.astack[i] = None
    if event in self.code.event:
      self._newex(iter(self.code.event.get(event)))
      
  def _getone(self):
    ind = len(self.estack) - 1
    if ind == -1: return None
    while self.astack[ind]!=None:
      if ind == -1: return None
      ind -= 1
    else:
      pr = True
      while pr:
        try:
          return next(self.estack[ind][-1])
        except StopIteration:
          pr = self._popex(ind)
        else: self.d = ind
      else:
        return False

  def _getnext(self):
    tmp = self._getone()
    while tmp == False: tmp = self._getone()
    else: return tmp

  def _extr(self,node):return True # overwrite this function for some nice yeeting
  def intrp(self,node):
    if self._extr(node):
      ct = type(node)
      if ct == c_set:
        trg = node.target.wrd
        val = node.value.Solve()
        if node.ext: self.ext.update({trg:val})
        else: self.env.update({trg:val})
      if ct == c_get:
        src = node.source.wrd
        trg = node.target.wrd
        self.env.update([[trg,self.ext.get(src)]])
      if ct == c_if:
        if node.test.Solve():
          self._pushex(iter(node.body),self.d)
        elif node.orelse:
          self._pushex(iter(node.orelse),self.d)
      if ct == c_await:
        self._await(node.id)
      if ct == c_invoke:
        eid = node.id
        scope = node.scope
        if scope == 3: #local
          self._invoke(eid)
        else:
          self.eout.append(node)
      if ct == c_while:
        cond = node.test
        self._pushex(reiter(node.body,cond),self.d)
      if ct == c_single:
        ## create a new execution block and keep a reference to this one
        tmp = self.d
        self._newex(iter(node.body)); sb = self.estack[-1]
        self.d = -1
        ## now force execute the entire code body
        while sb:
          try:
            n = next(sb[-1])
          except StopIteration:
            sb.pop()
          else: self.intrp(n)
        self.astack.pop() ; self.estack.pop() # remove any evidence
        self.d = tmp # pretend this never happened
      if ct == c_end:
        self.running = False
      if ct == c_print:
        print(*map(lambda x:x.Solve(),node.msg))

  def __next__(self):
    n = self._getnext()
    if n != None:
      self.intrp(n)
    return self.running

class aExecutor(bExecutor):
  def __init__(self,model):
    mab = c_bank(model.body,model.event) # to stop errorororororors
    bExecutor.__init__(self,mab,None)
    self.procs = []
    self.banks = model.banks

  def _extr(self,node):
    ct = type(node)
    if ct == c_create:
      self.procs.append(bExecutor(self.banks.get(node.bid.wrd),self.env))
      return False
    return True

  def __next__(self):
    
    n = self._getnext()
    if n != None: self.intrp(n)

    delb = []
    for i,p in enumerate(self.procs):
      if not next(p): delb.append(i)
      self.eout.extend(p.eout)
      p.eout.clear()
      
    for i in delb[::-1]: self.procs.pop(i)
    oevs = []
    for i in self.eout:
      if i.scope == 2:
        #print(i.id)
        self._invoke(i.id)
      else:
        oevs.append(i.id)
    for i in set(oevs):
      for p in self.procs: p._invoke(Name(i))

    self.eout.clear()
    
    return self.running or len(self.procs) > 0
  
