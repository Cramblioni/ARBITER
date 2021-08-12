
from enum import Enum
from dataclasses import dataclass
import re

@dataclass()
class Token:
  type:object
  lexeme:str
  lineno:int
  

class Lexer:
  def __init__(self):
    self.__rules = {}
    self.__skips = []
    self.__cc = None
    self.__lbs = False
  @property
  def linebreaks(self): return self.__lbs
  @linebreaks.setter
  def linebreaks(self,val): self.__lbs = val
  @property
  def skips(self):
    return self.__skips
  @skips.setter
  def skips(self,rule):
    self.__skips.append(rule)
  @property
  def rules(self):
    return self.__rules
  @rules.setter
  def rules(self,value):
    if isinstance(value,dict):
      self.__rules.update(value)
    elif isinstance(value,tuple):
      self.__rules.update([value])
    else: raise TypeError("Rules should be either a tuple or dict")

    self.__enum = Enum("Lexer",list(self.__rules.keys())+(["EOL"] if self.__lbs else []))

  @property
  def enum(self): return self.__enum

  def __call__(self,txt):
    enum=self.__enum
    out,lineno = [],1
    for i in self.__skips:
          txt = re.sub(i,"",txt,flags=re.DOTALL | re.MULTILINE | re.S)
    while txt:
      if txt[0] == "\n":
        lineno += 1
        txt = txt[1:]
        if self.__lbs: out.append(Token(enum.EOL,"EOL",lineno-1))
        continue
      elif txt[0] in " \t":
        txt = txt[1:]
        continue
      else:   
          for r,t in self.__rules.items():
            tst = re.match(t,txt)
            if tst:
              _,e = tst.span()
              lexeme = txt[:e]
              txt = txt[e:]
              out.append(Token(enum[r],lexeme,lineno))
              break
            else:
              continue
          else: raise SyntaxError(f"Unrecognised token '{txt}'")
    return out,enum

