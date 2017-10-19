#!python

import sys
import getopt
import bridge

optlist, args = getopt.getopt(sys.argv[1:], 'l:k:a:p:', ['lock=', 'key=', 'addr=', 'port='])

lock_id = None
key = None
addr = None
port = None

for opt, arg in optlist:
	if opt in ('-l', '--lock'): lock_id = arg
	elif opt in ('-k', '--key'): key = arg
	elif opt in ('-a', '--addr'): addr = arg
	elif opt in ('-p', '--port'): port = int(arg)

lock = bridge.lock(lock, key)
lock_server = bridge.lock_server(lock, addr, port)
lock_server.serve()

print "lock: %s\nkey: %s\naddr: %s\nport: %s" % (lock, key, addr)