# -------------------- IMPORTS and Definitions -------------------- #
import secrets, argparse, numpy as np
import dill, errno, os, subprocess as sp, atexit
from Affine import *


# exit handler, cleans up things
def cleanup_atexit(config):
    print("Cleaning up...")
    LPath = os.path.dirname(config.datpath)

    for lf in config.spawn:
        if config.generators[lf].poll() == None:
            try:
                config.generators[lf].terminate()
                os.remove(LPath + '/l' + str(lf))
            except Exception as e:
                print("Exception", e)
                pass
    print("Done...")


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

# Generate vinegar variables for 'u' layers where the last layer has 'n' vinegars
def generate_vinegars(u, n):
    ret = list()

    while True : 
        if len(ret) == u :
            ret.sort()
            ret[-1] = n
            break

        rnum = generate_random_element(n)

        if rnum not in ret and rnum != n:
            ret.append(rnum)

    return ret

# Generates Y or the set of targets
def generate_targets(message, v, n):

    ret = list()

    parts = n - v[0]          # Number of parts to split message into
    part = len(message) // (parts + 1)      # Length of each part
    part += 1

    k = 0
    for i in range(parts):
        yPart = 0
        for j in range(part):
            try:
                yPart = yPart | ord(message[k])
                k += 1
            except IndexError:
                ret.append(yPart)
                break
        ret.append(yPart)

    return ret

# Generate F - coefficients below 'k' for every polynomial 
def generate_coefficients(u, v, k):

    ret = list()

    for _i in range(u - 1):

        ol = v[_i + 1] - v[_i]

        ret.append(list())

        for i in range(ol):
            ret[-1].append(dict())
            layer = ret[-1][-1]
            
            layer['alphas'] = list()
            layer['betas'] = list()
            layer['gammas'] = list()
            layer['etas'] = list()

            alphas = generate_random_matrix(v[_i], v[_i], k)
            betas = generate_random_matrix(v[_i + 1] - v[_i], v[_i] , k)
            gammas = generate_random_matrix(1, v[_i + 1], k)
            etas = generate_random_element(k)

            layer['alphas'] = alphas
            layer['betas'] = betas
            layer['gammas'] = gammas
            layer['etas'] = [etas]
    
    return ret

# Generates a polynomial for the map F 
def generate_polynomial(vl, ol, pcount, coefficients, polynomial, config):

    # Composition of F and L2
    for _i in range(ol):

        # Multiply Alphas
        for i in range(vl):
            for j in range(vl):
                temp = np.multiply(coefficients[_i]['alphas'][i][j], config.L2[i])
                polynomial.quadratic[pcount + _i] = (np.add(np.array(polynomial.quadratic[pcount + _i]), np.multiply((np.array(temp)).reshape(config.n, 1), (np.array(config.L2[j])).reshape(1, config.n)))).tolist()
                temp = np.multiply(config.b2[j], temp)
                polynomial.linear[pcount + _i] = (np.add(temp, polynomial.linear[pcount + _i])).tolist()
                temp = np.multiply(coefficients[_i]['alphas'][i][j], config.L2[j])
                temp = np.multiply(config.b2[i], temp)
                polynomial.linear[pcount + _i] = (np.add(temp, polynomial.linear[pcount + _i])).tolist()     
                temp = coefficients[_i]['alphas'][i][j] * config.b2[i]
                polynomial.constant[pcount + _i] += temp * config.b2[j]

        # Multiply Betas    
        for i in range(ol):
            for j in range(vl):
                temp = np.multiply(coefficients[_i]['betas'][i][j], config.L2[i + vl])
                polynomial.quadratic[pcount + _i] = (np.add(np.array(polynomial.quadratic[pcount + _i]), np.multiply((np.array(temp)).reshape(config.n, 1), (np.array(config.L2[j])).reshape(1, config.n)))).tolist()
                temp = np.multiply(config.b2[j], temp)
                polynomial.linear[pcount + _i] = (np.add(temp, polynomial.linear[pcount + _i])).tolist()
                temp = np.multiply(coefficients[_i]['betas'][i][j], config.L2[j])
                temp = np.multiply(config.b2[i + vl], temp)
                polynomial.linear[pcount + _i] = (np.add(temp, polynomial.linear[pcount + _i])).tolist()
                temp = coefficients[_i]['betas'][i][j] * config.b2[i + vl]
                polynomial.constant[pcount + _i] += temp * config.b2[j]
        
        # Multiply Gammas    
        for i in range(vl + ol):
            temp = np.multiply(coefficients[_i]['gammas'][0][i], config.L2[i])
            polynomial.linear[pcount + _i] = (np.add(temp, polynomial.linear[pcount + _i])).tolist()
            polynomial.constant[pcount + _i] += coefficients[_i]['gammas'][0][i] * config.b2[i]
        
        # Add Eta
        polynomial.constant[pcount + _i] += coefficients[_i]['etas'][0]
    
    # Composition of L1 and F * L2
    temp_quadratic = [[[0] * config.n for i in range(config.n)] for j in  range(config.n - config.v[0])]
    temp_linear = [[0] * config.n for i in range(config.n - config.v[0])]
    temp_constant = [0] * (config.n - config.v[0])

    for i in range(config.n - config.v[0]):
        for j in range(len(config.L1)):
            temp_quadratic[i] = (np.add(np.array(temp_quadratic[i]), np.multiply(config.L1[i][j], polynomial.quadratic[j]))).tolist()
            temp_linear[i] = (np.add(np.array(temp_linear[i]), np.multiply(config.L1[i][j], polynomial.linear[j]))).tolist()
            temp_constant[i] += config.L1[i][j] * polynomial.constant[j] 
        temp_constant[i] += config.b1[i]

    # Assign the computed values for L1 * F * L2
    polynomial.quadratic = temp_quadratic
    polynomial.linear = temp_linear
    polynomial.constant = temp_constant

    return

