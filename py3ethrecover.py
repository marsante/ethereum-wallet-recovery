#!/usr/bin/python
from __future__ import print_function
from keys import decode_keystore_json
from joblib import Parallel, delayed

import json
import itertools
import sys
import os
import getopt
import traceback
import multiprocessing
import time
import string   
import argparse

maxcore=multiprocessing.cpu_count()
numbercore=maxcore
parser = argparse.ArgumentParser()  
group = parser.add_mutually_exclusive_group(required=True)                                             
parser.add_argument("-p", "--wallet", type=str, required=True, help="Keystore file")
parser.add_argument("-v", "--core", type=int, required=False, help="count core")
group.add_argument("-w", "--wordlist", type=str, required=False, help="Wordlist file")
group.add_argument("-b", "--brute", type=str, required=False, help="numbers / lowercase / uppercase / ASCII")
parser.add_argument("-d", "--length", type=int, required=False, help="length of repeating characters")
parser.add_argument("-k", "--endfile", type=str, required=False, help="ending file")
parser.add_argument("-z", "--startfile", type=str, required=False, help="starting file")
args = parser.parse_args()        

if args.brute is not None:
    k=1
    if args.length is not None:
        k = args.length
    else:
        k = 1
    l = args.brute
    if args.brute == "ascii" or args.brute == "ASCII":
        print ("Use entire ASCII table")
        l = string.printable
        print (l)
    z = []
    for s in range(k):
        a = [i for i in l]
        for y in range(s):
            a = [x+i for i in l for x in a]
        z = z+a

if args.core is not None:
    numbercore = args.core

if args.wordlist is not None:
    wordlist=args.wordlist
    with open(wordlist) as f:
        dictlist = f.read().splitlines()

if args.endfile is not None:
    ending = args.endfile
    with open(ending) as k:
        atend = k.read().splitlines()

if args.startfile is not None:
    starting = args.startfile
    with open(starting) as d:
        atstart = d.read().splitlines()


with open(args.wallet) as fd:
     json_data = json.load(fd)

grammar=['']

if args.startfile is not None and args.endfile is not None and args.wordlist is not None:
  grammar=[atstart, dictlist, atend]
elif args.startfile is not None and args.endfile is not None and args.brute is not None:
  grammar=[atstart, z, atend]
elif args.startfile is not None and args.wordlist is not None:
  grammar=[atstart, dictlist]
elif args.startfile is not None and args.brute is not None:
  grammar=[atstart, z]
elif args.startfile is not None and args.endfile is not None:
  grammar=[atstart, atend]
elif args.endfile is not None and args.wordlist is not None:
  grammar=[dictlist, atend]
elif args.endfile is not None and args.brute is not None:
  grammar=[z, atend]
elif args.brute is not None:
  grammar=[z]
elif args.wordlist is not None:
  grammar=[dictlist]

time1 = time.time()
w = json_data
print ("Processing wallet: ", w["address"])

def generate_all(el, tr):
    
    if el:
        for j in range(len(el[0])):
            for w in generate_all(el[1:], tr + el[0][j]):
                yield w
    else:
        yield tr

pwds = []
pwds = itertools.chain(pwds, generate_all(grammar,''))
pwds = sorted(pwds, key=len)
n_pws = len(list(pwds))

def attempt(w, pw):
    sys.stdout.flush()
    counter.increment()
    howlong=time.time() - time1
    cas="\t%.2f sec \t\t" % howlong
        
    print (counter.value, "\t", n_pws-counter.value, cas, [pw])
        
    try:
        o = decode_keystore_json(w,pw)
      
      
        print (
            """\n\n*************************\nPassword found:\n"%s"\n*************************\n\n""" % pw)
        f = open("passwordfound.txt",'w')
        f.write("""\n\n*************************\nPassword found:\n"%s"\n*************************\n\n""" % pw)
        f.close()
        os.system("killall python")
        try:
            os.system("killall python")
        except SystemExit as e:
            sys.exit(e)
        except:
            raise
   
    except ValueError as e:
        return ""
                
class Counter(object):
    def __init__(self):
        self.val = multiprocessing.Value('i', 0)

    def increment(self, n=1):
        with self.val.get_lock():
            self.val.value += n

    @property
    def value(self):
        return self.val.value

def __main__():  
    global counter
    counter = Counter()
    try:
        Parallel(n_jobs=numbercore, backend = 'multiprocessing', batch_size=1, pre_dispatch=numbercore, verbose=0)(delayed(attempt)(w, pw) for pw in pwds)
        print ("Done")
        
    except Exception as e:
        try:
            print ("\n\n")
            print (e)
            print ("Error!")
        except SystemExit as e:                                                   
            sys.exit(e)
        except:
            raise


if __name__ == "__main__":
    __main__()
