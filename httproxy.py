#!/usr/bin/env python3
import sys
import ssl
import socket
import threading

def connect(addr):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    s.connect((addr, 443))
    s = ssl.wrap_socket(s)
    return s

def recv(conn):
    ret = b""
    while(ret[-4:] != b"\r\n\r\n"):
        rcv = conn.recv(4096)
        ret += rcv
    return ret

def getHost(req):
    ret = b""
    for i in req.split(b"\r\n"):
        if(i.startswith(b"Host:") or i.startswith(b"host:")):
            ret = i.split(b":")[1].strip()
            break
    return ret

def handle(conn):
    req = recv(conn)
    dest = getHost(req)
    if(not dest):
        print("[!] Missing Host field!")
        return conn.close()
    nc = connect(dest)
    print("       Routing request to %s" % dest.decode())
    nc.sendall(req)
    res = recv(nc)
    conn.sendall(res)
    nc.close()
    conn.close()

def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 443
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    s.bind(("", port))
    s.listen(89)
    s = ssl.wrap_socket(s, certfile="./server.pem", server_side=True)
    print("[*] Serving HTTPS on 0.0.0.0 on port %i" % (port))
    while(True):
        conn, addr = s.accept()
        print("[!] Connection received from %s" % addr[0])
        t = threading.Thread(target=handle, args=(conn,))
        t.start()

if(__name__ == "__main__"):
    main()
