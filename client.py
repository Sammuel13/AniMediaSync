#!/usr/bin/env python3

import pyautogui
import socket

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

while True:
    command = input('PLAY, EXIT: ')
    clientSocket.send(str.encode(command))
    response = clientSocket.recv(2048)
    if response.decode('utf-8') == 'Playing!' or response.decode('utf-8') == 'Paused!':
        pyautogui.press('playpause')
    print(response.decode('utf-8'))
clientSocket.close()