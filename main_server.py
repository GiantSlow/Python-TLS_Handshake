import RSAclass as rsa 
import json
import diffie_linux as dh
import random
from hashlib import sha256
import re
import time
import HMAC
import socket
import threading
import textwrap
from AESclass import AES
import time

PEER_IP   = ""
#put ip add of other computer
IS_SERVER = True 
#put other computer as false
PORT = 5000

def receive(conn, AES):
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                print("\n[Connection closed by peer]")
                break
            AES.updateState(data.decode())
            t1 = time.time()
            AES.decrypt()
            t2 = time.time()
            newmsg = AES.getMessage()
            print("Time Decrypted: ", (t2-t1))

            print(f"\nClient >{data.decode()}")
            print(f"Client Decrypted >{newmsg}")
            print("Server> ", end="", flush=True)
        except:
            break

def chat(conn, AES):
    threading.Thread(target=receive, args=(conn, AES), daemon=True).start()
    while True:
        msg = input("Server> ")
        if not msg:
            continue
        AES.updateState(msg)
        t1 = time.time()
        AES.encrypt()
        t2 = time.time()
        newmsg = AES.getMessage()
        print("Encryption time: ", (t2-t1))
        try:
            conn.send(newmsg.encode())
        except Exception as e:
            print("[Send failed. Connection lost]")
            print(e)
            break

def generate_cert():
    randhash = random.getrandbits(256)
    randhash = randhash.to_bytes(32)
    randhash = sha256(randhash).hexdigest()
    #print(bytearray.fromhex(randhash))

    p,g, server_priv, server_pub = dh.generate_public_val()
    rsa_session = rsa.RSA()

    # Generating information to send to the client
    cert_temp= f"<cert><RSA_public_key>{rsa_session.e}</RSA_public_key><RSAn>{rsa_session.n}</RSAn><prime>{p}</prime><generator>{g}</generator><DH>{server_pub}</DH><randhash>{randhash}</randhash></cert>"
    # Digital signature
    rsa_session.updatemsg(cert_temp.encode())
    rsa_session.sign()
    sig = rsa_session.signed
    cert_temp += f"<sign>{sig}</sign>"

    return cert_temp, server_priv, p, randhash

def run_server():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", PORT))
    s.listen(1)
    print(f"\n  [Server] Waiting for connection on port {PORT}")
    conn, addr = s.accept()
    print(f"  [Server] Connected: {addr[0]}\n")

    certificate, server_priv, p, randhash = generate_cert()
    randhash = bytes.fromhex(randhash)
    time.sleep
    conn.send(certificate.encode())
    
    cli_pub = int(conn.recv(2048))
    prekey = pow(cli_pub,server_priv,p).to_bytes(256)

    aes_key = HMAC.HMAC_SHA256(prekey,randhash)
    print("common symmetric key:", aes_key)

    aes_key = textwrap.wrap(aes_key,2)
    Nk = 8
    Nb = 4
    Nr = 14
    aes_session = AES(aes_key, Nk,Nb,Nr)

    chat(conn, aes_session)

run_server()
#bdaec08a7e6cdeca5de4d674ed68ce d ade4d674ed68ceda
# WAIT FOR CLIENT'S DIFFIE VALUES

# Then HMAC, and AES starts