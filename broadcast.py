from socket import *
import sys
import time

def broadcast_client(port):
    # Create a UDP socket
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    # sock.settimeout(5)

    server_address = ('255.255.255.255', port)
    message = 'pfg_ip_broadcast_cl'

    try:
        while True:
            # Send data
            print('sending: ' + message)
            sent = sock.sendto(message.encode(), server_address)

            # Receive response
            print('waiting to receive')
            data, server = sock.recvfrom(4096)
            if data.decode('UTF-8') == 'pfg_ip_response_serv':
                print('Received confirmation')
                return str(server)
            else:
                print('Verification failed')
            print('Trying again...')
    finally:	
        sock.close()


def broadcast_server(port):
    sock = socket(AF_INET, SOCK_DGRAM)
    server_address = ('', port)

    sock.bind(server_address)

    response = 'pfg_ip_response_serv'

    while True:
        data, address = sock.recvfrom(4096)
        data = data.decode()
        print('Received ' + str(len(data)) + ' bytes from ' + str(address) )
        print('Data:' + data)
        
        if data == 'pfg_ip_broadcast_cl':
            print('responding...')
            sent = sock.sendto(response.encode(), address)
            print('Sent confirmation back')