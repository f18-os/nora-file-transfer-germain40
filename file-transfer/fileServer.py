#! /usr/bin/env python3
import sys, re, socket, os, threading
from threading import Thread
from framedSock import FramedStreamSock
import params


switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

progname = "server"
paramMap = params.parseParams(switchesVarDefaults)

debug, listenPort = paramMap['debug'], paramMap['listenPort']

if paramMap['usage']:
    params.usage()

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listener socket
bindAddr = ("127.0.0.1", listenPort)
lsock.bind(bindAddr)
lsock.listen(5)
print("listening on:", bindAddr)
print_lock = threading.Lock()

class ServerThread(Thread):
    requestCount = 0            # one instance / class
    def __init__(self, sock, debug):
        Thread.__init__(self, daemon=True)
        self.fsock, self.debug = FramedStreamSock(sock, debug), debug
        self.start()
    def run(self):
        while True:
            msg = self.fsock.receivemsg()
            print(msg)
            if not msg:
                if self.debug: print(self.fsock, "server thread done")
                return
            if msg.decode() == 'FOF':
                f = open('Server_file.txt', 'w')
            msg = msg.decode()
            f.write(msg)
            msg = msg.encode()
            self.fsock.sendmsg(msg)

while True:
    sock, addr = lsock.accept()
    print_lock.acquire()
    ServerThread(sock, debug)