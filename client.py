#!/usr/bin/env python3

import socket
host = '127.0.0.1'
port = 1234

ClientSocket = socket.socket()
print('Waiting for connection')

try:
    ClientSocket.connect((host, port))
except socket.error as e:
    print(str(e))

while True:
    Input = input('PLAY, EXIT: ')
    ClientSocket.send(str.encode(Input))
    Response = ClientSocket.recv(2048)
    print(Response.decode('utf-8'))
ClientSocket.close()