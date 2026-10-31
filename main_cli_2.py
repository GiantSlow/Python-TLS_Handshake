import diffie_linux as DH
import RSAclass as rsa
import re
from hashlib import sha256
import socket
import threading
from HMAC import HMAC_using_SHA256
from AESclass_cli import AES
import textwrap

PEER_IP   = "192.168.2.147"
PORT = 5000

def get_info(cert, info):
    m = re.search(rf"<{info}>(.*)<\/{info}>", cert)
    return m

def verify_sign(cert):
    # Fetch values from the certificate
    server_rsa_e = int(get_info(cert, "RSA_public_key").group(1))
    server_rsa_n = int(get_info(cert, "RSAn").group(1))
    sig = int(get_info(cert, "sign").group(1))

    #verify
    body = get_info(cert, "cert").group(0)
    verify = rsa.unsign(sig, server_rsa_e, server_rsa_n)
    orig = sha256(body.encode())
    orig = int(orig.hexdigest(), 16)

    return orig == verify

def receive(conn,AES):
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                print("\n[Connection closed by peer]")
                break
            AES.updateState(data.decode())
            AES.decrypt()
            newmsg = AES.getMessage()

            print(f"\nServer> {data.decode()}")
            print(f"Server Decrypted> {newmsg}")
            print("Client> ", end="", flush=True)
        except Exception as e:
            print(e)
            break

def chat(conn, AES):
    threading.Thread(target=receive, args=(conn, AES), daemon=True).start()
    while True:
        msg = input("Client> ")
        if not msg:
            continue
        try:
            AES.updateState(msg)
            AES.encrypt()
            newmsg = AES.getMessage()
            conn.send(newmsg.encode())
        except Exception as e:
            print("[Send failed. Connection lost]")
            print(e)
            break

def run_client():
    s = socket.socket()
    print(f"\n  [Client] Connecting to {PEER_IP}:{PORT}")
    s.connect((PEER_IP, PORT))
    print(f"  [Client] Connected\n")
    certificate = str(s.recv(100000))
    signature_validation = verify_sign(certificate)
    print("signature validity: ", signature_validation)
    if not signature_validation:
        print("WARNING: SERVER FAILED RSA SIGNATURE")

    p,g, server_pub = int(get_info(certificate, "prime").group(1)), int(get_info(certificate, "generator").group(1)), int(get_info(certificate, "DH").group(1))
    _,_, cli_priv, cli_pub = DH.generate_public_val(p,g)
    s.send(str(cli_pub).encode())

    prekey = pow(server_pub,cli_priv,p).to_bytes(256)
    randhash = get_info(certificate, "randhash").group(1)
    randhash = bytes.fromhex(randhash)

    aes_key = HMAC_using_SHA256(prekey, randhash)
    print("common symmetric key: ", aes_key)
    aes_key = textwrap.wrap(aes_key,2)
    Nk = 8
    Nb = 4
    Nr = 14
    aes_session = AES(aes_key, Nk,Nb,Nr)

    chat(s, aes_session)
    


run_client()



# Start by greeting the server, send a simple "Hello"
# WAIT FOR CERTIFICATE 

# Fetching information from received
#f = open("cert.txt", "r")
#cert = f.read() # entire certificate
#body = get_info(cert, "cert").group(0)
#server_rsa_e = int(get_info(cert, "RSA_public_key").group(1))
#server_rsa_n = int(get_info(cert, "RSAn").group(1))
#sig = int(get_info(cert, "sign").group(1))
#
## verify signatures
#verify = rsa.unsign(sig, server_rsa_e, server_rsa_n)
#orig = sha256(body.encode())
#orig = int(orig.hexdigest(), 16)
#print(orig == verify)

# GENERATE DIFFIE AND SEND