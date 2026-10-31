import random
import subprocess

def generate_public_val(p = False, g = False):
    if not (p and g):
        p = int(subprocess.check_output(["openssl", "prime", "-generate", "-bits", "2048"]))
        g = random.randint(2,p-1)

    priv=random.randint(1,p-1)
    pub = pow(g,priv,p)
    return p,g, priv, pub

def secret_key(other_public,self_private, p):
    key=pow(other_public,self_private,p)
    return key 

if __name__ == "__main__":
    p,g, A_priv, A_pub = generate_public_val()
    _,_, B_priv, B_pub = generate_public_val(p,g)

    B_key = secret_key(A_pub, B_priv, p)
    A_key = secret_key(B_pub, A_priv, p)

    if A_key==B_key:
        print("Success, both computers have the same key.")
        print("prime = ", p)
        print("generator = ", g)
        print("A's key=",A_key)
        print("B's key=",B_key)

