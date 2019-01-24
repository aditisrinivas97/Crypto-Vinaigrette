'''
Generate UOV parameters and keys
'''

# -------------------- IMPORTS and Definitions -------------------- #

import secrets, argparse, numpy as np
import dill, errno, os, subprocess as sp, atexit, hashlib
from datetime import datetime as dt
from .Affine import *
from .GF256 import *

class pubKeyClass: pass
class privKeyClass: pass

# -------------------- Command Line Args -------------------- #

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', type=int, nargs='?', default=0)
    args = parser.parse_args()
    if args.v is None:
        args.v = 0 
else:
    args = argparse.Namespace()
    args.v = 0


# -------------------- Module -------------------- #

class rainbowKeygen:

    def __init__(self, n = 32, u = 5, k = 8, save=''):
        '''
        Initialise the key object

        Parameters:
            n - Number of variables
            u - Number of layers
            k - Finite space of elements
            save - File to save as

        Private keys are saved as '.pem' files.
        Public keys are saved as '.pub' files.

        Generated:
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

        if args.v:
            print("Initialised with n :", self.n, ", k :", self.k, ", u :", self.u, "v :", self.v)

        start = dt.now()
        self.generate_keys(save)
        end = dt.now()
        if args.v:
            print("Generated keys in", end - start, "seconds")

    def generate_random_element() :
        '''
        Generate a cryptographically secure random number within the finite field.
        ''' 
        num = GF256.get()
        while not num :
            num = GF256.get()
        return num

    def generate_random_matrix(x, y, k) :
        '''
        Generate 2D matrix with random elements below k
        '''
        mat = [[0] * y for i in range(x)]
        for i in range(x) :
            for j in range(y):
                mat[i][j] = rainbowKeygen.generate_random_element()
        return mat
    
    def generate_vinegars(self):
        '''
        Generate vinegar variables for 'u' layers where the last layer has 'n' vinegars
        '''
        ret = list()

        rnum = rainbowKeygen.generate_random_element()
        while rnum > self.n or (rnum - self.n) >= (self.u):
            rnum = rainbowKeygen.generate_random_element()


        while True : 
            if len(ret) == self.u :
                ret.sort()
                ret[-1] = self.n
                break

            rnum = rainbowKeygen.generate_random_element()

            if rnum not in ret and rnum != self.n and (rnum - self.n) < (self.u - len(ret)):
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
                etas = rainbowKeygen.generate_random_element()

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
                    temp = GF256.multiply_scalar_vector(coefficients[_i]['alphas'][i][j], self.L2[i])
                    polynomial.quadratic[pcount + _i] = GF256.add_matrices(polynomial.quadratic[pcount + _i], GF256.multiply_vectors(temp, self.L2[j]))
                    temp = GF256.multiply_scalar_vector(self.b2[j], temp)
                    polynomial.linear[pcount + _i] = GF256.add_vectors(temp, polynomial.linear[pcount + _i])
                    temp = GF256.multiply_scalar_vector(coefficients[_i]['alphas'][i][j], self.L2[j])
                    temp = GF256.multiply_scalar_vector(self.b2[i], temp)
                    polynomial.linear[pcount + _i] = GF256.add_vectors(temp, polynomial.linear[pcount + _i])
                    temp = GF256.multiply(coefficients[_i]['alphas'][i][j], self.b2[i])
                    polynomial.constant[pcount + _i] = GF256.add(polynomial.constant[pcount + _i], GF256.multiply(temp, self.b2[j]))

            # Multiply Betas    
            for i in range(ol):
                for j in range(vl):
                    temp = GF256.multiply_scalar_vector(coefficients[_i]['betas'][i][j], self.L2[i + vl])
                    polynomial.quadratic[pcount + _i] = GF256.add_matrices(polynomial.quadratic[pcount + _i], GF256.multiply_vectors(temp, self.L2[j]))
                    temp = GF256.multiply_scalar_vector(self.b2[j], temp)
                    polynomial.linear[pcount + _i] = GF256.add_vectors(temp, polynomial.linear[pcount + _i])
                    temp = GF256.multiply_scalar_vector(coefficients[_i]['betas'][i][j], self.L2[j])
                    temp = GF256.multiply_scalar_vector(self.b2[i + vl], temp)
                    polynomial.linear[pcount + _i] = GF256.add_vectors(temp, polynomial.linear[pcount + _i])
                    temp = GF256.multiply(coefficients[_i]['betas'][i][j], self.b2[i + vl])
                    polynomial.constant[pcount + _i] = GF256.add(polynomial.constant[pcount + _i], GF256.multiply(temp, self.b2[j]))
            
            # Multiply Gammas    
            for i in range(vl + ol):
                temp = GF256.multiply_scalar_vector(coefficients[_i]['gammas'][0][i], self.L2[i])
                polynomial.linear[pcount + _i] = GF256.add_vectors(temp, polynomial.linear[pcount + _i])
                polynomial.constant[pcount + _i] = GF256.add(polynomial.constant[pcount + _i], GF256.multiply(coefficients[_i]['gammas'][0][i], self.b2[i]))
            
            # Add Eta
            polynomial.constant[pcount + _i] = GF256.add(polynomial.constant[pcount + _i], coefficients[_i]['etas'][0])
        
        return

    def generate_publickey(self, save=''):
        '''
        Generates the public key.

        Parameters:
            save - the destination folder
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
        
        # Composition of L1 and F * L2
        temp_quadratic = [[[0] * self.n for i in range(self.n)] for j in  range(self.n - self.v[0])]
        temp_linear = [[0] * self.n for i in range(self.n - self.v[0])]
        temp_constant = [0] * (self.n - self.v[0])

        for i in range(self.n - self.v[0]):
            for j in range(len(self.L1)):
                temp_quadratic[i] = GF256.add_matrices(temp_quadratic[i], GF256.multiply_matrix_scalar(self.polynomial.quadratic[j], self.L1[i][j]))
                temp_linear[i] = GF256.add_vectors(temp_linear[i], GF256.multiply_scalar_vector(self.L1[i][j], self.polynomial.linear[j]))
                temp_constant[i] = GF256.add(temp_constant[i], GF256.multiply(self.L1[i][j], self.polynomial.constant[j]))
            temp_constant[i] = GF256.add(temp_constant[i], self.b1[i])

        # Assign the computed values for L1 * F * L2
        self.polynomial.quadratic = temp_quadratic
        self.polynomial.linear = temp_linear
        self.polynomial.constant = temp_constant

        # Compaction
        compact_quads = list()
        for i in range(len(self.polynomial.quadratic)):
            compact_quads.append(list())
            for j in range(len(self.polynomial.quadratic[i])):
                for k in range(j, len(self.polynomial.quadratic[i][j])):
                    if j == k:
                        compact_quads[-1].append(self.polynomial.quadratic[i][j][k])
                    else:
                        compact_quads[-1].append(GF256.add(self.polynomial.quadratic[i][k][j], self.polynomial.quadratic[i][j][k]))
                        

        pubKey = pubKeyClass()
        pubKey.n = self.n
        pubKey.v0 = self.v[0]
        pubKey.k = self.k
        pubKey.quads = compact_quads
        pubKey.linear = self.polynomial.linear
        pubKey.consts = self.polynomial.constant
        self.public_key = pubKey
        
        if save != '':
            with open(save + 'cvPub.pub', 'wb') as pubFile:
                dill.dump(pubKey, pubFile)
        
        if args.v:
            print("Done")

    def generate_privatekey(self, save=''):
        '''
        Generates the private key.

        Parameters:
            save - the destination folder
        '''
        
        if args.v:
            print("Generating private key...")

        privKey = privKeyClass()
        privKey.l1 = self.L1
        privKey.l1inv = self.L1inv
        privKey.b1 = self.b1
        privKey.l2 = self.L2
        privKey.l2inv = self.L2inv
        privKey.b2 = self.b2
        privKey.F_layers = self.F_layers
        privKey.k = self.k
        self.private_key = privKey

        if save != '':
            with open(save + 'cvPriv.pem', 'wb') as privFile:
                dill.dump(privKey, privFile)

        if args.v:
            print("Done.")


    def generate_targets(n, v0, k, message):
        '''
        Generates Y or the set of targets from the hash of the message.
        '''

        h = hashlib.new('ripemd160')
        h.update(bytes(message, encoding='utf-8'))
        newMessage = h.hexdigest()
        if args.v:
            print("Hashed message of length", len(message), "to hash length :", len(newMessage))
        
        message = newMessage
        ret = list()

        parts = n - v0          # Number of parts to split message into
        if args.v >= 2:
            print("Splitting into", parts, "parts.")
        part = len(message) // (parts + 1)      # Length of each part
        part += 1

        k = 0
        for i in range(parts):
            yPart = 0
            try:
                for j in range(part):
                    yPart = yPart | ord(message[k])
                    k += 1
            except IndexError:
                ret.append(yPart)
                break
            ret.append(yPart)

        ret.extend([0] * (parts-i-1))

        if args.v >= 2:
            print("Message =", ret)

        return ret

    def sign(keyFile, msgFile):
        '''
        Sign message at msgFile with private key at keyFile!
        '''
        
        if args.v:
            pass#print("Signing...")
        # Load private key
        if isinstance(keyFile, privKeyClass):
            privKey = keyFile
            privKey.n = len(privKey.F_layers[-1][0]['alphas'][0]) + len(privKey.F_layers[-1][0]['betas'])
            privKey.layers = len(privKey.F_layers)
            if args.v:
                print("Loading private key from file...")
        else:
            with open(keyFile, 'rb') as kFile:
                privKey = dill.load(kFile)
                privKey.n = len(privKey.F_layers[-1][0]['alphas'][0]) + len(privKey.F_layers[-1][0]['betas'])
                privKey.layers = len(privKey.F_layers)

        # Load message (as n dimensional vector)
        with open(msgFile, 'r') as mFile:
            message = mFile.read()
            y = rainbowKeygen.generate_targets(privKey.n, len(privKey.F_layers[0][0]['alphas'][0]), privKey.k, message)
            if args.v >= 2:
                print(y)
        
        # Apply L1^(-1)

        ydash = GF256.add_vectors(y, privKey.b1)
        ydash = GF256.multiply_matrix_vector(privKey.l1inv, ydash)

        v0 = len(privKey.F_layers[0][0]['alphas'][0])

        while True:
            try:
                # Generate v0 number of random vinegars as x0, x1...xv0
                x = list()
                for i in range(len(privKey.F_layers[0][0]['alphas'][0])):
                    x.append(rainbowKeygen.generate_random_element())

                # Solve polynomials layer by layer, finding ol oils and adding them to vinegars (i.e, x)
                for layer in range(privKey.layers):
                    vl = len(privKey.F_layers[layer][0]['alphas'][0])
                    ol = len(privKey.F_layers[layer][0]['betas'])
                    equations = [[0] * ol for i in range(ol)]
                    consts = [0] * ol

                    if args.v >= 2:
                        print("Layer", layer, "oils", ol, "vinegars", vl)
                    
                    for i in range(ol):
                        for j in range(vl):
                            for k in range(vl):
                                consts[i]
                                privKey.F_layers[layer][i]['alphas'][j][k]
                                x[j]
                                x[k]
                                consts[i] = GF256.add(consts[i], 
                                    GF256.multiply(
                                        GF256.multiply(privKey.F_layers[layer][i]['alphas'][j][k], x[j]), 
                                        x[k])
                                    )

                        for j in range(ol):
                            for k in range(vl):
                                equations[i][j]
                                privKey.F_layers[layer][i]['betas'][j][k]
                                x[k]
                                equations[i][j] = GF256.add(equations[i][j], GF256.multiply(privKey.F_layers[layer][i]['betas'][j][k], x[k]))

                        for j in range(ol+vl):
                            if j < vl:
                                consts[i]
                                privKey.F_layers[layer][i]['gammas'][0][j]
                                x[j]
                                consts[i] = GF256.add(consts[i], GF256.multiply(privKey.F_layers[layer][i]['gammas'][0][j], x[j]))
                            else:
                                equations[i][j-vl]
                                privKey.F_layers[layer][i]['gammas'][0][j]
                                equations[i][j-vl] = GF256.add(equations[i][j-vl], privKey.F_layers[layer][i]['gammas'][0][j])

                        consts[i]
                        privKey.F_layers[layer][i]['etas'][0]
                        consts[i] = GF256.add(consts[i], privKey.F_layers[layer][i]['etas'][0])

                    for e in range(len(equations)):
                        equations[e].append(consts[e])

                    if args.v >= 2:
                        print(equations, consts)
                    
                    start = len(x) - v0
                    if args.v >= 3:
                        print(len(ydash))
                        print(start, len(equations))
                        print(start+len(equations))
                        print(len(ydash[start:start+ol]))
                    solns = GF256.solve_equation(equations, ydash[start:start+ol])

                    for s in solns:
                        x.append(s)

                # Applying L2 inverse to x
                signature = GF256.add_vectors(x, privKey.b2)
                signature = GF256.multiply_matrix_vector(privKey.l2inv, signature)

                if args.v >= 2:
                    print(signature)
                break
            except GF256Errors as e:
                print("Layer", layer, "of", privKey.layers)
                print("Restarting with new vinegar! because", e)
                #raise e
            except Exception as e:
                if args.v:
                    print("Restarting with new vinegar because", e, "!")
                    #raise e
        
        if args.v:
            print("Done.")
        return signature
    
    def verify(keyFile, signature, msgFile):
        '''
        Verify the signature using the public key
        '''
        if isinstance(keyFile, pubKeyClass):
            pubKey = keyFile
            if args.v:
                print("Loading public key from file...")
        else:
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
            if args.v >= 2:
                print(message)
            y = rainbowKeygen.generate_targets(pubKey.n, pubKey.v0, pubKey.k, message)

        ret = [0] * len(pubKey.quads)
        for p in range(len(pubKey.quads)):
            offset = 0
            for q in range(pubKey.n):
                for r in range(q, pubKey.n):
                    ret[p] = GF256.add(GF256.multiply(pubKey.quads[p][offset], 
                                GF256.multiply(signature[q], signature[r])), 
                            ret[p])
                    offset += 1
                ret[p] = GF256.add(ret[p], GF256.multiply(pubKey.linear[p][q], signature[q]))
            ret[p] = GF256.add(ret[p], pubKey.consts[p])

    
        for i, a, b in zip(range(len(ret)), ret, y):
            if args.v >= 2:
                print(i, a, b, a==b)
            if a != b:
                return False
        
        return True

    def generate_keys(self, save=''):
        '''
        Generates both the private and public keys.

        Parameters:
            save - the file to save as.

        Private keys get '.pem' extension, public keys get '.pub' extension.
        '''
        if args.v:
            print("Generating keys")
        
        self.generate_publickey(save)
        if args.v:
            print("Generated public key!")

        self.generate_privatekey(save)
        if args.v:
            print("Generated private key")

    def save_signature(signature, sfile='rSignature'):
        with open(sfile, 'wb') as opFile:
            dill.dump(signature, opFile)

    def load_signature(sfile='rSignature'):
        with open(sfile, 'wb') as ipFile:
            signature = dill.load(opFile)

        return signature


if __name__ == '__main__':
    print('CryptoVinaigrette is now a package! Please use `pip install cryptovinaigrette` and `from cryptovinaigrette import cryptovinaigrette` then `myKeyObject = cryptovinaigrette.rainbowKeygen()`')
    # myKeyObject = rainbowKeygen(save='rainbowTest')
    
    # start = dt.now()
    # signature = rainbowKeygen.sign('rainbowTest.pem', '../test/testFile.txt')
    # end = dt.now()
    # if args.v:
    #     print("Signed in", end - start, "seconds")
    
    # start = dt.now()
    # print("Signature verification :", rainbowKeygen.verify('rainbowTest.pub', signature, '../test/testFile.txt'))
    # end = dt.now()
    # if args.v:
    #     print("Verified signature in", end - start, "seconds")
    
    # if args.v >= 2:
    #     print("Signature :", signature)