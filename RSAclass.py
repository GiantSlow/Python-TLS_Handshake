import subprocess
from hashlib import sha256
import numpy as np
import time

class RSA:
    def __init__(self):
        p = int(subprocess.check_output(["openssl", "prime", "-generate", "-bits", "2048"]))
        q = int(subprocess.check_output(["openssl", "prime", "-generate", "-bits", "2048"]))
        self.primes = [p,q]
        self.n = self.primes[0]*self.primes[1]
        self.totient = (self.primes[0]-1)*(self.primes[1]-1)
        self.d = max(self.primes)
        self.e = pow(self.d, -1, self.totient)
        self.msg = ""
        self.hashDigest = 0
        self.signed = 0
    def encrypt(self):
        return pow(self.msg, self.e, mod=self.n)
    def sign(self):
        hash = sha256(self.msg)
        self.hashDigest = int(hash.hexdigest(), 16)
        self.signed = pow(self.hashDigest, self.d, mod=self.n)
    def updatemsg(self,msg):
        self.msg = msg
    
def unsign(cipher,e,n):
    return pow(cipher, e, mod=n)

if __name__=="__main__":
    r = RSA()
    s = RSA()
    print(r.d)
    print("\n")
    print(s.d)
    #msg = "Google.com, use this key: alskdjfldasjfklasdjfklasjdflkjasldkfjlkasjdfklajsdlkfjaslkdjfklasdjfklasjdfklsadjfklasjdflksadjf, alskdjflksajdfklasjdlkfjaslkdjflkajsdklfjaksdjflkasjdlkfjalksdjflkasjlfdkasjdlfkajsdlkfjaslkdfjlaksjdfklajsdlkfjaklsdjfa"
    #msg = msg.encode("ascii")
    #r.updatemsg(msg)
    #r.sign()
    #print(f"original hash: {r.hashDigest}")
    #print(f"signed hash: {r.signed}")
#
    #reverse = unsign(r.signed, r.e, r.n)
    #print(f"verified hash: {reverse}")
    #print(r.hashDigest == reverse)


