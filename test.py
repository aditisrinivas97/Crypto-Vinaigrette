from Generators import *
from datetime import datetime as dt

class args: pass
args = args()
args.v = True

myKeyObject = rainbowKeygen()
    
start = dt.now()
myKeyObject.generate_keys()  
end = dt.now()
if args.v:
    print("Generated keys in", end - start, "seconds")

start = dt.now()
signature = rainbowKeygen.sign('rPriv.rkey', 'testFile.txt')
end = dt.now()
if args.v:
    print("Signed in", end - start, "seconds")


print("Checking testFile.txt")
start = dt.now()
print("Signature verification :", rainbowKeygen.verify('rPub.rkey', signature, 'testFile.txt'))
end = dt.now()
if args.v:
    print("Verified signature in", end - start, "seconds")

if args.v >= 2:
    print("Signature :", signature)

print("Checking testFile2.txt")
start = dt.now()
print("Signature verification :", rainbowKeygen.verify('rPub.rkey', signature, 'testFile2.txt'))
end = dt.now()
if args.v:
    print("Verified signature in", end - start, "seconds")

if args.v >= 2:
    print("Signature :", signature)

