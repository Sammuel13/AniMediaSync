#!/usr/bin/env python3
import socket
import threading

from QoL import hostSetup
from ChainingHashTable import ChainingHashTable
from ListaSequencial import Lista

lock = threading.Lock()

address, port = hostSetup('SERVER')

status = 0
clients = ChainingHashTable()
playlist = Lista()
time = duration = -1

def playlist_loader():
    global playlist
    global time
    global duration
    while True:
        while playlist.estaVazia(): pass
        with lock:    
            media = playlist.elemento(1)
        for connection in clients.values():
            connection.sendall(str.encode('PLAY ' + media))
        while int(time) < int(duration)-300 and duration != -1: pass
        with lock:
            playlist.next()


def client_handler(connection):
    with lock:
        clientKey = str(connection.getpeername()[0] + ':' + str(connection.getpeername()[1]))
        clients.put(clientKey, connection)
    global status
    global time
    global duration
    connection.send(str.encode('Connected! Type EXIT to leave.\nPLAY, EXIT: '))
    while True:
        data = connection.recv(2048)
        message = data.decode('utf-8').split()

        print(time,duration)

        if message[0] == 'UPT':
            with lock:
                try:
                    time = int(message[1])
                    duration = int(message[2])
                except: pass
        elif message[0].upper() == 'EXIT': break
        else:
            command_handler(message, status)

    connection.close()
    print('Disconnected from:',clientKey)
    with lock:
        clients.remove(clientKey)
    

def command_handler(message, status):
    global playlist
    args = message
    command = args.pop(0).upper()

    try:
        if command == 'PLAY':
            with lock:
                for connection in clients.values():
                    connection.sendall(str.encode('MSG Playing!'))
        
        elif command == 'PAUSE':
            with lock:
                for connection in clients.values():
                    connection.sendall(str.encode('MSG Paused!'))

        elif command == 'SEEK':
            with lock:
                for connection in clients.values():
                    connection.sendall(str.encode('SEEK '+args[0]))

        elif command == 'PLAYLIST':
            if not len(args):
                printPlaylist = 'MSG Playlist:\n'
                
                for i in playlist.iterable():
                    printPlaylist += i + '\n'
                for connection in clients.values():
                    connection.sendall(str.encode(printPlaylist))

            elif args[0].upper() == 'NEXT':
                if playlist.tamanho() <= 1:
                    response = 'MSG Playlist do not have more videos.'
                else:
                    with lock:
                        response = 'PLAY ' + playlist.next()
                for connection in clients.values():
                    connection.sendall(str.encode(response))

            elif args[0].upper() == 'ADD':
                try:
                    with lock:
                        playlist.inserir(args[2], int(args[1]))
                except:
                    with lock:
                        playlist.inserir(args[1])

            elif args[0].upper() == 'REMOVE':
                with lock:
                    playlist.remover(int(args[1]))
            
            elif args[0].upper() == 'CLEAR':
                with lock:
                    playlist.clear()

            elif args[0].upper() == 'SHUFFLE':
                with lock:
                    playlist.shuffle()
            
            elif args[0].upper() == 'REMOVEDUPPS':
                with lock:
                    playlist.removeDupps()
                
            elif args[0].upper() == 'REALOCATE':
                with lock:
                    playlist.realocate(int(args[1]), int(args[2]))
    except Exception as error:
        print(error)
        print(f'Command "{command}" with wrong or insufficient arguments')

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

    threading.Thread(target=playlist_loader, args=()).start()

    while True:
        accept_connections(ServerSocket)

start_server(address, port)
