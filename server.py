import socket
import threading
from time import sleep
from QoL import hostSetup
from ChainingHashTable import ChainingHashTable
from Playlist import Playlist
from Video import Video

class Server:
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.lock = threading.Lock()
        self.clients = ChainingHashTable()
        self.playlist = Playlist()
        self.video = Video()

    def playlist_loader(self):
        while True:
            while self.playlist.is_empty(): sleep(1)
            with self.lock:
                self.video.url = self.playlist.get_current_media()
                self.video.is_playing = True
            for connection in self.clients.values():
                connection.sendall(str.encode('PLAY ' + self.video.url))
            while self.video.progress < 98: sleep(1)
            with self.lock:
                self.video.is_playing = False
                self.playlist.get_next_media()

    def client_handler(self, connection):
        with self.lock:
            clientKey = str(connection.getpeername()[0] + ':' + str(connection.getpeername()[1]))
            self.clients.put(clientKey, connection)
        connection.send(str.encode('MSG CONNECTED'))
        while True:
            data = connection.recv(2048)
            message = data.decode('utf-8').split()

            if message[0] == 'UPT':
                with self.lock:
                    try:
                        self.video.current_time = float(message[1])
                        self.video.progress = float(message[2])
                        self.video.duration = float(message[3])
                    except:
                        self.video.current_time = self.video.progress = self.video.duration = 0
            elif message[0].upper() == 'EXIT':
                break
            else:
                self.command_handler(message)

        connection.close()
        print('Disconnected from:', clientKey)
        with self.lock:
            self.clients.remove(clientKey)

    def command_handler(self, message):
        args = message
        command = args.pop(0).upper()

        try:
            if command == 'PLAY':
                with self.lock:
                    self.video.is_playing = True
                    for connection in self.clients.values():
                        connection.sendall(str.encode('MSG PLAYING'))

            elif command == 'PAUSE':
                with self.lock:
                    self.video.is_playing = False
                    for connection in self.clients.values():
                        connection.sendall(str.encode('MSG PAUSED'))

            elif command == 'SEEK':
                with self.lock:
                    for connection in self.clients.values():
                        connection.sendall(str.encode('SEEK ' + args[0]))

            elif command == 'PLAYLIST':
                if not len(args):
                    playlistStr = 'PLAYLIST '
                    for i in self.playlist.get_all_media():
                        playlistStr += i + '\n'
                    for connection in self.clients.values():
                        connection.sendall(str.encode(playlistStr))
                elif args[0].upper() == 'NEXT':
                    if self.playlist.get_playlist_length() <= 1:
                        response = 'MSG EMPTY_PLAYLIST'
                    else:
                        with self.lock:
                            self.video.url = self.playlist.next()
                            response = 'PLAY ' + self.video.url
                            self.video.is_playing = True
                    for connection in self.clients.values():
                        connection.sendall(str.encode(response))
                elif args[0].upper() == 'ADD':
                    try:
                        with self.lock:
                            self.playlist.add_media(args[2], int(args[1]))
                    except:
                        with self.lock:
                            self.playlist.add_media(args[1])
                elif args[0].upper() == 'REMOVE':
                    with self.lock:
                        self.playlist.remove_media(int(args[1]))
                elif args[0].upper() == 'CLEAR':
                    with self.lock:
                        self.playlist.clear_playlist()
                elif args[0].upper() == 'SHUFFLE':
                    with self.lock:
                        self.playlist.shuffle_playlist()
                elif args[0].upper() == 'REMOVEDUPPS':
                    with self.lock:
                        self.playlist.remove_duplicates()
                elif args[0].upper() == 'REALOCATE':
                    with self.lock:
                        self.playlist.realocate_media(int(args[1]), int(args[2]))
        except:
            # error_message = f'Command "{command}" with wrong or insufficient arguments'
            for connection in self.clients.values():
                connection.sendall(str.encode('ERROR 101'))

    def accept_connections(self, server_socket):
        client, address = server_socket.accept()
        print('Connected to: ' + address[0] + ':' + str(address[1]))
        threading.Thread(target=self.client_handler, args=(client,)).start()
        return client

    def start_server(self):
        server_socket = socket.socket()
        try:
            server_socket.bind((self.address, self.port))
        except socket.error as e:
            print(str(e))
        print(f'Server is listening on port {self.port}...')
        server_socket.listen()

        threading.Thread(target=self.playlist_loader, args=()).start()

        while True:
            self.accept_connections(server_socket)

# Usage:
address, port = hostSetup('SERVER')
server = Server(address, port)
server.start_server()
