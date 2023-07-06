import socket
import threading
from time import sleep
from QoL import hostSetup
from ChainingHashTable import ChainingHashTable
# from Playlist import Playlist
# from Video import Video
from Party import Party

class Server:
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.lock = threading.Lock()
        self.clients = ChainingHashTable()
        self.parties = ChainingHashTable()

    def playlist_loader(self):
        while len(self.parties) != 0:
            for party in self.parties.values():
                while party.playlist.is_empty(): sleep(1)
                with self.lock:
                    party.video_url = party.playlist.get_current_media()
                #     party.video_is_playing = True
                sleep(3)
                party_members = party.get_members()
                for connection in party_members:
                    connection.sendall(str.encode('PLAY ' + party.video_url))
                while party.video_position < 96: sleep(1)
                with self.lock:
                    # party.video_is_playing = False
                    party.playlist.get_next_media()

    def set_party(self, connection):
        partiesStr = '| '
        for i in self.parties.keys():
            partiesStr += i + ' | '
        connection.sendall(str.encode('MSG PARTY_SETUP ' + partiesStr))
        setup = ['']
        while setup[0] not in ['CREATE', 'JOIN']:
            data = connection.recv(2048)
            setup = data.decode('utf-8').upper().split()

        if setup[0] == 'CREATE':
            try:
                party = self.parties.get(' '.join(setup[1:]))
                connection.sendall(str.encode('ERROR 102'))
                party = self.set_party(connection)
            except:
                party = Party(' '.join(setup[1:]))
                with self.lock:
                    self.parties.put(' '.join(setup[1:]), party)

        elif setup[0] == 'JOIN':
            try:
                party = self.parties.get(' '.join(setup[1:]))
            except:
                connection.sendall(str.encode('ERROR 103'))
                party = self.set_party(connection)
        
        return party

    def client_handler(self, connection):
     
        party = self.set_party(connection)

        with self.lock:
            clientKey = str(connection.getpeername()[0] + ':' + str(connection.getpeername()[1]))
            party.add_member(clientKey, connection)
            self.clients.put(clientKey, connection)

            if len(self.parties) == 1 and party.get_member_count() == 1:
                threading.Thread(target=self.playlist_loader, args=()).start()

        connection.send(str.encode('MSG CONNECTED'))
        while True:
            data = connection.recv(2048)
            message = data.decode('utf-8').split()

            if message[0] == 'UPT':
                with self.lock:
                    try:
                        party.video_time = float(message[1])
                        party.video_position = float(message[2])
                        party.video_duration = float(message[3])
                    except:
                        party.video_time = 0
                        party.video_position = 0
                        party.video_duration = 0
            elif message[0].upper() == 'EXIT':
                break
            else:
                self.command_handler(message, party)

        connection.close()
        print('Disconnected from:', clientKey)
        with self.lock:
            party.remove_member(clientKey)
            if party.get_member_count() == 0:
                self.parties.remove(party.name)
            self.clients.remove(clientKey)

    def command_handler(self, message, party):
        party_members = party.get_members()
        args = message
        command = args.pop(0).upper()

        try:
            if command == 'PLAY':
                with self.lock:
                    # party.video_is_playing = True
                    for connection in party_members:
                        connection.sendall(str.encode('MSG PLAYING'))

            elif command == 'PAUSE':
                with self.lock:
                    # party.video_is_playing = False
                    for connection in party_members:
                        connection.sendall(str.encode('MSG PAUSED'))

            elif command == 'SEEK':
                with self.lock:
                    for connection in party_members:
                        connection.sendall(str.encode('SEEK ' + args[0]))

            elif command == 'PARTY':
                # if not len(args):
                #     membersStr = '| '
                #     for i in party_members:
                #         membersStr += i + ' | '
                if args[0].upper() == 'NAME':
                    with self.lock:
                        for connection in party_members:
                            connection.sendall(str.encode('MSG ' + party.name))

            elif command == 'PLAYLIST':
                if not len(args):
                    if party.playlist.get_playlist_length() == 0:
                        response = 'MSG EMPTY_PLAYLIST'
                    else:
                        response = 'PLAYLIST '
                        for i in party.playlist.get_all_media():
                            response += i + '\n'
                    for connection in party_members:
                        connection.sendall(str.encode(response))
                elif args[0].upper() == 'NEXT':
                    if party.playlist.get_playlist_length() <= 1:
                        response = 'MSG EMPTY_PLAYLIST'
                    else:
                        with self.lock:
                            party.video_url = party.playlist.get_next_media()
                            # party.video_is_playing = True
                        response = 'PLAY ' + party.video_url
                    for connection in party_members:
                        connection.sendall(str.encode(response))
                elif args[0].upper() == 'ADD':
                    with self.lock:
                        party.playlist.add_media(' '.join(args[1:]))
                elif args[0].upper() == 'REMOVE':
                    with self.lock:
                        party.playlist.remove_media(int(args[1]))
                elif args[0].upper() == 'CLEAR':
                    with self.lock:
                        party.playlist.clear_playlist()
                elif args[0].upper() == 'SHUFFLE':
                    with self.lock:
                        party.playlist.shuffle_playlist()
                elif args[0].upper() == 'REMOVEDUPPS':
                    with self.lock:
                        party.playlist.remove_duplicates()
                elif args[0].upper() == 'REALOCATE':
                    with self.lock:
                        party.playlist.realocate_media(int(args[1]), int(args[2]))
        
            else:
                for connection in party_members:
                    connection.sendall(str.encode('ERROR 104'))
        except Exception as e:
            print(e)
            for connection in party_members:
                connection.sendall(str.encode('ERROR 101'))

    def accept_connections(self, server_socket):
        client, address = server_socket.accept()
        print('Connected to: ' + address[0] + ':' + str(address[1]))

        threading.Thread(target=self.client_handler, args=(client,)).start()

    def start_server(self):
        server_socket = socket.socket()
        try:
            server_socket.bind((self.address, self.port))
        except socket.error as e:
            print(str(e))
        print(f'Server is listening on port {self.port}...')
        server_socket.listen()

        while True:
            self.accept_connections(server_socket)

# Usage:
address, port = hostSetup('SERVER')
server = Server(address, port)
server.start_server()
