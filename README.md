# Socket
import socket 

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_addr = ('localhost',10003)
#print 'starting up on %s port %s' % server_addr
s.bind(server_addr)
s.listen(2)

while True:
	print 'waiting for a connection'
	conn, client_addr = s.accept()
	while True:
		data = conn.recv(64)
		if ( data == 'q' or data == 'Q'):
       			conn.close()
			break;
		else:
			print "RECIEVED:" , data
			data = raw_input ( "SEND( TYPE q or Q to Quit):" )
        		if (data <> 'Q' and data <> 'q'):
            			conn.sendall(data)
    			else:
         			conn.send(data)
         			conn.close()
         			break
	break


ooooooooo