def generate_publickey(config):
    
    config.L2 = config.L2.retrieve()
    config.L2, config.L2inv, config.b2 = config.L2['l'], config.L2['linv'], config.L2['b']

    config.L1 = config.L1.retrieve()
    config.L1, config.L1inv, config.b1 = config.L1['l'], config.L1['linv'], config.L1['b']

    class myPolynomial: pass
    polynomial = myPolynomial()
    
    polynomial.quadratic = [[[0] * config.n for i in range(config.n)] for j in  range(config.n - config.v[0])]
    polynomial.linear = [[0] * config.n for i in range(config.n - config.v[0])]
    polynomial.constant = [0] * (config.n - config.v[0])

    olcount = 0
    pcount = 0

    for _i in range(config.u - 1):  
        
        layer = _i
        vl = len(config.F_layers[layer][0]['alphas'][0])
        ol = len(config.F_layers[layer][0]['betas'])

        generate_polynomial(vl, ol, pcount, config.F_layers[layer], polynomial, config)

        pcount += ol

    return polynomial
       

# Solves a set of linear equations given in 'polynomials'
def solve(polynomials, variables):

    eqn_var = list()
    eqn_con = list()

    for eqn in polynomials:
        #print("EQN : ", eqn)
        eqn_var.append(eqn[1:])
        eqn_con.append(-eqn[0])
    
    #print()
    
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

# -------------------- Retrieve Message -------------------- #

with open('testFile.txt', 'r') as file:
    message = file.read()

# -------------------- Parameters for Rainbow Scheme -------------------- #
class myConfigs: pass
config = myConfigs()

config.L1 = list()
config.L1inv = None
config.b1 = list()

config.L2 = list()
config.L2inv = None
config.b2 = list()

# Components of F
config.F_layers = list()
config.v = list()              # vinegar layers

config.n = 32        
config.u = 5                   # number of layers
config.k = 8                   # finite space of elements -- standard ASCII

#y = (6, 2, 0, 5)

# Components of public key
coeff_quadratic = list()
coeff_singular = list()
coeff_scalars = list()

#v = [2, 4, 6]   # Remove after generation of y is done
config.y = list()

config.v = generate_vinegars(config.u, config.n)


if args.v:
    print("V :", config.v)

config.y = generate_targets(message, config.v, config.n)


if args.v:
    print("Y :", config.y)

# -------------------- Generating F -------------------- #

config.F_layers = generate_coefficients(config.u, config.v, config.k)

# -------------------- Generating L1 and L2 -------------------- #

config.L1 = Affine(config.n-config.v[0], config.k)
config.L1.start_generators(20)

config.L2 = Affine(config.n, config.k)
config.L2.start_generators(20)

# -------------------- Generating Public Key -------------------- #

polynomial = generate_publickey(config)

print(polynomial.quadratic, len(polynomial.quadratic), len(polynomial.quadratic[0]), len(polynomial.quadratic[0][0]))
print(polynomial.linear, len(polynomial.linear), len(polynomial.linear[0]))
print(polynomial.constant, len(polynomial.constant))

# ------------------------ End of File ------------------------ #