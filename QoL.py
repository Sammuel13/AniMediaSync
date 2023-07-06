import configparser
from validations import *

clientConfig = configparser.ConfigParser()
clientConfig.read('config.ini')

def read_from_ini(connectionSide):                                       # Função lê do arquivo config.ini e carrega
    address = clientConfig[connectionSide]['address']                    # as informações do ip e da porta
    port = int(clientConfig[connectionSide]['port'])
    return address, port

def write_on_ini(connectionSide, address='127.0.0.1', port='1234'):      # No caso da ausência do mesmo, um novo arquivo 
    with open('config.ini', 'w') as configFile:                          # config.ini é gerado com as informações padrão
        clientConfig[connectionSide] = {'address': address, 'port': port}
        clientConfig.write(configFile)
        read_from_ini(connectionSide)                                    # As informações padrão são carregados
    return address, port

def hostSetup(connectionSide):                                           # Espera-se CLIENT ou SERVER como parâmetro
    try:                                                                 # para ser feita a busca correta no arquivo de configurações
        address, port = read_from_ini(connectionSide)
    except:
        address, port = write_on_ini(connectionSide)

    while True:                                                          # Validação simples do ip e da porta
        option = input(f'Proceed with the server "{address}:{port}"? (y/n) ').lower()
        if option == 'y':
            return address, int(port)
        if option == 'n':
            validHostAddress = validAddress()
            validHostPort = validPort()
            return write_on_ini(connectionSide, validHostAddress, validHostPort)
        print(f'{option} is not a valid option')
