#!/usr/bin/env python3

import socket
import threading
from QoL import hostSetup

lock = threading.Lock()

address, port = hostSetup('SERVER')

status = ''
clients = []

def client_handler(connection):
    with lock:
        clients.append(connection)
    global status
    connection.send(str.encode('Connected! Type EXIT to stop\nPLAY, EXIT: '))
    while True:
        data = connection.recv(2048)
        message = data.decode('utf-8').upper()

        status = command_broadcast(message, status)

        if message == 'EXIT':
            connection.sendall(str.encode('Bye...'))
            break
    with lock:
        clients.remove(connection)
    connection.close()

#TODO Thinking of changing the broadcast strategy to some sort of communication between Threads
def command_broadcast(command, status):
    if command == 'PLAY':
        if status != 'playing':
            for connection in clients:
                connection.sendall(str.encode('Playing!'))
            return 'playing'
        else:
            for connection in clients:
                connection.sendall(str.encode('Paused!'))
            return 'paused'

def accept_connections(ServerSocket):
    Client, address = ServerSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    threading.Thread(target=client_handler, args=(Client, )).start()
    return Client

def start_server(address, port):
    ServerSocket = socket.socket()
    try:
        ServerSocket.bind((address, port))
    except socket.error as e:
        print(str(e))
    print(f'Server is listening on the port {port}...')
    ServerSocket.listen()

    while True:
        accept_connections(ServerSocket)

start_server(address, port)
