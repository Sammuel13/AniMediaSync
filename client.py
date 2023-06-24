#!/usr/bin/env python3

#TODO gui with tkinter
import socket
import threading
import time as clock

from QoL import hostSetup

import vlc

player = vlc.MediaPlayer()

################################################################

from pynput.keyboard import Key, Listener, Controller, KeyCode
keyboard = Controller()

# code from https://pynput.readthedocs.io/en/latest/keyboard.html
keypressed = ''
def on_press(key):
    global keypressed
    try:
        keypressed = key.char
    except: keypressed = ''

listener = Listener(on_press=on_press)
listener.start()

address, port = hostSetup('CLIENT')

clientSocket = socket.socket()
print('Waiting for connection.')

try:
    clientSocket.connect((address, port))
except socket.error as e:
    print(str(e))

response = clientSocket.recv(2048)
print(response.decode('utf-8'))

def server_listener():
    while True:
        response = clientSocket.recv(2048)
        response = response.decode('utf-8').split()
        
        if not response:
            break
        if response[0] == 'PLAY':
            media = vlc.Media(response[1])
            player.set_media(media)
            player.play()
            print(f'"{response[1]}" is ready to play.')
            player.set_pause(1)

        elif response[0] == 'MSG':
            print(" ".join(response[1:]))

            if response[1] == 'Playing!':
                # keyboard.press(Key.media_play_pause)
                player.play()
                player.set_pause(0)

            elif response[1] == 'Paused!':
                player.set_pause(1)

        elif response[0] == 'SEEK':
            seek = int(response[1])/100
            player.set_position(seek)

        print('PLAY, EXIT: ')

def update_time():
    while True:
        try:
            clock.sleep(1)
            time = player.get_time()
            duration = player.get_length()
            message = 'UPT' + ' ' + str(time) + ' ' + str(duration)
            clientSocket.send(str.encode(message))
        except: break

threading.Thread(target=server_listener).start()
threading.Thread(target=update_time).start()

while True:
    
    command = input()
    clientSocket.send(str.encode(command))
    if command.upper() == 'EXIT':
        input('Connection closed.')
        break