from socket import *
import sys
import time

def broadcast_client(port, id_):
    # Create a UDP socket
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    # sock.settimeout(5)

    server_address = ('255.255.255.255', port)
    message = f'broadcast_{id_}'

    try:
        for i in range(5):
            # Send data
            sent = sock.sendto(message.encode(), server_address)

            # Receive response
            print('Esperando recibir información...')
            data, server = sock.recvfrom(4096)
            return data.decode()
    finally:	
        sock.close()


def broadcast_server(port, id_, address):
    sock = socket(AF_INET, SOCK_DGRAM)
    server_address = ('', port)

    sock.bind(server_address)

    response = address

    while True:
        data, address = sock.recvfrom(4096)
        data = data.decode()
        if data == f'broadcast_{id_}':
            print('Respondiendo...')
            sent = sock.sendto(response.encode(), address)
            print('Enviando la confirmación de vuelta')