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

    def playlist_loader(self):                                           # Função responsável pela lista de reprodução de cada party
        while len(self.parties) != 0:
            for party in self.parties.values():
                while party.playlist.is_empty(): sleep(1)                # Espera por vídeo na lista
                with self.lock:
                    party.video_url = party.playlist.get_current_media() # Define como a mídia atual
                #     party.video_is_playing = True
                sleep(3)                                                 # Sleep necessário para o funcionamento, porém não interfere na logica
                party_members = party.get_members()
                for connection in party_members:                         # Envia a mensagem para reproduzir o vídeo da lista à todos da party
                    connection.sendall(str.encode('PLAY ' + party.video_url))
                while party.video_position < 96: sleep(1)                # Aguarda o vídeo acabar com uma margem de erro
                with self.lock:
                    # party.video_is_playing = False
                    party.playlist.get_next_media()                      # Remove o primeiro vídeo da lista, visto que foi reproduzido

    def set_party(self, connection):                                     # Função responsável por definir a party de cada usuário
        partiesStr = '| '
        for i in self.parties.keys():
            partiesStr += i + ' | '
        connection.sendall(str.encode('MSG PARTY_SETUP ' + partiesStr))  # Mensagem contendo a lista de parties disponíveis para entrar
        setup = ['']
        while setup[0] not in ['CREATE', 'JOIN']:                        # Validação do input
            data = connection.recv(2048)
            setup = data.decode('utf-8').upper().split()

        if setup[0] == 'CREATE':
            try:                                                         # Verifica a existência de uma party com o nome dado
                party = self.parties.get(' '.join(setup[1:]))
                connection.sendall(str.encode('ERROR 102'))
                party = self.set_party(connection)                       # Com falha, faz-se uma nova tentativa
            except:
                party = Party(' '.join(setup[1:]))
                with self.lock:
                    self.parties.put(' '.join(setup[1:]), party)         # Com sucesso, a nova party é guardada

        elif setup[0] == 'JOIN':
            try:
                party = self.parties.get(' '.join(setup[1:]))            # Verifica a existência de uma party com o nome dado
            except:
                connection.sendall(str.encode('ERROR 103'))
                party = self.set_party(connection)                       # Com falha, faz-se uma nova tentativa
        
        return party                                                     # Devolve a party, seja criada ou escolhida

    def client_handler(self, connection):
     
        party = self.set_party(connection)                               # Define a party do cliente

        with self.lock:
            clientKey = str(connection.getpeername()[0] + ':' + str(connection.getpeername()[1]))
            party.add_member(clientKey, connection)                      # Guarda o cliente na hashtable da party
            self.clients.put(clientKey, connection)                      # Guarda o cliente na hashtable contendo todos os clientes do servidor

            if len(self.parties) == 1 and party.get_member_count() == 1: # Com ao menos um cliente, o playlist_loader() é executado
                threading.Thread(target=self.playlist_loader, args=()).start()

        connection.send(str.encode('MSG CONNECTED'))
        while True:
            data = connection.recv(2048)
            message = data.decode('utf-8').split()                       # A mensagem do cliente é recebida e decodificada

            if message[0] == 'UPT':                                      # Caso seja uma mensagem de atualização das
                with self.lock:                                          # informações do vídeo, as mesmas serão guardadas
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
                self.command_handler(message, party)                     # Em outro caso, trata-se de uma possível mensagem de comando

        connection.close()                                               # Se o loop foi interrompido, o cliente quer desconectar-se
        print('Disconnected from:', clientKey)
        with self.lock:                                                  # É feita a sua remoção das hashtables
            party.remove_member(clientKey)
            self.clients.remove(clientKey)
            if party.get_member_count() == 0:                            # Caso vazia, a party também é removida
                self.parties.remove(party.name)

    def command_handler(self, message, party):                           # Função responsável por interpretar comandos de clientes
        party_members = party.get_members()
        args = message
        command = args.pop(0).upper()                                    # São separados os comandos dos argumentos

        try:                                                             # A seguir, econtram-se todos os comandos
            if command == 'PLAY':                                        # Em cada um deles, a mensagem é
                with self.lock:                                          # repassada para TODOS os clientes da party
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
                    if party.playlist.get_playlist_length() == 0:        # Verifica se há vídeos na playlist
                        response = 'MSG EMPTY_PLAYLIST'
                    else:
                        response = 'PLAYLIST '                           # Gera uma string de impressão da playlist na tela
                        for i in party.playlist.get_all_media():
                            response += i + '\n'
                    for connection in party_members:
                        connection.sendall(str.encode(response))
                elif args[0].upper() == 'NEXT':
                    if party.playlist.get_playlist_length() <= 1:        # Verifica se há próximo vídeo a ser reproduzido
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
                for connection in party_members:                         # Caso não seja nenhum comando acima         
                    connection.sendall(str.encode('ERROR 104'))          # É informado o desconhecimento do comando
        except Exception as e:
            # print(e)
            for connection in party_members:                             # No caso de algum erro, há um problema com algum
                connection.sendall(str.encode('ERROR 101'))              # parâmetro inseriodo em algum comando

    def accept_connections(self, server_socket):                         # Função responsável por aceitar conexões com clientes
        client, address = server_socket.accept()
        print('Connected to: ' + address[0] + ':' + str(address[1]))
                                                                         # uma thread é chamada para o cliente conectado
        threading.Thread(target=self.client_handler, args=(client,)).start()

    def start_server(self):                                              # Função para se iniciar o servidor
        server_socket = socket.socket()
        try:
            server_socket.bind((self.address, self.port))
        except socket.error as e:
            print(str(e))
        print(f'Server is listening on port {self.port}...')
        server_socket.listen()

        while True:
            self.accept_connections(server_socket)                       # Espera pela conexão de novos clientes

# Usage:
address, port = hostSetup('SERVER')                                      # Inicia a configuração do ip e da porta
server = Server(address, port)
server.start_server()                                                    # Inicia o servidor
