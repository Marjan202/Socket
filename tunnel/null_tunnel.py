#!/usr/bin/env python
"""

ChangeLog:
    [2015-04-14] [0.1.1]
        * Passing None instead of empty list to select function
        * Changing `IP Address` to `HOST` in command line help
        * Program name changed to `null_tunnel`
        * Test case was provided

"""

import socket
import argparse
from select import select
__version__ = '0.1.1'

parser = argparse.ArgumentParser(description='Creates a simple TCP port forwarder.')
parser.add_argument('-l', '--listen', required=True, metavar='HOST:PORT', help='The Host & port to listen on.')
parser.add_argument('-f', '--forward', required=True, metavar='HOST:PORT', help='The Host & port to to forward.')
parser.add_argument('-m', '--mtu', default=1400, type=int, metavar='MTU', help='Maximum read/write size. default: 1400')


def main(listen, target):
    
    # Create and listen on the server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(listen)
    server_socket.listen(1)
    client_conn, client_addr = server_socket.accept()
    
    # Create and connect the target socket
    target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    target_socket.connect_ex(target)

    chunk_size = args.mtu

    try:
        while True:
            to_read = select(
                [client_conn, target_socket],
                None,
                None)[0]

            if client_conn in to_read:
                target_socket.send(client_conn.recv(chunk_size))

            if target_socket in to_read:
                client_conn.send(target_socket.recv(chunk_size))

    except KeyboardInterrupt:
        print("\nCTRL+C pressed.")

    finally:
        client_conn.close()
        target_socket.close()

if __name__ == '__main__':
    args = parser.parse_args()
    listen_addr, listen_port = args.listen.split(':')
    forward_addr, forward_port = args.forward.split(':')
    main((listen_addr, int(listen_port)), (forward_addr, int(forward_port)))

