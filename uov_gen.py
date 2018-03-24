# -------------------- IMPORTS and Definitions -------------------- #
import secrets, argparse, numpy as np

def generator(nbits):
    '''Returns a random integer of size nbytes '''
    gen = secrets.randbits(nbits)
    while not gen:
        gen = secrets.randbits(nbits)
    return gen

# -------------------- Command Line Arguements -------------------- #
parser = argparse.ArgumentParser(description='Asymmetric key generation using Unbalanced Oil and Vinegar Scheme.')

'''parser.add_argument('message_file', type=str,
                    help='File containing the message to encrypt.')'''
parser.add_argument('-v', action="store_true",
                    help='Verbose output.')
parser.add_argument('-vv', action="store_true",
                    help='Very verbose output.')

args = parser.parse_args()

if args.vv :
    args.v = True

'''
# -------------------- Retrieve Message -------------------- #
with open(args.message_file, 'r') as file:
    message = file.read()
'''

# -------------------- Parameters for Rainbow Scheme -------------------- #
L1 = list()
L1inv = None
b1 = list()

L2 = list()
L2inv = None
b2 = list()

# Components of F
F_layers = list()
v = list()              # vinegar layers

n = 33          
u = 5           # number of layers


# Components of public key
coeff_quadratic = list()
coeff_singular = list()
coeff_scalars = list()


nbits = len("{0:b}".format(n)) - 1
tries = 0

if args.vv:
    print("nbits =", nbits)

while True:
    _nbits = nbits - 1
    v.append(generator(nbits))

    for i in range(u-1):
        v.append(v[-1] + generator(_nbits))
        _nbits -= 1
        if v[-1] > n:
            break
    
    if v[-1] <= n:
        v[-1] = n
        break
    else:
        del v
        v = list()
        tries += 1
        if tries == 100:
            print("N might be too small, could not generate vector in 100 tries!")
            break

if args.v:
    print("tries =", tries, "\nv =", v)


# -------------------- Generating L1 -------------------- #
L1_dimensions = v[u - 1] - v[0]
while True:
    for i in range(L1_dimensions):
        L1.append(list())
        for j in range(L1_dimensions):
            L1[-1].append(generator(32))
    
    try:
        L1inv = np.linalg.inv(L1)
        break
    except:
        del L1
        L1 = list()


# -------------------- Generating L2 -------------------- #
L2_dimensions = v[u - 1]
while True:
    for i in range(L2_dimensions):
        L2.append(list())
        for j in range(L2_dimensions):
            L2[-1].append(generator(32))
    
    try:
        L2inv = np.linalg.inv(L2)
        break
    except:
        del L2
        L2 = list()


# -------------------- Generating F -------------------- #
for _i in range(u-1):
    F_layers.append(dict())
    layer = F_layers[-1]
    
    layer['alphas'] = list()
    layer['betas'] = list()
    layer['gammas'] = list()
    layer['etas'] = list()

    # oi is number of polynomials
    oi = v[_i + 1] - v[_i]
    for k in range(oi):
        layer['alphas'].append(list())
        layer['betas'].append(list())
        layer['gammas'].append(list())

        # alphas
        for i in range(oi):
            layer['alphas'][-1].append(list())
            for j in range(v[_i]):
                layer['alphas'][-1][-1].append(generator(32))

        # betas
        for i in range(v[_i]):
            layer['betas'][-1].append(list())
            for j in range(v[_i]):
                layer['betas'][-1][-1].append(generator(32))

        # gammas
        for i in range(v[_i+1]):
            layer['gammas'][-1].append(generator(32))

        # etas
        layer['etas'].append(generator(32))


# -------------------- Generating Public Key -------------------- #
