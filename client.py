#!/usr/bin/env python3

#TODO gui with tkinter
import socket
import threading

from QoL import hostSetup

# import os
# os.environ["PATH"] = os.path.dirname(__file__) + os.pathsep + os.environ["PATH"]
# import mpv

# player = mpv.MPV()

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
print('Waiting for connection')

try:
    clientSocket.connect((address, port))
except socket.error as e:
    print(str(e))

response = clientSocket.recv(2048)
print(response.decode('utf-8'))

def server_listener():
    while True:
        response = clientSocket.recv(2048)
        if response.decode('utf-8') == 'Playing!' or response.decode('utf-8') == 'Paused!':
            keyboard.press(Key.media_play_pause)
        elif response.decode('utf-8') == 'Bye...': break
        print(response.decode('utf-8'))
        print('PLAY, EXIT: ')

threading.Thread(target=server_listener).start()

while True:
    command = input() #TODO change to key listener
    clientSocket.send(str.encode(command))
    if command.upper() == 'EXIT': break

clientSocket.close()