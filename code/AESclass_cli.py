import numpy as np
import time
import multTables as mt
import sbox
import keyexp
import textwrap

class AES:
    def __init__(self, key, Nk, Nb, Nr):
        self.bytesarr = []
        self.states = []
        self.Nb = Nb 
        self.Nk = Nk 
        self.Nr = Nr

        # get all the tables
        x1 = True
        x0 = False
        self.mx = np.array([x0,x0,x0,x0,x0,x0,x0,x1, x0,x0,x0,x1,x1,x0,x1,x1])
        self.xMat = mt.matInit()        
        self.invTable = mt.invLookup(self.mx, self.xMat)
        self.multTab = mt.multLookup(self.xMat)
        self.sBox = sbox.sBoxInit(self.invTable)

        # Mixing and shifting matrices
        self.aMat = np.array([
            [0x02,0x03,0x01,0x01],
            [0x01,0x02,0x03,0x01],
            [0x01,0x01,0x02,0x03],
            [0x03,0x01,0x01,0x02]
        ], dtype=np.uint8)
        self.ishift = np.array([
            [0,1,2,3],
            [1,2,3,0],
            [2,3,0,1],
            [3,0,1,2]
        ])
        self.jshift = np.array([0,1,2,3])

        # Inverse mixing and shifting
        self.Invishift = np.array([
            [0,3,2,1],
            [1,0,3,2],
            [2,1,0,3],
            [3,2,1,0]
        ])
        self.InvaMat = np.array([
            [0x0e,0x0b,0x0d,0x09],
            [0x09,0x0e,0x0b,0x0d],
            [0x0d,0x09,0x0e,0x0b],
            [0x0b,0x0d,0x09,0x0e]
        ])

        # Inverse S-Box
        idx = np.arange(2**8)
        self.invsBox = np.array(sorted(zip(self.sBox, idx)))[:,1]

        # Key schedule
        self.w = keyexp.keyExp(key, Nb, Nk, Nr, self.sBox, self.mx)
    
    def mixColumns(self,p):
        for i in range(p.shape[0]):
            p[i] = np.bitwise_xor.reduce(self.multTab[self.aMat,p[i]], 1)
    
    def InvmixColumns(self,p):
        for i in range(p.shape[0]):
            p[i] = np.bitwise_xor.reduce(self.multTab[self.InvaMat,p[i]], 1)
    
    def shiftRows(self,s):
        return s[self.ishift,self.jshift]
    
    def InvshiftRows(self,s):
        return s[self.Invishift,self.jshift]
    
    def Round(self, state, rkey):
        state = self.sBox[state]
        state = self.shiftRows(state)
        self.mixColumns(state)
        state = np.bitwise_xor(state, rkey)
        return state
    
    def InvRound(self, state, rkey):
        state = self.InvshiftRows(state) 
        state = self.invsBox[state]
        state = np.bitwise_xor(state,rkey)
        self.InvmixColumns(state)
        return state

    def encrypt(self):
        for i in range(len(self.states)):
            state = np.bitwise_xor(self.states[i], self.w[0:self.Nb])

            for r in range(1,self.Nr):
                state = self.Round(state, self.w[r*self.Nb:(r+1)*self.Nb])
            
            state = self.sBox[state]
            state = self.shiftRows(state)
            state = np.bitwise_xor(state, self.w[self.Nr*self.Nb : (self.Nr+1)*self.Nb])

            self.states[i] = state

    def decrypt(self):
        for i in range(len(self.states)):
            state = np.bitwise_xor(self.states[i], self.w[self.Nr*self.Nb : (self.Nr+1)*self.Nb])

            for r in range(self.Nr-1, 0, -1):
                state = self.InvRound(state, self.w[r*self.Nb : (r+1)*self.Nb])
            state = self.InvshiftRows(state)
            state = self.invsBox[state]
            state = np.bitwise_xor(state, self.w[0:self.Nb])

            self.states[i] = state
    
    def updateState(self, instr):
        padding = len(instr) % 32
        if padding != 0:
            instr += "0"*(32-padding)
        self.bytesarr = textwrap.wrap(instr,2)
        self.bytesarr = [int(i, 16) for i in self.bytesarr]
        self.states = []

        # Initialize state matrices
        for i in range(0,len(self.bytesarr),4*self.Nb):
            state = np.array([self.bytesarr[i:i+4], self.bytesarr[i+4:i+8], self.bytesarr[i+8:i+12], self.bytesarr[i+12:i+16]], dtype=np.uint8)
            self.states.append(state)
    def getMessage(self):
        msg = ""
        for state in self.states:
            state = state.flatten()
            for b in state:
                #msg += hex(b)[2:]
                msg += f"{b:#0{4}x}"[2:]
        return msg
    
if __name__=="__main__":
    np.set_printoptions(formatter={'int':hex})

    key = "2b 7e 15 16 28 ae d2 a6 ab f7 15 88 09 cf 4f 3c"
    key = "000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f"
    key = textwrap.wrap(key,2)
    Nk = 8
    N = 4
    Nr = 14

    #i = "bdaec08a7e6cdeca5de4d674ed68cedade4d674ed68ceda"
    i = "bdaec08a7e6cdeca5de4d674ed68cedade4d674ed68ceda00000000000000000"
    a = AES(key, Nk,N,Nr)
    a.updateState(i)
    print("--------------input-----------------")
    print(a.states)
    t1 = time.time()
    a.encrypt()
    t2 = time.time()
    print("----------------encrypted-----------------")
    print(a.states)
    print(t2-t1)

    a.decrypt()
    print("---------------decrypted-----------------")
    print(a.states)
    
    newmsg = a.getMessage()
    print(newmsg)
    a.updateState(newmsg)
    a.decrypt()
    print(a.getMessage())
