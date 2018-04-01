'''
Generate UOV parameters and keys
'''

# -------------------- IMPORTS and Definitions -------------------- #

import secrets, argparse, numpy as np
import dill, errno, os, subprocess as sp, atexit
from Affine import *

# -------------------- Module -------------------- #

class rainbowKeygen:

    def __init__(self, verbosity = False):
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
        self.n = 32        
        self.u = 5                  
        self.k = 8
        self.verbosity = verbosity
        self.v = self.generate_vinegars()     
        self.F_layers = self.generate_coefficients()

        self.L1 = Affine(self.n - self.v[0], self.k)
        self.L1.start_generators(20)
        self.L1 = self.L1.retrieve()
        self.L1, self.L1inv, self.b1 = self.L1['l'], self.L1['linv'], self.L1['b'] 
        
        self.L2 = Affine(self.n, self.k)
        self.L2.start_generators(20)    
        self.L2 = self.L2.retrieve()
        self.L2, self.L2inv, self.b2 = self.L2['l'], self.L2['linv'], self.L2['b']

        if self.verbosity:
            print("Initialised with n :", self.n, ", k :", self.k, ", u :", self.u, "v :", self.v)

    def generate_random_element(self, k) :
        '''
        Generate a cryptographically secure random number below k
        ''' 
        num = secrets.randbelow(k)
        while not num :
            num = secrets.randbelow(k)
        return num

    def generate_random_matrix(self, x, y) :
        '''
        Generate 2D matrix with random elements below k
        '''
        mat = [[0] * y for i in range(x)]
        for i in range(x) :
            for j in range(y):
                mat[i][j] = self.generate_random_element(self.k)
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

            rnum = self.generate_random_element(self.n)

            if rnum not in ret and rnum != self.n:
                ret.append(rnum)

        if self.verbosity:
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

                alphas = self.generate_random_matrix(self.v[_i], self.v[_i])
                betas = self.generate_random_matrix(self.v[_i + 1] - self.v[_i], self.v[_i])
                gammas = self.generate_random_matrix(1, self.v[_i + 1])
                etas = self.generate_random_element(self.k)

                layer['alphas'] = alphas
                layer['betas'] = betas
                layer['gammas'] = gammas
                layer['etas'] = [etas]
        
        if self.verbosity:
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

        if self.verbosity:
            print("Generating public key..")

        class myPolynomial: pass
        polynomial = myPolynomial()
        
        polynomial.quadratic = [[[0] * self.n for i in range(self.n)] for j in  range(self.n - self.v[0])]
        polynomial.linear = [[0] * self.n for i in range(self.n - self.v[0])]
        polynomial.constant = [0] * (self.n - self.v[0])

        olcount = 0
        pcount = 0

        for _i in range(self.u - 1):  
            
            layer = _i
            vl = len(self.F_layers[layer][0]['alphas'][0])
            ol = len(self.F_layers[layer][0]['betas'])

            self.generate_polynomial(vl, ol, pcount, self.F_layers[layer], polynomial)

            pcount += ol
        
        # Compaction
        for i in range(len(polynomial.quadratic)):
            for j in range(len(polynomial.quadratic[i])):
                if i > j:   # lower triangle
                    polynomial.quadratic[j][i] += polynomial.quadratic[i][j]
                    polynomial.quadratic[j][i] = 0

        compact_quads = list()
        for i in range(len(polynomial.quadratic)):
            for j in range(i, len(polynomial.quadratic[i])):
                compact_quads.append(polynomial.quadratic[i][j])

        compact_quads_store = dill.dumps(compact_quads)
        
        if self.verbosity:
            print("Done")

if __name__ == '__main__':

    myKeyObject = rainbowKeygen(verbosity = True)
    myPublicKey = myKeyObject.generate_publickey()
 

    
    
    