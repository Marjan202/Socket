#!/usr/bin/env python

import socket 
import argparse
import time
from select import select
from Queue import Queue

parser = argparse.ArgumentParser(description='Creates a simple TCP port forwarder.')
parser.add_argument('-l', '--listen', required=True, metavar='IPADDRESS:PORT', help='The IP address & port to listen on.')
parser.add_argument('-f', '--forward', required=True, metavar='IPADDRESS:PORT', help='The IP address & port to to forward.')


def main(listen, target):
    
    # Create and listen on the server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(listen)
    server_socket.listen(1)
    client_conn, client_addr = server_socket.accept()
    
    # Create and connect the target socket
    target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    target_socket.connect(target) 
       
    target_buff = Queue()
    client_buff = Queue()
    chunk_size = 1400
    
    try:
        while True:
            try:
                
                to_write, to_read, ex = select(
                    [client_conn, target_socket],
                    [client_conn, target_socket],
                    []) 
                    
                if target_socket in to_read:
                    target_buff.put_nowait(target_socket.recv(chunk_size))
                    
                if client_conn in to_read:
                    target_buff.put_nowait(client_conn.recv(chunk_size))
                    
                if target_socket in to_write and not target_buff.empty():
                    target.socket.send(target_buff.get_nowait())
                  
                if client_conn in to_write and not client_buff.empty():
                    client_conn.send(client_buff.get_nowait())
                
            except KeyboardInterrupt:
                print "\nCTRL+C pressed."
                break
    
    finally:
        client_conn.close()
        target_socket.close()
        

if __name__ == '__main__':
	args = parser.parse_args()
	listen_addr, listen_port = args.listen.split(':')
	forward_addr, forward_port = args.forward.split(':')
	main((listen_addr, int(listen_port)), (forward_addr, int(forward_port)))
	
