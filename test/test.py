# from Generators import *
from context import cryptovinaigrette
from cryptovinaigrette import cryptovinaigrette
from datetime import datetime as dt

__RED = "\033[0;31m"
__GREEN = "\033[0;32m"
__NOCOLOR = "\033[0m"
def colored_binary(b):
    if b:
        return __GREEN + str(b) + __NOCOLOR
    else:
        return __RED + str(b) + __NOCOLOR

class args: pass
args = args()
args.v = True

myKeyObject = cryptovinaigrette.rainbowKeygen(save='./')

start = dt.now()
signature = cryptovinaigrette.rainbowKeygen.sign('cvPriv.pem', 'testFile.txt')
end = dt.now()
if args.v:
    print()
    print("Signed (from file) in", end - start, "seconds")

start = dt.now()
signature = cryptovinaigrette.rainbowKeygen.sign(myKeyObject.private_key, 'testFile.txt')
end = dt.now()
if args.v:
    print()
    print("Signed (from key object) in", end - start, "seconds")

print()
print("Checking testFile.txt")
start = dt.now()
print("Signature verification with file:", colored_binary(cryptovinaigrette.rainbowKeygen.verify('cvPub.pub', signature, 'testFile.txt')))
end = dt.now()
if args.v:
    print("Verified signature in", end - start, "seconds")

print()
print("Checking testFile.txt")
start = dt.now()
print("Signature verification with object :", colored_binary(cryptovinaigrette.rainbowKeygen.verify(myKeyObject.public_key, signature, 'testFile.txt')))
end = dt.now()
if args.v:
    print("Verified signature in", end - start, "seconds")

if args.v >= 2:
    print("Signature :", signature)

print()
print("Checking testFile2.txt")
start = dt.now()
print("Signature verification with tampered file :", colored_binary(cryptovinaigrette.rainbowKeygen.verify('rPub.rkey', signature, 'testFile2.txt')))
end = dt.now()
if args.v:
    print("Verified signature in", end - start, "seconds")

if args.v >= 2:
    print("Signature :", signature)

