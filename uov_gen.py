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

    if rnum not in v and rnum != n:
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

for i in range(L1_dimensions):
    b1.append(generate_random_element(k))
            

# -------------------- Generating L2 -------------------- #

L2_dimensions = v[u - 1] - v[0]
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

for i in range(L2_dimensions):
    b2.append(generate_random_element(k))

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

central_map = list()        # Holds the central map i.e the public key information

no_solution = True

print(F_layers)

while no_solution :

    print("Starting")

    no_solution = False

    vinegar_vars = list()   # Random vinegar variables

    for i in range(v[0]):
        vinegar_vars.append(generate_random_element(k))

    print("vins :", vinegar_vars)

    for layer in range(u - 1):

        vl = v[layer]
        ol = v[layer + 1] - v[layer]

        for o in range(ol):

            p = [[0] * (vl + o) for i in range(vl + o)]

            for i in range(vl):         # Multiply alphas
                for j in range(vl):
                    p[i][j] += F_layers[layer]['alphas'][i][j] * vinegar_vars[i] * vinegar_vars[j]

            for i in range(vl):         # Multiply betas
                for j in range(vl, vl + o):
                    p[i][j] += F_layers[layer]['betas'][i][j] * vinegar_vars[i]
            
            central_map.append(p)

        print("c", central_map)

        equations = [[0] * (ol + vl) for i in range(ol)]
            
        for i in range(ol):
            for j in range(vl + i):
                for l in range(vl + i):
                    if j < vl and l < vl :
                        equations[i][0] += central_map[-ol+i][j][l]
                    else :
                        if j > vl :
                            equations[i][j] += central_map[-ol+i][j][l]
                        elif l > vl :
                            equations[i][k] += central_map[-ol+i][j][l]
                if j < vl :
                    equations[i][0] += F_layers[layer]['gammas'][0][j] * vinegar_vars[j]
                else:
                    equations[i][j] += F_layers[layer]['gammas'][0][j]

        print("eqn =", equations)
        
        np_eqn = [0 for i in range(ol)]
        np_const = [0 for i in range(ol)]

        for e in range(len(equations)):
            np_eqn[e] = equations[e][-ol:]
            np_const[e] = equations[e][0] + F_layers[layer]['etas'][0]
        
        ans = list()

        print("NP", np_eqn, np_const)
        
        try :
            ans = np.linalg.solve(np_eqn, np_const)

        except :
            central_map = list()
            no_solution = True
            break

        print("ans =", ans)
        
        for a in ans :
            vinegar_vars.append(a)

print("v", v)
print("L1", L1)
print("L2", L2)
print("Vinegar vars : ", vinegar_vars)
print("Central map : ", central_map)
            
