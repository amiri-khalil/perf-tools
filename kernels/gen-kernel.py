#!/usr/bin/env python2
# generate C-language kernels with ability to incorporate x86 Assembly with certain control-flow constructs
# Author: Ahmad Yasin
# edited: Oct. 2020
__author__ = 'ayasin'
__version__ = 0.2

import argparse, sys

INST_UNIQ='PAUSE'
INST_1B='NOP'

ap = argparse.ArgumentParser()
ap.add_argument('-n', '--num', type=int, default=3)
ap.add_argument('-i', '--instruction', nargs='+', default=[INST_UNIQ])
ap.add_argument('-a', '--align' , type=int, default=0, help='in power of 2')
ap.add_argument('-o', '--offset', type=int, default=0)
ap.add_argument('mode', nargs='?', choices=['basicblock', 'jumpy'], default='basicblock')
args = ap.parse_args()

def asm(x, tabs=1, spaces=8):
  print ' '*spaces + 'asm("' + '\t'*tabs + x + '");'

print "// Auto-generated by %s's %s version %s invoked with:\n//  %s .\n"%(__author__, sys.argv[0].replace('./',''), str(__version__), str(args).replace('Namespace', '')) + """// Do not modify!
//
#include <stdio.h>
#include <stdlib.h>
int main(int argc, const char* argv[])
{
    long i,n;
    if (argc<2) {
        printf("%s: missing <num-iterations> arg!\\n", argv[0]);
        exit(-1);
    }
    n= atol(argv[1]);"""
asm(INST_UNIQ, spaces=4)
print "    for (i=0; i<n; i++) {"

for j in range(args.num):
  if args.offset:
     for k in range(j+args.offset-1): asm(INST_1B)
  if args.mode == 'jumpy': asm('Lbl%03d:'%j, tabs=0)
  for inst in args.instruction:
    if inst == 'JMP': inst += ' Lbl%03d'%(j+1)
    asm(inst)
  if args.align: asm('.align %d'%(2 ** args.align), tabs=0)
if args.mode == 'jumpy': asm('Lbl%03d:'%args.num, tabs=0)

print """    }
    return 0;
}"""

