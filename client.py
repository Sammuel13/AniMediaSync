#!/usr/bin/env python3

# import pyautogui
import socket
import threading

# import os
# os.environ["PATH"] = os.path.dirname(__file__) + os.pathsep + os.environ["PATH"]
# import mpv

# player = mpv.MPV()

################################################################

from pynput.keyboard import Key, Listener, Controller
keyboard = Controller()

# def on_press(key):
#     print('{0} pressed'.format(key))


# def on_release(key):
#     print('{0} release'.format(key))
#     if key == Key.esc:
#         return False

# with Listener(on_press=on_press, on_release=on_release) as listener:
#     listener.join()

################################################################


#TODO https://docs.python.org/3/library/configparser.html
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