
import socket
import random
import threading

# Get the IP address
def get_ipaddress():
    try:
        # Create a socket object and connect to a remote server (e.g., Google DNS)
        # This step is not required to get the local IP, but it ensures that you are connected to a network.
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        print(ip_address)
        return ip_address
    except Exception as err:
        return str(err)

# Get port number
def get_port():
    return random.randint(5000,65534)

# number of connected clients
number_of_clients = 0

# recording flag
recording_active = False

def bind(ip_address, port):
    #  create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # AF_INET : address family, IPv4
    # SOCK_STREAM : TCP
    # bind to the port
    server_socket.bind((ip_address, port))
    return server_socket



def listen(server_socket):
# queue up to 5 requests
    server_socket.listen(5)



# recording state
def handle_client(server_socket):
    while True:
        print("chal rha hai")
        client_socket, address = server_socket.accept()
        print(f"Connection from {address} has been established!")
        if client_socket.recv(1024).decode('ascii') == '200':
            number_of_clients += 1
            print(f"Number of connected clients: {number_of_clients}")
        

        

