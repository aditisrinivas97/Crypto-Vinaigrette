# -------------------- IMPORTS and Definitions -------------------- #
import secrets, argparse, numpy as np

# Generate non zero random numbers below k
def generate_random_element(k) :
    num = secrets.randbelow(k)
    while not num :
        num = secrets.randbelow(k)
    return num

# Generate 2D matrix with random elements below k
def generate_random_matrix(x, y, k) :
    mat = [[0] * y for i in range(x)]
    for i in range(x) :
        for j in range(y):
            mat[i][j] = generate_random_element(k)
    return mat

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

n = 6        
u = 3                   # number of layers
k = 7                   # finite space of elements

# Components of public key
coeff_quadratic = list()
coeff_singular = list()
coeff_scalars = list()

while True : 
    if len(v) == u :
        v.sort()
        v[-1] = n 
        break

    rnum = generate_random_element(k)

    if rnum not in v :
        v.append(rnum)
    
# -------------------- Generating L1 -------------------- #

L1_dimensions = v[u - 1] - v[0]
while True:
    for i in range(L1_dimensions):
        L1.append(list())
        for j in range(L1_dimensions):
            L1[-1].append(generate_random_element(k))
    
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
            L2[-1].append(generate_random_element(k))
    
    try:
        L2inv = np.linalg.inv(L2)
        break
    except:
        del L2
        L2 = list()


# -------------------- Generating F -------------------- #

for _i in range(u - 1):
    
    F_layers.append(dict())
    layer = F_layers[-1]
    
    layer['alphas'] = list()
    layer['betas'] = list()
    layer['gammas'] = list()
    layer['etas'] = list()

    alphas = generate_random_matrix(v[_i], v[_i], k)
    betas = generate_random_matrix(v[_i + 1], v[_i + 1] , k)
    gammas = generate_random_matrix(1, v[_i + 1], k)
    etas = generate_random_element(k)

    for i in range(v[_i + 1]):
        for j in range(v[_i + 1]):
            if i >= v[_i] or j < v[_i]:
                betas[i][j] = 0
    
    layer['alphas'] = alphas
    layer['betas'] = betas
    layer['gammas'] = gammas
    layer['etas'] = [etas]

# --------------- Construction of central map --------------- #

m = n - v[0]            # Number of polynomials in the central map

vinegar_vars = list()   # Random vinegar variables

central_map = list()    # Holds the central map i.e the public key information
