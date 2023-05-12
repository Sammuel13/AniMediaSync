#!/usr/bin/env python3

import pyautogui
import socket
import threading

# import os
# os.environ["PATH"] = os.path.dirname(__file__) + os.pathsep + os.environ["PATH"]
# import mpv

# player = mpv.MPV()

host = '127.0.0.1'
port = 1234

clientSocket = socket.socket()
print('Waiting for connection')

try:
    clientSocket.connect((host, port))
except socket.error as e:
    print(str(e))

response = clientSocket.recv(2048)
print(response.decode('utf-8'))

def server_listener():
    while True:
        response = clientSocket.recv(2048)
        if response.decode('utf-8') == 'Playing!' or response.decode('utf-8') == 'Paused!':
            pyautogui.press('playpause')
        print(response.decode('utf-8'))
        print('PLAY, EXIT: ')

threading.Thread(target=server_listener).start()

while True:
    command = input()
    clientSocket.send(str.encode(command))
    
clientSocket.close()