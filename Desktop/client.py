import socket

def connect(ip_address, port):
    '''
    connects to server and returns the client socket
    '''
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # connecting to the server
        client.connect((ip_address, int(port)))
        return client
    except Exception as err:
        return str(err)

# recording state
recording_active = False

# receiving and sending data from and to the server
def receive_send_data(client):
    ''' recieves and sends data from and to the server '''
    while True:
        try:
            client.send('200'.encode('ascii'))
        except Exception as err:
            print(str(err))
            client.close()
        
    
