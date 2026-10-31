import numpy as np
import multTables as mt

def sBoxVal(p, invTable):
    x0 = False
    x1 = True 
    subMat = np.array([
        [x1,x0,x0,x0,x1,x1,x1,x1],
        [x1,x1,x0,x0,x0,x1,x1,x1],
        [x1,x1,x1,x0,x0,x0,x1,x1],
        [x1,x1,x1,x1,x0,x0,x0,x1],
        [x1,x1,x1,x1,x1,x0,x0,x0],
        [x0,x1,x1,x1,x1,x1,x0,x0],
        [x0,x0,x1,x1,x1,x1,x1,x0],
        [x0,x0,x0,x1,x1,x1,x1,x1]
    ])
    subMat = subMat.T 
    subc = np.array([x0,x1,x1,x0,x0,x0,x1,x1])

    subMat = np.packbits(subMat).astype(np.uint8)
    subc = np.packbits(subc).astype(np.uint8)

    q = invTable[p]
    afftrans = np.bitwise_and(subMat, q)
    afftrans = np.packbits(np.bitwise_count(afftrans)%2).astype(np.uint8)
    afftrans = np.bitwise_xor(afftrans, subc)
    return afftrans[0]

def sBoxInit(invTable):
    sBox = []
    for i in range(2**8):
        sBox.append(sBoxVal(i, invTable))
    sBox = np.array(sBox, dtype=np.uint8)
    return sBox

if __name__=="__main__":
    x0 = False
    x1 = True 
    mx = np.array([x0,x0,x0,x0,x0,x0,x0,x1, x0,x0,x0,x1,x1,x0,x1,x1])
    xMat = mt.matInit()
    invTable = mt.invLookup(mx, xMat)
    multTab = mt.multLookup(xMat)

    sBox = sBoxInit(invTable)
    print(hex(sBox[0xc8]))
