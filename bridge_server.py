#!python

import sys
import getopt
import bridge

optlist, args = getopt.getopt(sys.argv[1:], 'l:c:', ['lock_port=', 'client_port='])

lock_port = None
client_port = None

for opt, arg in optlist:
	if opt in ('-l', '--lock_port'): lock_port = int(arg)
	elif opt in ('-c', '--client_port'): client_port = int(arg)

bridge_server = bridge.bridge_server(client_port, lock_port)
bridge_server.serve()