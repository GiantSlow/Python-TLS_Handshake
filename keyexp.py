import numpy as np
import multTables as mt 
import sbox 

def Rcon(i,mx):
    if i<9:
        return np.array([2**(i-1), 0,0,0], dtype=np.uint8)
    else:
        x0 = False 
        x1 = True
        x = np.array([x0,x0,x0,x0, x0,x0,x0,x0, x0,x0,x0,x0, x0,x0,x0,x0], dtype=bool)
        x[16-i] = x1
        _, r = mt.polydiv(x, mx)
        r = np.packbits(r).astype(np.uint8)[1]
        return np.array([r, 0,0,0], dtype=np.uint8)

def displayHex(ls):
    s = ""
    for i in ls:
        s += hex(i)[2:]
    return s

def keyExp(key, Nb, Nk, Nr, sBox, mx):
    w=[]
    for i in range(Nk):
        a0 = int(key[i*4], 16)
        a1 = int(key[i*4+1], 16)
        a2 = int(key[i*4+2], 16)
        a3 = int(key[i*4+3], 16)
        word = np.array([a0,a1,a2,a3], dtype=np.uint8)
        w.append(word)

    for i in range(Nk, Nb*(Nr+1)):
        temp = w[i-1]
        if (i%Nk) == 0:
            temp = np.roll(temp, -1)
            subW = sBox[temp]
            temp = np.bitwise_xor(subW, Rcon(int(i/Nk),mx))
        elif (Nk>6) and (i%Nk == 4):
            temp = sBox[temp]
        temp = np.bitwise_xor(w[i-Nk], temp)
        w.append(temp)
        #print(f"{i}: {displayHex(temp)}")
    return np.array(w)

if __name__=="__main__":
    x0 = False
    x1 = True 
    mx = np.array([x0,x0,x0,x0,x0,x0,x0,x1, x0,x0,x0,x1,x1,x0,x1,x1])
    xMat = mt.matInit()
    invTable = mt.invLookup(mx, xMat)
    multTab = mt.multLookup(xMat)

    sBox = sbox.sBoxInit(invTable)

    Nk = 8
    Nb = 4
    Nr = 14
    key = "60 3d eb 10 15 ca 71 be 2b 73 ae f0 85 7d 77 81 1f 35 2c 07 3b 61 08 d7 2d 98 10 a3 09 14 df f4"
    key = key.split()
    
    w = keyExp(key, Nb, Nk, Nr, sBox, mx)