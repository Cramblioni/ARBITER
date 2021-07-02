
## a Simple python script that takes *.txt files and
## executes them as ARBITER code, printing out every
## variable space that's in use
import argparse as ap

from executor import *

pr = ap.ArgumentParser(description="Executes ARBITER script")
pr.add_argument("sdir",metavar="F",type=str,help="the directory of the ARBITER script")
pr.add_argument("-X",dest="ooae",action="store_const",const=False,default=True,help="only print enviroment after execution(default:print enviroment after every step")

def envdmp(env):
  "dumps out python dicts in a \"nicer\" fashion"
  return ", ".join(map(lambda x:"{} = {}".format(*x),env.items()))

def main():
  global sdir,ooae
  with open(sdir,"rb") as f:
    prog = f.read().decode("utf8")
    #print(prog)
  try:
    exe,_ = aParse(lexer(prog))
  except Exception as e:
    import traceback
    traceback.print_exc()
  else:
    arb = aExecutor(exe)
    while next(arb):
      if ooae:
        print(envdmp(arb.env),
              *map(envdmp,[i.env for i in arb.procs]),"",
              sep="\n\t")
    print(envdmp(arb.env),
          *map(envdmp,[i.env for i in arb.procs]),"",
          sep="\n\t")

if __name__ == "__main__":
  globals().update(ns:=pr.parse_args().__dict__)
  #print(ns)
  main()
