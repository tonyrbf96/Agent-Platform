from socket import *
import sys
import time

def broadcast_client(port, id_):
    # Create a UDP socket
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    sock.settimeout(5)

    server_address = ('255.255.255.255', port)
    message = f'broadcast_{id_}'
    try:
        # Send data
        sent = sock.sendto(message.encode(), server_address)

        # Receive response
        print('---------------------------------------')
        print(f'Esperando recibir información de {id_}...')
        data, server = sock.recvfrom(4096)
        print('Información recibida')
        print('---------------------------------------')

        return data.decode()
    finally:	
        sock.close()


def broadcast_server(port, id_, address):
    sock = socket(AF_INET, SOCK_DGRAM)
    server_address = ('', port)

    try:
        sock.bind(server_address)
    except Exception as e:
        print('No se puedo establecer la conexión con el servidor de broadcast')
        print(f'ERROR: {e}')
        return

    response = address
    while True:
        data, address = sock.recvfrom(4096)
        data = data.decode()
        print('---------------------------------------')
        print(f'ID: {id_}...')
        print(f'Recibiendo data: {data}')
        if data == f'broadcast_{id_}':
            print(f'Respondiendo a {address[0]}:{address[1]}...')
            sent = sock.sendto(response.encode(), address)
            print('Enviando la confirmación de vuelta')
        print('---------------------------------------')
        