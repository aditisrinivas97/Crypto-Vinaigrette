'''
Generate UOV parameters and keys
'''

# -------------------- IMPORTS and Definitions -------------------- #

import secrets, argparse, numpy as np
import dill, errno, os, subprocess as sp, atexit
from Affine import *

# -------------------- Command Line Args -------------------- #

parser = argparse.ArgumentParser()
parser.add_argument('-v', type=int, nargs='?', default=0)
args = parser.parse_args()
if args.v is None:
    args.v = 0 


# -------------------- Module -------------------- #

class rainbowKeygen:

    def __init__(self, n = 32, u = 5, k = 8):
        '''
        Initialise the key object

        n - Number of variables
        u - Number of layers
        k - Finite space of elements
        v - List of number of vinegar variables in each layer
        F_layers - Map F containing the coefficients namely alphas, betas, gammas and etas
        L1, L2 - Affine maps
        b1, b2 - Translation elements for the corresponsing affine maps

        '''
        self.n = n        
        self.u = u                  
        self.k = k
        self.v = self.generate_vinegars()     
        self.F_layers = self.generate_coefficients()

        self.L1 = Affine(self.n - self.v[0], self.k)
        self.L1.start_generators(20)
        
        self.L2 = Affine(self.n, self.k)
        self.L2.start_generators(20)

        self.L1 = self.L1.retrieve()
        self.L1, self.L1inv, self.b1 = self.L1['l'], self.L1['linv'], self.L1['b'] 

        self.L2 = self.L2.retrieve()
        self.L2, self.L2inv, self.b2 = self.L2['l'], self.L2['linv'], self.L2['b']
        #print(self.L1, self.L2, self.L1inv, self.L2inv)
        #print(self.F_layers)

        if args.v:
            print("Initialised with n :", self.n, ", k :", self.k, ", u :", self.u, "v :", self.v)

    def generate_random_element(k) :
        '''
        Generate a cryptographically secure random number below k
        ''' 
        num = secrets.randbelow(k)
        while not num :
            num = secrets.randbelow(k)
        return num

    def generate_random_matrix(x, y, k) :
        '''
        Generate 2D matrix with random elements below k
        '''
        mat = [[0] * y for i in range(x)]
        for i in range(x) :
            for j in range(y):
                mat[i][j] = rainbowKeygen.generate_random_element(k)
        return mat
    
    def generate_vinegars(self):
        '''
        Generate vinegar variables for 'u' layers where the last layer has 'n' vinegars
        '''
        ret = list()

        while True : 
            if len(ret) == self.u :
                ret.sort()
                ret[-1] = self.n
                break

            rnum = rainbowKeygen.generate_random_element(self.n)

            if rnum not in ret and rnum != self.n:
                ret.append(rnum)

        if args.v:
            print("Done generating vinegar variable count for each layer")

        return ret

    def generate_coefficients(self):
        '''
        Generate F - coefficients below 'k' for every polynomial in the keys
        '''
        ret = list()

        for _i in range(self.u - 1):

            ol = self.v[_i + 1] - self.v[_i]

            ret.append(list())

            for i in range(ol):
                ret[-1].append(dict())
                layer = ret[-1][-1]
                
                layer['alphas'] = list()
                layer['betas'] = list()
                layer['gammas'] = list()
                layer['etas'] = list()

                alphas = rainbowKeygen.generate_random_matrix(self.v[_i], self.v[_i], self.k)
                betas = rainbowKeygen.generate_random_matrix(self.v[_i + 1] - self.v[_i], self.v[_i], self.k)
                gammas = rainbowKeygen.generate_random_matrix(1, self.v[_i + 1], self.k)
                etas = rainbowKeygen.generate_random_element(self.k)

                layer['alphas'] = alphas
                layer['betas'] = betas
                layer['gammas'] = gammas
                layer['etas'] = [etas]
        
        if args.v:
            print("Done generating F map for each layer")
        
        return ret
    
    def generate_polynomial(self, vl, ol, pcount, coefficients, polynomial):
        '''
        Generates polynomials for the Map F
        '''
        # Composition of F and L2
        for _i in range(ol):

            # Multiply Alphas
            for i in range(vl):
                for j in range(vl):
                    temp = np.multiply(coefficients[_i]['alphas'][i][j], self.L2[i])
                    polynomial.quadratic[pcount + _i] = (np.add(np.array(polynomial.quadratic[pcount + _i]), np.multiply((np.array(temp)).reshape(self.n, 1), (np.array(self.L2[j])).reshape(1, self.n)))).tolist()
                    temp = np.multiply(self.b2[j], temp)
                    polynomial.linear[pcount + _i] = (np.add(temp, polynomial.linear[pcount + _i])).tolist()
                    temp = np.multiply(coefficients[_i]['alphas'][i][j], self.L2[j])
                    temp = np.multiply(self.b2[i], temp)
                    polynomial.linear[pcount + _i] = (np.add(temp, polynomial.linear[pcount + _i])).tolist()     
                    temp = coefficients[_i]['alphas'][i][j] * self.b2[i]
                    polynomial.constant[pcount + _i] += temp * self.b2[j]

            # Multiply Betas    
            for i in range(ol):
                for j in range(vl):
                    temp = np.multiply(coefficients[_i]['betas'][i][j], self.L2[i + vl])
                    polynomial.quadratic[pcount + _i] = (np.add(np.array(polynomial.quadratic[pcount + _i]), np.multiply((np.array(temp)).reshape(self.n, 1), (np.array(self.L2[j])).reshape(1, self.n)))).tolist()
                    temp = np.multiply(self.b2[j], temp)
                    polynomial.linear[pcount + _i] = (np.add(temp, polynomial.linear[pcount + _i])).tolist()
                    temp = np.multiply(coefficients[_i]['betas'][i][j], self.L2[j])
                    temp = np.multiply(self.b2[i + vl], temp)
                    polynomial.linear[pcount + _i] = (np.add(temp, polynomial.linear[pcount + _i])).tolist()
                    temp = coefficients[_i]['betas'][i][j] * self.b2[i + vl]
                    polynomial.constant[pcount + _i] += temp * self.b2[j]
            
            # Multiply Gammas    
            for i in range(vl + ol):
                temp = np.multiply(coefficients[_i]['gammas'][0][i], self.L2[i])
                polynomial.linear[pcount + _i] = (np.add(temp, polynomial.linear[pcount + _i])).tolist()
                polynomial.constant[pcount + _i] += coefficients[_i]['gammas'][0][i] * self.b2[i]
            
            # Add Eta
            polynomial.constant[pcount + _i] += coefficients[_i]['etas'][0]
        
        # Composition of L1 and F * L2
        temp_quadratic = [[[0] * self.n for i in range(self.n)] for j in  range(self.n - self.v[0])]
        temp_linear = [[0] * self.n for i in range(self.n - self.v[0])]
        temp_constant = [0] * (self.n - self.v[0])

        for i in range(self.n - self.v[0]):
            for j in range(len(self.L1)):
                temp_quadratic[i] = (np.add(np.array(temp_quadratic[i]), np.multiply(self.L1[i][j], polynomial.quadratic[j]))).tolist()
                temp_linear[i] = (np.add(np.array(temp_linear[i]), np.multiply(self.L1[i][j], polynomial.linear[j]))).tolist()
                temp_constant[i] += self.L1[i][j] * polynomial.constant[j] 
            temp_constant[i] += self.b1[i]

        # Assign the computed values for L1 * F * L2
        polynomial.quadratic = temp_quadratic
        polynomial.linear = temp_linear
        polynomial.constant = temp_constant
        return

    def generate_publickey(self):
        '''
        Generates the public key
        '''

        if args.v:
            print("Generating public key...")

        class myPolynomial: pass
        self.polynomial = myPolynomial()
        
        self.polynomial.quadratic = [[[0] * self.n for i in range(self.n)] for j in  range(self.n - self.v[0])]
        self.polynomial.linear = [[0] * self.n for i in range(self.n - self.v[0])]
        self.polynomial.constant = [0] * (self.n - self.v[0])

        olcount = 0
        pcount = 0

        for _i in range(self.u - 1):  
            
            layer = _i
            vl = len(self.F_layers[layer][0]['alphas'][0])
            ol = len(self.F_layers[layer][0]['betas'])

            self.generate_polynomial(vl, ol, pcount, self.F_layers[layer], self.polynomial)

            pcount += ol
        
        # Compaction
        compact_quads = list()
        for i in range(len(self.polynomial.quadratic)):
            compact_quads.append(list())
            for j in range(len(self.polynomial.quadratic[i])):
                for k in range(len(self.polynomial.quadratic[i][j])):
                    if j > k:   # lower triangle
                        self.polynomial.quadratic[i][k][j] += self.polynomial.quadratic[i][j][k]
                        #self.polynomial.quadratic[i][j][k] = 0
                    else:
                        compact_quads[-1].append(self.polynomial.quadratic[i][j][k])

        class pubKeyClass: pass

        pubKey = pubKeyClass()
        pubKey.n = self.n
        pubKey.v0 = self.v[0]
        pubKey.k = self.k
        pubKey.quads = compact_quads
        pubKey.linear = self.polynomial.linear
        pubKey.consts = self.polynomial.constant
        
        with open('rPub.rkey', 'wb') as pubFile:
            dill.dump(pubKey, pubFile)
        
        if args.v:
            print("Done")

    def generate_privatekey(self):
        '''
        Generates the private key.
        '''
        
        if args.v:
            print("Generating private key...")
        class privKeyClass: pass

        privKey = privKeyClass()
        privKey.l1 = self.L1
        privKey.l1inv = self.L1inv
        privKey.b1 = self.b1
        privKey.l2 = self.L2
        privKey.l2inv = self.L2inv
        privKey.b2 = self.b2
        privKey.F_layers = self.F_layers
        privKey.k = self.k

        with open('rPriv.rkey', 'wb') as privFile:
            dill.dump(privKey, privFile)

        if args.v:
            print("Done.")


    def generate_targets(n, v0, k, message):
        '''
        Generates Y or the set of targets
        '''
        ret = list()

        parts = n - v0          # Number of parts to split message into
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

    def sign(keyFile, msgFile):
        '''
        Sign message at msgFile with private key at keyFile!
        '''
        
        if args.v:
            print("Signing...")
        # Load private key
        with open(keyFile, 'rb') as kFile:
            privKey = dill.load(kFile)
            privKey.n = len(privKey.F_layers[-1][0]['alphas'][0]) + len(privKey.F_layers[-1][0]['betas'])
            privKey.layers = len(privKey.F_layers)

        # Load message (as n dimensional vector)
        with open(msgFile, 'r') as mFile:
            message = mFile.read()
            y = rainbowKeygen.generate_targets(privKey.n, len(privKey.F_layers[0][0]['alphas'][0]), privKey.k, message)
        
        # Apply L1^(-1)
        ydash = [a-b for a, b in zip(y, privKey.b1)]
        privKey.l1inv = np.matrix(privKey.l1inv)
        ydash = np.matrix(ydash)

        ydash = ydash * privKey.l1inv
        ydash = np.array(ydash)[0]

        while True:
            try:
                # Generate v0 number of random vinegars as x0, x1...xv0
                x = list()
                for i in range(len(privKey.F_layers[0][0]['alphas'][0])):
                    x.append(rainbowKeygen.generate_random_element(privKey.k))

                # Solve polynomials layer by layer, finding ol oils and adding them to vinegars (i.e, x)
                for layer in range(privKey.layers):
                    vl = len(privKey.F_layers[layer][0]['alphas'][0])
                    ol = len(privKey.F_layers[layer][0]['betas'])
                    equations = [[0] * ol for i in range(ol)]
                    consts = [0] * ol
                    
                    for i in range(ol):
                        for j in range(vl):
                            for k in range(vl):
                                consts[i]
                                privKey.F_layers[layer][i]['alphas'][j][k]
                                x[j]
                                x[k]
                                consts[i] += privKey.F_layers[layer][i]['alphas'][j][k] * x[j] * x[k]

                        for j in range(ol):
                            for k in range(vl):
                                equations[i][j]
                                privKey.F_layers[layer][i]['betas'][j][k]
                                x[k]
                                equations[i][j] += privKey.F_layers[layer][i]['betas'][j][k] * x[k]

                        for j in range(ol+vl):
                            if j < vl:
                                consts[i]
                                privKey.F_layers[layer][i]['gammas'][0][j]
                                x[j]
                                consts[i] += privKey.F_layers[layer][i]['gammas'][0][j] * x[j]
                            else:
                                equations[i][j-vl]
                                privKey.F_layers[layer][i]['gammas'][0][j]
                                equations[i][j-vl] += privKey.F_layers[layer][i]['gammas'][0][j]

                        consts[i]
                        privKey.F_layers[layer][i]['etas'][0]
                        consts[i] += privKey.F_layers[layer][i]['etas'][0]

                    for i in range(len(consts)):
                        consts[i] = -consts[i] + ydash[i]

                    if args.v >= 2:
                        print(equations, consts)
                    solns = np.linalg.solve(equations, consts)
                    for s in solns:
                        x.append(s)

                # Applying L2 inverse to x
                signature = [a-b for a, b in zip(x, privKey.b2)]
                privKey.l2inv = np.matrix(privKey.l2inv)
                signature = np.matrix(signature)

                signature = signature * privKey.l2inv
                signature = np.array(signature)[0]
                if args.v >= 2:
                    print(signature)
                break
            except LinAlgError:
                print("Restarting with new vinegar!")
        
        if args.v:
            print("Done.")
        return signature
    
    def verify(keyFile, signature, msgFile):
        '''
        Verify the signature using the public key
        '''
        with open(keyFile, 'rb') as kFile:
            pubKey = dill.load(kFile)

        pubKey.quadratic = list()

        for _i in pubKey.quads:
            temp2d = list()
            for i in range(pubKey.n):
                temp = list()
                temp.extend([0] * i)
                for j in range(pubKey.n - i):
                    temp.append(_i[j+i])
                temp2d.append(temp)
            pubKey.quadratic.append(temp2d)

        with open(msgFile, 'r') as mFile:
            message = mFile.read()
        
        y = rainbowKeygen.generate_targets(pubKey.n, pubKey.v0, pubKey.k, message)
        temp = 0
        for i in range(len(pubKey.quadratic)):
            for p in range(len(pubKey.quadratic[i])):
                for q in range(len(pubKey.quadratic[i][p])):
                    temp += pubKey.quadratic[i][p][q] * signature[p] * signature[q]
            
            for p in range(len(pubKey.linear[i])):
                temp += pubKey.linear[i][p] * signature[p]

            temp += pubKey.consts[i]
            print(i, temp, y[i], temp == y[i])
        
        return


if __name__ == '__main__':
    myKeyObject = rainbowKeygen()
    myKeyObject.generate_publickey()
    myKeyObject.generate_privatekey()
    signature = rainbowKeygen.sign('rPriv.rkey', 'testFile.txt')
    rainbowKeygen.verify('rPub.rkey', signature, 'testFile.txt')
    print(signature)