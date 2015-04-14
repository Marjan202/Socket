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

    [2015-04-15] 0.3.0
        * Multi-threading

"""

import sys
import socket
import argparse
import time
import select
import threading

__version__ = '0.3.0'

parser = argparse.ArgumentParser(description='Creates a simple TCP port forwarder.')
parser.add_argument('-l', '--listen', required=True, metavar='[HOST:]PORT', help='The Host & port to listen on.')
parser.add_argument('-f', '--forward', required=True, metavar='[HOST:]PORT', help='The Host & port to to forward.')
parser.add_argument('-m', '--mtu', default=1400, type=int, metavar='MTU', help='Maximum read/write size. default: 1400')
parser.add_argument('-R', '--reusable', action="store_true", default=False,
                    help='Reusable tunnel, making new socket to the target server after closing and reestablishing the client socket.')
parser.add_argument('-t', '--threaded', action="store_true", default=False,
                    help='Implies -R. Act as a multi-thread server, so it can handle more than one connection simultaneously.')

KB = 1024
MB = KB ** 2
GB = KB ** 3
TB = KB ** 4


def format_size(s):
    if s > TB:
        return '%.2FTB' % (float(s) / TB)
    if s > GB:
        return '%.2FGB' % (float(s) / GB)
    if s > MB:
        return '%.2FMB' % (float(s) / MB)
    if s > KB:
        return '%.2FKB' % (float(s) / KB)
    return '%.2FB' % s


def get_address(addr_string):
    if ':' in addr_string:
        addr, port = addr_string.split(':')
    else:
        addr, port = '127.0.0.1', addr_string
    if not isinstance(port, int):
        port = int(port)
    return addr, port


def handle_connection(client_conn, client_addr):
    global transfer_size, receive_size
    # Create and connect the target socket
    print '\nConnection from: %s:%s' % client_addr
    chunk_size = args.mtu
    target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    target_socket.connect(target)

    try:

        while True:
            to_read = select.select(
                [client_conn, target_socket],
                [],
                [], .01)[0]

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
    finally:
        if client_conn:
            client_conn.close()
        if target_socket:
            target_socket.close()


def printing_job():
    global transfer_size, receive_size
    start_time = time.time()
    while True:
        threads = threading.active_count() - 2
        elapsed_time = time.time() - start_time

        sys.stdout.write('\rSend: %s %s/s, Receive : %s %s/s, Threads: %s     ' % (
            format_size(transfer_size),
            format_size(0 if not threads else float(transfer_size) / elapsed_time),
            format_size(receive_size),
            format_size(0 if not threads else float(receive_size) / elapsed_time),
            threads))
        sys.stdout.flush()

        time.sleep(.1)


if __name__ == '__main__':
    global transfer_size, receive_size

    transfer_size = 0
    receive_size = 0

    args = parser.parse_args()

    listen = get_address(args.listen)
    target = get_address(args.forward)

    # Create and listen on the server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(listen)

    printing_thread = threading.Thread(
        target=printing_job,
        name='nt_printing')
    printing_thread.daemon = True
    printing_thread.start()
    try:
        while True:
            if args.threaded:
                server_socket.listen(5)
                new_conn, new_addr = server_socket.accept()
                thread = threading.Thread(
                    target=handle_connection,
                    name='nt_%s_%s' % new_addr,
                    args=(new_conn, new_addr))
                thread.daemon = True
                thread.start()

            else:
                server_socket.listen(0)
                handle_connection(*server_socket.accept())
                if not args.reusable:
                    break

    except KeyboardInterrupt:
        print("\nCTRL+C pressed.")

    finally:
        if server_socket:
            server_socket.close()

