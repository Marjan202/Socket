#!/usr/bin/env python
"""

ChangeLog:
    [2015-04-14] 0.1.1
        * Changing `IP Address` to `HOST` in command line help
        * Program name changed to `null_tunnel`
        * Test case was provided

    [2015-04-15] 0.2.0
        * Closing both sockets on zero length read. refer: http://stackoverflow.com/a/667710/680372
        * -R switch. Reusable tunnel, making new socket to the target server after closing and reestablishing the client socket.
        * Enhanced printing

    [2015-04-15] 0.2.1
        * Separating connection handling method, So, its ready to cast as a threaded server.

    [2015-04-15] 0.2.2
        * Enhanced printing
"""

import sys
import socket
import argparse
import time
import select
__version__ = '0.2.2'

parser = argparse.ArgumentParser(description='Creates a simple TCP port forwarder.')
parser.add_argument('-l', '--listen', required=True, metavar='HOST:PORT', help='The Host & port to listen on.')
parser.add_argument('-f', '--forward', required=True, metavar='HOST:PORT', help='The Host & port to to forward.')
parser.add_argument('-m', '--mtu', default=1400, type=int, metavar='MTU', help='Maximum read/write size. default: 1400')
parser.add_argument('-R', '--reusable', action="store_true", default=False, help='Reusable tunnel, making new socket to the target server after closing and reestablishing the client socket.')

KB = 1024
MB = KB**2
GB = KB**3
TB = KB**4


def format_size(s):
    if s > TB:
        return '%.2FTB' % (float(s) / TB)
    if s > GB:
        return '%.2FGB' % (float(s) / GB)
    if s > MB:
        return '%.2FMB' % (float(s) / MB)
    if s > KB:
        return '%.2FKB' % (float(s) / KB)
    return '%sB' % s


def handle_connection(client_conn, client_addr):
    # Create and connect the target socket
    print 'Connection from: %s:%s' % client_addr
    chunk_size = args.mtu
    target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    target_socket.connect(target)
    transfer_size = 0
    receive_size = 0
    loops = 0
    start_time = time.time()

    try:

        while True:
            loops += 1
            to_read = select.select(
                [client_conn, target_socket],
                [],
                [], .02)[0]

            if client_conn in to_read:
                data = client_conn.recv(chunk_size)
                if not data:
                    client_conn.close()
                    target_socket.close()
                    break
                transfer_size += len(data)
                target_socket.send(data)

            if target_socket in to_read:
                data = target_socket.recv(chunk_size)
                if not data:
                    client_conn.close()
                    target_socket.close()
                    break
                receive_size += len(data)
                client_conn.send(data)

            if loops % 10 == 0:
                elapsed_time = time.time() - start_time

                sys.stdout.write('\rSend: %s %s/s, Receive : %s %s/s       ' % (
                    format_size(transfer_size),
                    format_size(float(transfer_size) / elapsed_time),
                    format_size(receive_size),
                    format_size(float(receive_size) / elapsed_time)))
                sys.stdout.flush()
            # time.sleep(.001)
        print
    finally:
        if client_conn:
            client_conn.close()
        if target_socket:
            target_socket.close()


if __name__ == '__main__':
    args = parser.parse_args()

    listen_addr, listen_port = args.listen.split(':')
    listen_port = int(listen_port)
    listen = listen_addr, listen_port

    target_addr, target_port = args.forward.split(':')
    target_port = int(target_port)
    target = target_addr, target_port

    # Create and listen on the server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(listen)

    try:
        while True:
            server_socket.listen(3)
            handle_connection(*server_socket.accept())
            if not args.reusable:
                break

    except KeyboardInterrupt:
        print("\nCTRL+C pressed.")

