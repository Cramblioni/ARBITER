

# ARBITER but in the command prompt
import argparse as ap

from core import *

pr = ap.ArgumentParser(description="Executes ARBITER script")
pr.add_argument("sdir",metavar="F",type=str,help="the directory of the ARBITER script")
pr.add_argument("-X",dest="ooae",action="store_const",const=False,default=True,help="only print enviroment after execution(default:print enviroment after every step")



if __name__ == "__main__":
  APELENV = APEL()
  backend = ARBITER(APELENV)
  backend.prog_load(r".\pclasses.py")

  globals().update(pr.parse_args().__dict__)
  #print(ns)
  with open(sdir) as f: 
    arb = backend._load(f.read())
  if ooae: run(arb)
  else: run(arb,lambda:print(arb.env,
    *map(lambda x:x.env,arb._procs),sep="\n\t"))
  
