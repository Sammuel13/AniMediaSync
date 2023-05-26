def validPort():
    while True:
        port = input('Enter the host port:\n')
        try:
            port = int(port)
            if port <= 65535 and port >= 1024:
                return port
            else: print('The informed port is out of range')
        except: print('The informed port is not a valid port')

def validAddress():
    while True:
        address = input('Enter the host address:\n')
        try:
            addressList = address.split('.')
            if len(addressList) != 4:
                print('The informed address is not a valid address')
            else:
                isValid = True
                for i in addressList:
                    i = int(i)
                    if not (i >= 0 and i <= 255):
                        isValid = False
                if not isValid: print('The informed address is out of range')
                else: break
        except:
            print('The informed address is not a valid address')
    return address
