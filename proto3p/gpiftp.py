
# General Programming Interface For Testing Purposes GPIFTP

import tkinter as tk
from parserg import *

#globals
ARB_EXE = None

#setup
print(sys.version)


root = tk.Tk()
root.resizable(False,False)
uie = tk.Text(root,width=60,height=30,borderwidth=2)
uie.grid(row=1,column=0,rowspan=10,sticky=tk.NSEW,padx=(2,2))

uie.insert(0.0,"print \"Hello, World!\"\nend")

uoe = tk.Text(root,width=60,height=10,borderwidth=2)
uoe.grid(row=8,column=1,rowspan=3,sticky=tk.NSEW,padx=(2,2))

class empt:pass

iout = empt() ; iout.write=lambda x,*args: uoe.insert('end',x,*args)
iout.clear = lambda:uoe.delete(0.0,'end')


def prep():
  global ARB_EXE,backend
  iout.clear()
  prog = uie.get(0.0,'end')
  prog_l = a_lexer(prog)
  print("Lexing succesful",file=iout)
  backend = Backend()
  parser = backend.getParser()
  prog_p = parser(prog_l)
  print("Parsing successful",file=iout)
  ARB_EXE = ARBITER(prog_p,backend)
  print("",file=iout)
  

tk.Button(root,text="run",command=prep).grid(row=1,column=1)

if __name__ == "__main__":
  while True:
    try:
      root.update()
      root.update_idletasks()
    except tk.TclError: break
    else:
      if ARB_EXE != None:
        tmp = next(ARB_EXE)
        print(ARB_EXE.aout.cont,end="",file=iout)
        ARB_EXE.aout.cont = ""
        if not tmp:
          ARB_EXE = None
          print("\nfinished execution",file=iout)
