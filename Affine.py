'''
Generate an invertible Affine function.
'''

# -------------------- Imports -------------------- #
import secrets, dill
from multiprocessing import Process, Pipe
from datetime import datetime as dt
from GF256 import *

# -------------------- Module -------------------- #
class Affine:
    def __init__(self, m, k, seed=666, verbosity=False):
        self.m = int(m)
        self.n = int(m)
        self.k = int(k)
        self.seed = secrets.randbelow(seed)
        self.verbosity = verbosity

    def generator(m, n, k, endPoint):
        import secrets, dill, numpy as np
        from numpy.linalg import LinAlgError

        try:
            m = int(m)
            n = int(n)
            k = int(k)
        except ValueError as e:
            print("M, N, and K must be integers!")

        iters = 0
        while True:
            l = list()
            for i in range(m):
                l.append(list())
                for j in range(n):
                    l[-1].append(GF256.get())
            
            try:
                linv = GF256.find_inverse(l)
                #print("tried : ",linv)
                break
            except Exception as e:
                iters += 1
                if iters % 100000 == 0:
                    print(iters, "done")
                pass
                
        b = list()
        for i in range(m):
            b.append(GF256.get())

        ret = dict()
        ret['l'] = l
        ret['linv'] = linv
        ret['b'] = b

        endPoint.send(dill.dumps(ret))
        exit(0)
    
    def start_generators(self, n):
        '''
        Use `n` subprocesses to generate a random affine function.
        ''' 
        self.children = list()
        self.parentEnds = list()
        self.childEnds = list()
        for c in range(n):
            parentEnd, childEnd = Pipe()
            p = Process(target=Affine.generator, args=(self.m, self.n, self.k, childEnd))
            self.children.append(p)
            self.parentEnds.append(parentEnd)
            self.childEnds.append(childEnd)
            p.start()
            if self.verbosity:
                print("L Worker started with PID :", p.pid)

    def retrieve(self):
        '''
        Retrieves the affine function from the first worker found to have completed!
        '''
        done = -1
        tries = 0
        while done == -1:
            for c in range(len(self.children)):
                if self.parentEnds[c].poll(timeout=1):
                    done = c
                    break
            tries += 1

        ret = dill.loads(self.parentEnds[done].recv())

        for c in self.children:
            c.terminate()

        return ret


if __name__ == '__main__':
    for i in range(2, 100):
        start = dt.now()
        a = Affine(i, 128)
        a.start_generators(5)
        a = a.retrieve()
        end = dt.now()
        print(i, end-start)
        