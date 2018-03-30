# -------------------- IMPORTS and Definitions -------------------- #
import secrets, argparse, numpy as np
import dill, errno, os, subprocess as sp, atexit


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
    
    return ret


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

'''
# -------------------- Retrieve Message -------------------- #
with open(args.message_file, 'r') as file:
    message = file.read()
'''
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

config.n = 33        
config.u = 5                   # number of layers
config.k = 128                   # finite space of elements -- standard ASCII

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


# -------------------- Setup Work for Generating Ls -------------------- #

config.datpath = os.path.abspath('.') + '/.dat/params'
if not os.path.exists(os.path.dirname(config.datpath)):
    try:
        os.makedirs(os.path.dirname(config.datpath))
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


config.spawn = 10       # Child process to spawn for L1 and L2 each
config.cmd = 'python3'
config.genscript = 'l_generator.py'
config.generators = list()

# Register exit handler
atexit.register(cleanup_atexit, config)


# -------------------- Generating L1 and L2 -------------------- #

def generate_L_props(config):
    config.L_dimensions = config.v[config.u - 1] - config.v[0]

    with open(config.datpath, 'wb') as lfile:
        toWrite = dict()
        toWrite['dim'] = config.L_dimensions
        toWrite['generate_random_element'] = generate_random_element
        toWrite['generate_random_matrix'] = generate_random_matrix
        toWrite['k'] = config.k
        dill.dump(toWrite, lfile)

    return config

config = generate_L_props(config)


# ---------- Spawn Generators ---------- #
def spawn_Lgenerators(config):
    for i in range(config.spawn):
        _temp = sp.Popen([config.cmd, os.path.abspath('.') + '/' + config.genscript, config.datpath, str(i)])
        config.generators.append(_temp)
        print("Spawned generator", i)

    config.spawn = set(range(config.spawn))
    config.spawned = True
    return config

config = spawn_Lgenerators(config)


# --------------- Loading L1 and L2 --------------- #
def load_Ls(config):
    if args.v:
        print("Retrieving Ls")

    LPath = os.path.dirname(config.datpath)

    while True:
        found = False
        for lf in config.spawn:
            if config.generators[lf].poll() != None:
                print("L1 from generator", lf)
                with open(LPath + '/l' + str(lf), 'rb') as lfile:
                    tempL = dill.load(lfile)
                    config.L1 = tempL[0]
                    config.L1inv = tempL[1]
                os.remove(LPath + '/l' + str(lf))
                config.spawn.remove(lf)
                found = True
                break
        
        if found:
            break

    while True:
        found = False
        for lf in config.spawn:
            if config.generators[lf].poll() != None:
                print("L2 from generator", lf)
                with open(LPath + '/l' + str(lf), 'rb') as lfile:
                    tempL = dill.load(lfile)
                    config.L2 = tempL[0]
                    config.L2inv = tempL[1]
                config.spawn.remove(lf)
                found = True
                break

        if found:
            break
    
    sp.Popen(['rm', '-r', '-f', LPath])
    return config


# -------------------- Generating F -------------------- #

config.F_layers = generate_coefficients(config.u, config.v, config.k)

# --------------- Construction of central map --------------- #

max_attempts = 30
attempts = 0

no_solution = True

while no_solution:

    #print("LOOP")

    if attempts == max_attempts:
        print("New Attempt")
        if 'spawned' in vars(config):
            cleanup_atexit(config)
        config.v = generate_vinegars(config.u, config.n)
        config.F_layers = generate_coefficients(config.u, config.v, config.k)
        config.y = generate_targets(message, config.v, config.n)
        config = generate_L_props(config)
        config = spawn_Lgenerators(config)

        attempts = 1
    else:
        attempts += 1

    no_solution = False

    config.vinegar_vars = list()   # Random vinegar variables

    for i in range(config.v[0]):
        config.vinegar_vars.append(generate_random_element(config.k))

    ycount = 0
    pcount = 0
    olcount = 0

    polynomials = list()

    for _i in range(config.v[0], config.n):  # Number of polynomials in the central map

        vl = -1         # Number of vinegar variables in current layer
        ol = -1         # Number of oil variables in current layer
        layer = -1      # Layer number

        for i in range(1, len(config.v)):
            if _i < config.v[i] :
                ol = config.v[i] - config.v[i - 1]
                vl = config.v[i - 1]
                layer = i - 1 
                break
        
        p, variables = generate_polynomial(vl, ol, config.F_layers[layer][olcount], config.vinegar_vars, config.y[ycount])

        polynomials.append(p)

        pcount += 1

        if len(variables) == pcount:
            res = solve(polynomials, variables)
            
            if len(res) == 0:
                no_solution = True
                break

            for x in res:
                config.vinegar_vars.append(x)
            
            polynomials = list()
            pcount = 0
            olcount = 0          
        else:
            olcount += 1

        ycount += 1

print("Vinegars for each layer (v) : ", config.v)
print("Solution : ", config.vinegar_vars)
print("Y : ", config.y)


# -------------------- Generating b1 -------------------- #

for i in range(config.L_dimensions):
    config.b1.append(generate_random_element(config.k))

# -------------------- Generating b2 -------------------- #

for i in range(config.L_dimensions):
    config.b2.append(generate_random_element(config.k))

config = load_Ls(config)

if args.vv :
    print("L1 :", config.L1)
    print("L1inv :", config.L1inv)
    print("L2 :", config.L2)
    print("L2inv :", config.L2inv)