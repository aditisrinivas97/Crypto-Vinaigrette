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

# Generates a polynomial with the given parameters
def generate_polynomial(vl, ol, coefficients, vinegars, y):

    polynomial = [[0] * (vl + ol) for i in range(ol + vl)]

    for i in range(vl):
        for j in range(vl):
            polynomial[i][j] = coefficients['alphas'][i][j] * vinegars[i] * vinegars[j]
    
    for i in range(vl):
        for j in range(vl, vl + ol):
            polynomial[i][j] = coefficients['betas'][i][j] * vinegars[i]

    flattened_polynomial = [0] * (vl + ol)
    
    for i in range(vl + ol):
        for j in range(vl + ol):
            if i < vl and j < vl:
                flattened_polynomial[0] += polynomial[i][j]
            else:
                if i >= vl :
                    flattened_polynomial[i] += polynomial[i][j]
                if j >= vl :
                    flattened_polynomial[j] += polynomial[i][j]

    for i in range(vl + ol):
        flattened_polynomial[i] += coefficients['gammas'][0][i]

    flattened_polynomial = [sum(flattened_polynomial[0:vl])] + flattened_polynomial[vl:]

    flattened_polynomial[0] -= y

    flattened_polynomial[0] += coefficients['etas'][0]

    return (flattened_polynomial, list(range(ol, ol + ol)))

# Solves a set of linear equations given in polynomials
def solve(polynomials, variables):

    eqn_var = list()
    eqn_con = list()

    for eqn in polynomials:
        print("EQN : ", eqn)
        eqn_var.append(eqn[1:])
        eqn_con.append(-eqn[0])
    
    print()
    
    sol = []

    try:
        sol = np.linalg.solve(np.array(eqn_var), np.array(eqn_con))
    except:
        return sol

    return sol

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

y = (6, 2, 0, 5)

# Components of public key
coeff_quadratic = list()
coeff_singular = list()
coeff_scalars = list()

v = [2, 4, 6]   # Remove after generation of y is done
'''
while True : 
    if len(v) == u :
        v.sort()
        v[-1] = n 
        break

    rnum = generate_random_element(k)

    if rnum not in v and rnum != n:
        v.append(rnum)
'''
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

    ol = v[_i + 1] - v[_i]

    F_layers.append(list())

    for i in range(ol):
        F_layers[-1].append(dict())
        layer = F_layers[-1][-1]
        
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

no_solution = True

while no_solution:

    no_solution = False

    vinegar_vars = list()   # Random vinegar variables

    for i in range(v[0]):
        vinegar_vars.append(generate_random_element(k))

    ycount = 0
    pcount = 0
    olcount = 0

    polynomials = list()

    for _i in range(v[0], n):  # Number of polynomials in the central map

        vl = -1         # Number of vinegar variables in current layer
        ol = -1         # Number of oil variables in current layer
        layer = -1      # Layer number

        for i in range(1, len(v)):
            if _i <= v[i] :
                ol = v[i] - v[i - 1]
                vl = v[i - 1]
                layer = i - 1 
                break

        p, variables = generate_polynomial(vl, ol, F_layers[layer][olcount], vinegar_vars, y[ycount])

        polynomials.append(p)

        pcount += 1

        if len(variables) == pcount:
            res = solve(polynomials, variables)
            
            if len(res) == 0:
                no_solution = True
                break

            for x in res:
                vinegar_vars.append(x)
            
            polynomials = list()
            pcount = 0
            olcount = 0          
        else:
            olcount += 1

        ycount += 1

print("Vinegars for each layer (v) : ", v)
print("Solution : ", vinegar_vars)

            
