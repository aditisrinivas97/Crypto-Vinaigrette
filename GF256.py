'''
Galois Field 256 basic arithmetic operations
'''

# -------------------- IMPORTS and Definitions -------------------- #

import secrets, argparse, numpy as np
import dill, errno, os, subprocess as sp, atexit


# -------------------- Module -------------------- #

class GF256:

    mask = 0xff

    exponenets = [
        1, 2, 4, 8, 16, 32, 64, 128, 77, 154, 121, 242,
        169, 31, 62, 124, 248, 189, 55, 110, 220, 245, 167, 3, 6, 12, 24,
        48, 96, 192, 205, 215, 227, 139, 91, 182, 33, 66, 132, 69, 138, 89,
        178, 41, 82, 164, 5, 10, 20, 40, 80, 160, 13, 26, 52, 104, 208,
        237, 151, 99, 198, 193, 207, 211, 235, 155, 123, 246, 161, 15, 30,
        60, 120, 240, 173, 23, 46, 92, 184, 61, 122, 244, 165, 7, 14, 28,
        56, 112, 224, 141, 87, 174, 17, 34, 68, 136, 93, 186, 57, 114, 228,
        133, 71, 142, 81, 162, 9, 18, 36, 72, 144, 109, 218, 249, 191, 51,
        102, 204, 213, 231, 131, 75, 150, 97, 194, 201, 223, 243, 171, 27,
        54, 108, 216, 253, 183, 35, 70, 140, 85, 170, 25, 50, 100, 200,
        221, 247, 163, 11, 22, 44, 88, 176, 45, 90, 180, 37, 74, 148, 101,
        202, 217, 255, 179, 43, 86, 172, 21, 42, 84, 168, 29, 58, 116, 232,
        157, 119, 238, 145, 111, 222, 241, 175, 19, 38, 76, 152, 125, 250,
        185, 63, 126, 252, 181, 39, 78, 156, 117, 234, 153, 127, 254, 177,
        47, 94, 188, 53, 106, 212, 229, 135, 67, 134, 65, 130, 73, 146,
        105, 210, 233, 159, 115, 230, 129, 79, 158, 113, 226, 137, 95, 190,
        49, 98, 196, 197, 199, 195, 203, 219, 251, 187, 59, 118, 236, 149,
        103, 206, 209, 239, 147, 107, 214, 225, 143, 83, 166, 1
    ]

    logarithms = [
        0, 0, 1, 23, 2, 46, 24, 83, 3, 106, 47, 147,
        25, 52, 84, 69, 4, 92, 107, 182, 48, 166, 148, 75, 26, 140, 53,
        129, 85, 170, 70, 13, 5, 36, 93, 135, 108, 155, 183, 193, 49, 43,
        167, 163, 149, 152, 76, 202, 27, 230, 141, 115, 54, 205, 130, 18,
        86, 98, 171, 240, 71, 79, 14, 189, 6, 212, 37, 210, 94, 39, 136,
        102, 109, 214, 156, 121, 184, 8, 194, 223, 50, 104, 44, 253, 168,
        138, 164, 90, 150, 41, 153, 34, 77, 96, 203, 228, 28, 123, 231, 59,
        142, 158, 116, 244, 55, 216, 206, 249, 131, 111, 19, 178, 87, 225,
        99, 220, 172, 196, 241, 175, 72, 10, 80, 66, 15, 186, 190, 199, 7,
        222, 213, 120, 38, 101, 211, 209, 95, 227, 40, 33, 137, 89, 103,
        252, 110, 177, 215, 248, 157, 243, 122, 58, 185, 198, 9, 65, 195,
        174, 224, 219, 51, 68, 105, 146, 45, 82, 254, 22, 169, 12, 139,
        128, 165, 74, 91, 181, 151, 201, 42, 162, 154, 192, 35, 134, 78,
        188, 97, 239, 204, 17, 229, 114, 29, 61, 124, 235, 232, 233, 60,
        234, 143, 125, 159, 236, 117, 30, 245, 62, 56, 246, 217, 63, 207,
        118, 250, 31, 132, 160, 112, 237, 20, 144, 179, 126, 88, 251, 226,
        32, 100, 208, 221, 119, 173, 218, 197, 64, 242, 57, 176, 247, 73,
        180, 11, 127, 81, 21, 67, 145, 16, 113, 187, 238, 191, 133, 200,161
    ]

    def __init__(self):
        pass
        
    def add(x, y):
        '''
        Add two numbers in the finite field
        '''
        if x not in range(256) or y not in range(256):
            print("Error : Values must be within finite field 256")
            return
        return x ^ y

    def subtract(x, y):
        '''
        Subtract two numbers in the finite field
        '''
        if x not in range(256) or y not in range(256):
            print("Error : Values must be within finite field 256!")
            return
        return x ^ y

    def multiply(x, y):
        '''
        Multiply two numbers in the finite field
        '''
        if x not in range(256) or y not in range(256):
            print("Error : Values must be within finite field 256!")
            return
        if x == 0 or y == 0 : 
            return 0
        else:
            return GF256.exponenets[(GF256.logarithms[x] + GF256.logarithms[y]) % 255] 

    def get_inverse(x):
        '''
        Find the inverse of a number in the finite field
        '''
        if x not in range(256):
            print("Error : Values must be within finite field 256!")
            return
        if x == 0:
            return 0
        else:
            return GF256.exponenets[255 - GF256.logarithms[x]]

    def lower_zero_matrix(mat, inverse):
        '''
        Change elements below diagonal to 0.
        '''
        if inverse:
            length = 2 * len(mat)
        else:
            length = len(mat) + 1

        for k in range(len(mat)-1):
            for i in range(k+1, len(mat)):
                factor = mat[i][k]
                factor2 = GF256.get_inverse(mat[k][k])
                if factor2 == 0:
                    raise Exception("Matrix not invertible")
                
                for j in range(k, length):
                    temp = GF256.multiply(mat[k][j], factor2)
                    temp = GF256.multiply(factor, temp)
                    mat[i][j] = GF256.add(mat[i][j], temp)

    
    def upper_zero_matrix(mat):
        '''
        Change elements above diagonal to 0.
        '''
        temp = 0
        for k in range(len(mat)-1, 0, -1):
            for i in range(k-1, -1, -1):
                factor = mat[i][k]
                factor2 = GF256.inverse(mat[k][k])
                if factor2 == 0:
                    raise Exception("Matrix not invertible")

                for j in range(k, 2 * len(mat)):
                    temp = GF256.multiply(mat[k][j], factor2)
                    temp = GF256.multiply(factor, temp)
                    mat[i][j] = GF256.add(mat[i][j], temp)

    
    def back_substitute(mat):
        '''
        Perform back-substitution (for solving equations)
        '''
        temp = GF256.inverse(mat[len(mat)-1][len(mat)-1])
        if temp == 0:
            raise Exception("Equations cannot be solved!")
        
        x = [0] * len(mat)
        x[len(mat) - 1] = GF256.multiply(mat[len(mat)-1][len(mat)], temp)
        for i in range(len(mat)-2, -1, -1):
            temp2 = mat[i][len(mat)]
            for j in range(len(mat)-1, i, -1):
                temp = GF256.multiply(at[i][j], x[j])
                temp2 = GF256.add(temp2, temp)
            
            temp = GF256.inverse(mat[i][i])
            if temp == 0:
                raise Exception("Equations cannot be solved!")
            
            x[i] = GF256.multiply(temp2, temp)


    def multiply_matrices(m1, m2):
        '''
        Multiply 2 matrices within the finite field.
        '''
        if len(m1) != len(m2) or len(m1[0]) != len(m2[0]):
            raise Exception("Matrices have to have same dimensions.")

        ret = [[0] * len(m2[0])] * len(m1)
        for i in range(len(m1)):
            for j in range(len(m2)):
                for k in range(len(m2[0])):
                    temp = GF256.multiply(m1[i][j], m2[j][k])
                    ret[i][k] = GF256.add(ret[i][k], temp)

        return ret

    
    def multiply_matrix_vector(m, v):
        '''
        Multiply a matrix and a vector within the finite field.
        '''
        if len(m[0]) != len(v):
            raise Exception("Cannot multiply")
        
        ret = [0] * len(m)
        for i in range(len(m)):
            for j in range(len(v)):
                temp = GF256.multiply(m[i][j], v[j])
                ret[i] = GF256.add(v[i], temp)

        return ret

    
    def add_vectors(v1, v2):
        '''
        Add two vectors within the finite field.
        '''
        if len(v1) != len(v2):
            raise Exception("Vectors must be equal length!")

        ret = [0] * len(v1)
        for i in range(len(v1)):
            ret[i] = GF256.add(v1[i], v2[i])

        return ret

    
    def multiply_vectors(v1, v2):
        '''
        Multiply 2 vectors.
        '''
        if len(v1) != len(v2):
            raise Exception("Vectors must be of same length to multiply!")

        ret = [[0] * len(v1)] * len(v2)
        for i in range(len(v1)):
            for j in range(len(v2)):
                ret[i][j] = GF256.multiply(v1[i], v2[j])

        return ret


    def multiply_matrix_scalar(m, s):
        '''
        Multiply a matrix with a scalar (each element) within the finite field.
        '''
        ret = list()
        for i in m:
            ret.append(list())
            for j in i:
                temp = GF256.multiply(j, s)
                ret[-1].append(temp)

        return ret

    def add_matrices(m1, m2):
        if len(m1) != len(m2) or len(m1[0]) != len(m2[0]):
            raise Exception("Matrices have to have same dimensions!")

        ret = list()
        for i in range(len(m1)):
            ret.append(list())
            for j in range(len(m1[0])):
                temp = GF256.add(m1[i][j], m2[i][j])
                ret[-1].append(temp)

        return ret



if __name__ == '__main__':
    print("Mask value :", GF256.mask)
    print("Addition of 255 and 254 :", GF256.add(255, 254))
    print("Subtraction of 255 and 254 :", GF256.subtract(255, 254))
    print("Multiplication of 255 and 254 :", GF256.multiply(255, 254))
    print("Inverse of 1 is and 255 are :", GF256.get_inverse(1), GF256.get_inverse(255))
    