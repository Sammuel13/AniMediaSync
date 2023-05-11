#!/usr/bin/env python3

import pyautogui

import socket
from _thread import *

HOST = '127.0.0.1'
PORT = 1234

status = ''

def client_handler(connection):
    connection.send(str.encode('Connected! Type EXIT to stop'))
    while True:
        data = connection.recv(2048)
        message = data.decode('utf-8').upper()

        if message == 'PLAY':
            pyautogui.press('playpause')
            if status != 'playing':
                connection.sendall(str.encode('Playing!'))
                status = 'playing'
            else:
                connection.sendall(str.encode('Paused!'))
                status = 'paused'

        if message == 'EXIT':
            connection.sendall(str.encode('Bye...'))
            break
    connection.close()

def accept_connections(ServerSocket):
    Client, address = ServerSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(client_handler, (Client, ))

def start_server(HOST, PORT):
    ServerSocket = socket.socket()
    try:
        ServerSocket.bind((HOST, PORT))
    except socket.error as e:
        print(str(e))
    print(f'Server is listing on the port {PORT}...')
    ServerSocket.listen()

    while True:
        accept_connections(ServerSocket)

start_server(HOST, PORT)
