#!/usr/bin/env python3

#TODO gui with tkinter
import socket
import threading
import time as clock

from QoL import hostSetup

from python_mpv_jsonipc import MPV

mpv = MPV(ytdl=True)

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
            mpv.play(response[1])
            print(f'"{response[1]}" is now playing.')
            mpv.command("set_property","pause", False)

        elif response[0] == 'MSG':
            print(" ".join(response[1:]))

            if response[1] == 'Playing!':
                # keyboard.press(Key.media_play_pause)
                mpv.command("set_property","pause", False)

            elif response[1] == 'Paused!':
                mpv.command("set_property","pause", True)

        elif response[0] == 'SEEK':
            seek = response[1]
            mpv.command("set_property", "playback-time", seek)

        print('PLAY, EXIT: ')

def update_time():
    while True:
        try:
            clock.sleep(1)
            time = mpv.command("get_property", "time-pos")
            duration = mpv.command("get_property", "duration")
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

mpv.terminate()