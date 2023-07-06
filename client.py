import socket
import threading
import time as clock
from QoL import hostSetup
from python_mpv_jsonipc import MPV

class Client:
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.clientSocket = socket.socket()
        self.mpv = MPV(ytdl=True)
        self.dictionary = {}

    def connect(self):                                                   # Função responsável por tentar se conectar ao servidor
        print('Waiting for connection...')
        self.clientSocket.connect((self.address, self.port))
        print('Connected!')
        # print('\nCommand: ')

    def receive_response(self):                                          # Dunção responsável por receber e interpretar
        while True:                                                      # as mensagens do servidor
            response = self.clientSocket.recv(2048)
            
            if not response:
                break

            response = response.decode('utf-8').split(' ')               # A mensagem é decodificada e guardada

            if response[0] == 'PLAY':
                self.mpv.play(response[1])                               # Executa o vídeo passado como parâmetro
                print(f'"{response[1]}" is now playing.')
                self.mpv.command("set_property", "pause", True)          # Linhas 33 à 36 possuem o intuito de uma melhor 
                self.mpv.command("set_property", "pause", False)         # sincronização no caso do travamento de algum cliente
                clock.sleep(.5)
                self.mpv.command("set_property", "playback-time", 0)

            elif response[0] == 'MSG':                                   # Traduz as mensagens do servidor de acordo com
                print(self.dictionary[response[1]])                      # o dicionário que foi carregado inicialmente

                if response[1] == 'PLAYING':
                    self.mpv.command("set_property", "pause", False)

                elif response[1] == 'PAUSED':
                    self.mpv.command("set_property", "pause", True)

                elif response[1] == 'PARTY_SETUP':
                    print('List of Parties:')
                    print(' '.join(response[2:]))
            
            elif response[0] == 'SEEK':
                seek = response[1]
                self.mpv.command("set_property", "playback-time", seek)

            elif response[0] == 'PLAYLIST':
                print(self.dictionary[response.pop(0)])
                print(' '.join(response))

            elif response[0] == 'ERROR':
                print(self.dictionary[response[1]])

            print('\nCommand: ')

    def update_time(self):                                               # Função responsável por periodicamente enviar ao
        while True:                                                      # sevidor, informações sobre o vídeo em reprodução
            try:
                clock.sleep(.2)
                time = self.mpv.command("get_property", "time-pos")
                percent = self.mpv.command("get_property", "percent-pos")
                duration = self.mpv.command("get_property", "duration")
                message = 'UPT' + ' ' + str(time) + ' ' + str(percent) + ' ' + str(duration)
                self.clientSocket.send(str.encode(message))
            except:
                break

    def set_dictionary(self):                                            # Assim foi feito para futuramente ser adaptado à
        #TODO add support for different languages                        # outras linguas com facilidade
        self.dictionary = {
            "CONNECTED": "Joined the party!",                            # No momento, a função apenas carrega as mensagens
            "PARTY_SETUP": "Create or enter on a party to proceed.",     # definidas ao lado
            "PLAYING": "Playing!",
            "PAUSED": "Paused!",
            "PLAYLIST": "Playlist:",
            "EMPTY_PLAYLIST": "Playlist does not have more videos.",
            "101": "Command with wrong or insufficient arguments.",
            "102": "Party already exists.",
            "103": "Party does not exist.",
            "104": "Invalid command.",
        }

    def start(self):                                                     # Função responsável por iniciar o cliente
        self.set_dictionary()                                            # Carrega o dicionário
        try:
            self.connect()                                               # Tenta conectar-se ao servidor
        except:
            input('The server could not be contacted.')
            self.mpv.terminate()                                         # Em caso de falha, o programa é encerrado
            exit(0)

        threading.Thread(target=self.receive_response).start()           # Dá início às threads de recebimento de mensagem
        threading.Thread(target=self.update_time).start()                # e de atualização das informações do vídeo

        while True:
            command = input()                                            # É na thread principal que os comandos do cliente são inseridos
            self.clientSocket.send(str.encode(command))
            if command.upper() == 'EXIT':
                input('Connection closed.')
                break

        self.mpv.terminate()                                             # No caso de encerramento do loop, o programa é encerrado

# Usage:
address, port = hostSetup('CLIENT')
client = Client(address, port)
client.start()