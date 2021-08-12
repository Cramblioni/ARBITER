

# ARBITER but in the command prompt
import argparse as ap

from core import *

pr = ap.ArgumentParser(description="Executes ARBITER script")
pr.add_argument("sdir",metavar="F",type=str,help="the directory of the ARBITER script")
pr.add_argument("-X",dest="ooae",action="store_const",const=False,default=True,help="only print enviroment after execution(default:print enviroment after every step")



if __name__ == "__main__":
  e = APEL()
  b = ARBITER(e)
  b.prog_load(r".\pclasses.py")
  lex = lambda x: b._ARBITER__lexer(x)[0]
  alex = lambda x:e._APEL__lexer(x)[0]
  arb = Arbiter()
  
  def run(proc):
    try:
      while next(proc):pass
    except KeyboardInterrupt: print("suspended execution",file=sys.stderr)

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
    

  globals().update(ns:=pr.parse_args().__dict__)
  #print(ns)
  with open(sdir) as f: load(f.read())
  run(arb)
  
