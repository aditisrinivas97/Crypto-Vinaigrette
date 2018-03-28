# -------------------- IMPORTS -------------------- #
import dill, os, secrets, numpy as np, sys


# -------------------- Generate Random Invertible Matrix -------------------- #

with open(sys.argv[1], 'rb') as pfile:
    params = dill.load(pfile)
    for p in params:
        globals()[p] = params[p]

while True:
    L = generate_random_matrix(dim, dim, k)

    try:
        Linv = np.linalg.inv(L)
        break
    except:
        pass


# -------------------- Dump Matrices to File -------------------- #

with open(os.path.abspath('.') + '/.dat/l' + sys.argv[2], 'wb') as wfile:
    Ls = [L, Linv]
    dill.dump(Ls, wfile)