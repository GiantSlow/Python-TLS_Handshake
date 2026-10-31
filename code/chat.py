
import socket
import threading

PEER_IP   = ""
#put ip add of other computer
IS_SERVER = True 
#put other computer as false
PORT = 5000

def receive(conn):
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                print("\n[Connection closed by peer]")
                break
            print(f"\n  Peer → {data.decode()}")
            print("  You  → ", end="", flush=True)
        except:
            break

def chat(conn):
    threading.Thread(target=receive, args=(conn,), daemon=True).start()
    print("\n  Type a message and press Enter.\n")
    while True:
        msg = input("  You  → ")
        if not msg:
            continue
        try:
            conn.send(msg.encode())
        except:
            print("[Send failed. Connection lost]")
            break

def run_server():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", PORT))
    s.listen(1)
    print(f"\n  [Server] Waiting for connection on port {PORT}...")
    conn, addr = s.accept()
    print(f"  [Server] Connected: {addr[0]}\n")
    chat(conn)

def run_client():
    s = socket.socket()
    print(f"\n  [Client] Connecting to {PEER_IP}:{PORT}...")
    s.connect((PEER_IP, PORT))
    print(f"  [Client] Connected!\n")
    chat(s)

if IS_SERVER:
    run_server()
else:
    run_client()
