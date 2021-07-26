
# ARBITER proto3p bootstrapper
import argparse as ap
from parserg import *
pr = ap.ArgumentParser(description="Executes ARBITER script")
pr.add_argument("sdir",metavar="F",type=str,help="the directory of the ARBITER script")


def main():
  global sdir,backend
  with open(sdir,"r") as f:
    prog_t = f.read()

  prog_ts = a_lexer(prog_t)
  backend = Backend()
  sparser = backend.getParser()
  prog_p = sparser(prog_ts)

  Arbiter = ARBITER(prog_p,backend)

  while next(Arbiter):
    Arbiter.aout.print()
    

if __name__ == "__main__":
  globals().update(ns:=pr.parse_args().__dict__)
  #print(ns)
  main()
