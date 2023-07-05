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

    def connect(self):
        print('Waiting for connection...')
        self.clientSocket.connect((self.address, self.port))
        print('Connected!')
        print('\nCommand: ')

    def receive_response(self):
        while True:
            response = self.clientSocket.recv(2048)
            
            if not response:
                break

            response = response.decode('utf-8').split(' ')

            if response[0] == 'PLAY':
                self.mpv.play(response[1])
                self.mpv.command("set_property", "pause", True)
                clock.sleep(.5)
                print(f'"{response[1]}" is now playing.')
                self.mpv.command("set_property", "pause", False)
                self.mpv.command("set_property", "playback-time", 0)

            elif response[0] == 'MSG':
                print(self.dictionary[response[1]])

                if response[1] == 'PLAYING':
                    self.mpv.command("set_property", "pause", False)

                elif response[1] == 'PAUSED':
                    self.mpv.command("set_property", "pause", True)
            
            elif response[0] == 'SEEK':
                seek = response[1]
                print(seek)
                self.mpv.command("set_property", "playback-time", seek)

            elif response[0] == 'PLAYLIST':
                response[0] = self.dictionary[response[0]] + '\n'
                print(' '.join(response))

            elif response[0] == 'ERROR':
                print(self.dictionary[response[1]])

            print('\nCommand: ')

    def update_time(self):
        while True:
            try:
                clock.sleep(.2)
                time = self.mpv.command("get_property", "time-pos")
                percent = self.mpv.command("get_property", "percent-pos")
                duration = self.mpv.command("get_property", "duration")
                message = 'UPT' + ' ' + str(time) + ' ' + str(percent) + ' ' + str(duration)
                self.clientSocket.send(str.encode(message))
            except:
                break

    def set_dictionary(self):
        #TODO add support for different languages
        self.dictionary = {
            "PLAYING": "Playing!",
            "PAUSED": "Paused!",
            "PLAYLIST": "Playlist:",
            "EMPTY_PLAYLIST": "Playlist does not have more videos.",
            "ERROR 101": "Command with wrong or insufficient arguments.",
        }

    def start(self):
        self.set_dictionary()
        try:
            self.connect()
        except:
            input('The server could not be contacted.')
            self.mpv.terminate()
            exit(0)
            
        response = self.clientSocket.recv(2048)

        threading.Thread(target=self.receive_response).start()
        threading.Thread(target=self.update_time).start()

        while True:
            command = input()
            self.clientSocket.send(str.encode(command))
            if command.upper() == 'EXIT':
                input('Connection closed.')
                break

        self.mpv.terminate()

# Usage:
address, port = hostSetup('CLIENT')
client = Client(address, port)
client.start()