#!python

import sys
import getopt
import bridge
import socket

optlist, args = getopt.getopt(sys.argv[1:], 'a:p:c:', ['addr=', 'port=', 'command='])

addr = None
port = None
command = None

for opt, arg in optlist:
	if opt in ('-a', '--addr'): addr = arg
	elif opt in ('-p', '--port'): port = int(arg)
	elif opt in ('-c', '--command'): command = arg

# Intialize a socket to talk to the bridge server.
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((addr, port))
sock_file = sock.makefile('rw', 0) # read / write, unbuffered

# Write the command into the socket, read the response and print it.
sock_file.write(command + '\n')
response = sock_file.readline()
print response.strip()