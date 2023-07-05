import configparser
from validations import *

clientConfig = configparser.ConfigParser()
clientConfig.read('config.ini')

def read_from_ini(connectionSide):
    address = clientConfig[connectionSide]['address']
    port = int(clientConfig[connectionSide]['port'])
    return address, port

def write_on_ini(connectionSide, address='127.0.0.1', port='1234'):
    with open('config.ini', 'w') as configFile:
        clientConfig[connectionSide] = {'address': address, 'port': port}
        clientConfig.write(configFile)
        read_from_ini(connectionSide)
    return address, port

def hostSetup(connectionSide):
    try:
        address, port = read_from_ini(connectionSide)
    except:
        address, port = write_on_ini(connectionSide)

    while True:
        option = input(f'Proceed with the server "{address}:{port}"? (y/n) ').lower()
        if option == 'y':
            return address, int(port)
        if option == 'n':
            validHostAddress = validAddress()
            validHostPort = validPort()
            return write_on_ini(connectionSide, validHostAddress, validHostPort)
        print(f'{option} is not a valid option')
