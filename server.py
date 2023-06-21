#!/usr/bin/env python3
import os
import socket
import threading
from QoL import hostSetup
from ChainingHashTable import ChainingHashTable
from ListaSequencial import Lista
os.environ["PATH"] = os.path.dirname(__file__) + os.pathsep + os.environ["PATH"]
import mpv
mpvPlayer = mpv.MPV(ytdl=True)
@mpvPlayer.property_observer('time-pos')
def time_observer(_name, value):
    print(value)

lock = threading.Lock()

address, port = hostSetup('SERVER')

status = ''
clients = ChainingHashTable()
playlist = Lista()

def playlist_loader():
    global playlist
    while True:
        while playlist.estaVazia(): pass
        with lock:
            if mpvPlayer.show_progress():
                mpvPlayer.play(playlist.next())
            


def client_handler(connection):
    with lock:
        clientKey = str(connection.getpeername()[0] + ':' + str(connection.getpeername()[1]))

        clients.put(clientKey, connection)
    global status
    connection.send(str.encode('Connected! Type EXIT to stop\nPLAY, EXIT: '))
    while True:
        data = connection.recv(2048)
        message = data.decode('utf-8')

        status = command_handler(message, status)

        if message.upper() == 'EXIT':
            connection.sendall(str.encode('Bye...'))
            break
    with lock:
        clients.remove(clientKey)
    connection.close()

def command_handler(message, status):
    global playlist
    args = message.split()
    command = args.pop(0).upper()

    print('progress')
    mpvPlayer.show_progress()

    # " ".join(args[1:]) for the playlist

    if command == 'PLAY':
        if status != 'playing':
            for connection in clients.values():
                connection.sendall(str.encode('Playing!'))
            return 'playing'
    
    elif command == 'PAUSE':
        for connection in clients.values():
            connection.sendall(str.encode('Paused!'))
        return 'paused'
    
    elif command == 'PLAYLIST':
        try:
            if args[0].upper == 'NEXT':
                if playlist.tamanho() <= 1:
                    print('Playlist do not have more videos')
                else:
                    with lock:
                        mpvPlayer.play(playlist.next())
                        mpvPlayer.wait_for_playback()
            
            elif args[0].upper() == 'ADD':
                try:
                    with lock:
                        playlist.inserir(args[2], int(args[1]))
                except:
                    with lock:
                        playlist.inserir(args[1])

            elif args[0].upper() == 'REMOVE':
                with lock:
                    playlist.remover(str(args[1]))
            
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
                    playlist.realocate(args[1], args[2])
        except:
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

    while True:
        accept_connections(ServerSocket)

start_server(address, port)
