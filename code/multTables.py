import numpy as np
import time

def deg(p):
    if np.any(p):
        i = np.nonzero(p)[0][0]
        return p.size - 1 - i
    else:
        return -1

#should convert this to bits rather than np arrays?
def polydiv(num, denom):
    x1 = True
    x0 = False
    q = np.zeros_like(denom)
    r = num
    dnum = deg(r)
    ddenom = deg(denom)
    while np.any(r) and dnum >= ddenom:
        tmp = dnum - ddenom
        q[-tmp-1] = q[-tmp-1] ^ x1
        r = np.logical_xor(r, np.roll(denom, -tmp))
        dnum = deg(r)
    return q, r



def matmul(extern,intern):
    mat = []
    for i in range(intern.shape[0]):
        x = np.logical_xor.reduce(intern[:,i]*extern,1)
        mat.append(x)
    return np.array(mat).T

def matInit():
    x1 = True
    x0 = False
    I = np.array([
        [x1,x0,x0,x0,x0,x0,x0,x0],
        [x0,x1,x0,x0,x0,x0,x0,x0],
        [x0,x0,x1,x0,x0,x0,x0,x0],
        [x0,x0,x0,x1,x0,x0,x0,x0],
        [x0,x0,x0,x0,x1,x0,x0,x0],
        [x0,x0,x0,x0,x0,x1,x0,x0],
        [x0,x0,x0,x0,x0,x0,x1,x0],
        [x0,x0,x0,x0,x0,x0,x0,x1],
    ])
    xt = np.array([
        [x0,x1,x0,x0,x0,x0,x0,x0],
        [x0,x0,x1,x0,x0,x0,x0,x0],
        [x0,x0,x0,x1,x0,x0,x0,x0],
        [x1,x0,x0,x0,x1,x0,x0,x0],
        [x1,x0,x0,x0,x0,x1,x0,x0],
        [x0,x0,x0,x0,x0,x0,x1,x0],
        [x1,x0,x0,x0,x0,x0,x0,x1],
        [x1,x0,x0,x0,x0,x0,x0,x0],
    ])
    xMat = [I, xt]
    for i in range(2,8):
        mat = matmul(xt, xMat[-1])
        xMat.append(mat)
    xMat = np.array(xMat)
    return xMat

def polyMultMat(q, xMat):
    return np.logical_xor.reduce(np.logical_and(np.flip(q),xMat.T).T)

def polyMult(p,q, xMat):
    return np.logical_xor.reduce(p*polyMultMat(q, xMat),1)

def convert16bits(p):
    amiss = 16-p.size
    return np.append(np.zeros(amiss, dtype=bool), p)

def multLookup(xMat):
    multTable = []
    for i in range(0,2**8):
        curr = []
        p = np.unpackbits(np.uint8(i)).astype(bool)
        mat = polyMultMat(p, xMat)
        # This can probably be vectorized, but it doesn't matter since
        # the table is fixed
        for j in range(0, 2**8):
            q = np.unpackbits(np.uint8(j)).astype(bool)
            prod = np.logical_xor.reduce(q*mat,1)
            nprod = np.packbits(prod).astype(np.uint8)[0]
            curr.append(nprod)
        multTable.append(curr)
    return np.array(multTable)

def euclid816(b,c,xMat):
    #assume deg c = 8 
    #       deg b = 16
    #a(x) = m(x)
    x1 = True
    x0 = False
    r0, r1 = b, np.pad(c, (8,0))
    x_0, y_0 = np.array([x0,x0,x0,x0,x0,x0,x0,x1]), np.array([x0,x0,x0,x0,x0,x0,x0,x0]) #b's
    x_1, y_1 = np.array([x0,x0,x0,x0,x0,x0,x0,x0]), np.array([x0,x0,x0,x0,x0,x0,x0,x1]) #c's

    q, r = polydiv(r0,r1)

    q, r = np.resize(np.roll(q, -8), 8), np.resize(np.roll(r, -8), 8)

    x = np.logical_xor(x_0, polyMult(x_1,q, xMat))
    y = np.logical_xor(y_0, polyMult(y_1,q, xMat))
    
    r0 = np.resize(np.roll(r1, -8), 8)
    x_0, y_0 = x_1, y_1
    r1 = r
    x_1, y_1 = x, y

    while np.any(r1):

        q, r = polydiv(r0,r1)
        x = np.logical_xor(x_0, polyMult(x_1,q, xMat))
        y = np.logical_xor(y_0, polyMult(y_1,q, xMat))
        
        r0 = r1
        x_0, y_0 = x_1, y_1
        r1 = r
        x_1, y_1 = x, y
    return y_0

def displaypoly(p):
    n = deg(p)
    lead = np.nonzero(p)[0][0]
    out = f"x^{n}"
    for i in range(lead+1, p.size):
        if p[i]:
            out += f" +x^{n - (i-lead)}"

    return out

def invLookup(mx, xMat):
    x1 = True
    x0 = False
    byte0 = np.array([x0,x0,x0,x0,x0,x0,x0,x0])
    byte0 = np.packbits(byte0).astype(np.uint8)[0]
    invTable = [byte0]

    for i in range(1,2**8):
        p = np.unpackbits(np.uint8(i)).astype(bool)
        inv = euclid816(mx,p, xMat)
        ninv = np.packbits(inv).astype(np.uint8)[0]
        invTable.append(ninv)
    invTable = np.array(invTable)

    return invTable



if __name__=="__main__":
    x1 = True
    x0 = False
    mx = np.array([x0,x0,x0,x0,x0,x0,x0,x1, x0,x0,x0,x1,x1,x0,x1,x1])

    #initialization
    xMat = matInit()
    invTable = invLookup(mx, xMat)
    multTab = multLookup(xMat)

    p = np.array([x0,x1,x0,x1, x0,x1,x1,x1])
    q = np.array([x1,x0,x0,x0, x0,x0,x1,x1])
    pn = np.packbits(p).astype(np.int8)
    qn = np.packbits(q).astype(np.int8)
    prod = multTab[pn,qn]
    nprod = np.unpackbits(prod).astype(bool)
    print(nprod)
    
    t1 = time.time()
    print(multTab[qn, invTable[qn]])
    t2 = time.time()
    print(t2-t1)
    # much faster

    np.set_printoptions(formatter={'int':hex})
