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

myKeyObject = cryptovinaigrette.rainbowKeygen()

start = dt.now()
signature = cryptovinaigrette.rainbowKeygen.sign('rPriv.rkey', 'testFile.txt')
end = dt.now()
if args.v:
    print("Signed in", end - start, "seconds")


print("Checking testFile.txt")
start = dt.now()
print("Signature verification :", colored_binary(cryptovinaigrette.rainbowKeygen.verify('rPub.rkey', signature, 'testFile.txt')))
end = dt.now()
if args.v:
    print("Verified signature in", end - start, "seconds")

if args.v >= 2:
    print("Signature :", signature)

print("Checking testFile2.txt")
start = dt.now()
print("Signature verification :", colored_binary(cryptovinaigrette.rainbowKeygen.verify('rPub.rkey', signature, 'testFile2.txt')))
end = dt.now()
if args.v:
    print("Verified signature in", end - start, "seconds")

if args.v >= 2:
    print("Signature :", signature)

