#!/usr/bin/env python

import sys
sys.path.append('../..')
import base
import os

def make():
  print("[fetch & build]: brotli")
  # Run through the interpreter rather than the .py file association, which on
  # Windows can resolve to a different (or stub) Python than the build's.
  base.cmd_in_dir(base.get_script_dir() + "/../../core/Common/3dParty/brotli", "python", ["./make.py"])
  return

if __name__ == '__main__':
  # manual compile
  make()
