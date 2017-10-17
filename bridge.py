import subprocess
import re
import socket


# Constants.
NODE_CMD = "/Users/tomrusso/.nvm/v0.10.40/bin/node"
SCRIPT_PATH = "/Users/tomrusso/code/alta/scripts"


# Class to represent a smart lock.
class lock:
	def __init__(self, lock_id, key):
		self.lock_id = lock_id
		self.key = key

	# Call the alta script to get the state of the lock.  Wait for the output of the command
	# and search for the state string in the output, and return as appropriate.
	def get_state(self):
		# Try to get the state of the lock.  If the alta script returns an error code, we return "unknown".
		try:
			output = subprocess.check_output("lock=%s key=%s status=AUG_STAT_LOCK_STATE %s %s/get_status.js" % (self.lock_id, self.key, NODE_CMD, SCRIPT_PATH), shell=True, stderr=subprocess.STDOUT) 
		except subprocess.CalledProcessError:
			return "unknown"

		# Parse the output.  If we don't find one of the expected states, we return "unknown".
		if re.search(r'kAugLockState_Locked', output): return "locked"
		elif re.search(r'kAugLockState_Unlocked', output): return "unlocked"
		else: return "unknown"


	# Call the alta script to lock the lock.  Wait for the output, search for the success message
	# and return "success" or "failure", depending on the output of the alta script.
	def lock(self):
		# Try to lock the lock.  If the alta script returns and error code, we return "failure".
		try:
			output = subprocess.check_output("lock=%s key=%s %s %s/lock_check.js" % (self.lock_id, self.key, NODE_CMD, SCRIPT_PATH), shell=True, stderr=subprocess.STDOUT)
		except subprocess.CalledProcessError:
			return "failure"

		# Parse the output.  If we don't find text indicating success or that the lock is already locked, we return "failure".
		if re.search(r'This lock/unlock script was successful!!', output): return "success"
		elif re.search(r'authenticated!\nFinished', output): return "already locked"
		else: return "failure"


	# Call the alta script to unlock the lock.  Wait for the output, search for the success message
	# and return "success" or "failure", depending on the output of the alta script.
	def unlock(self):
		# Try to unlock the lock.  If the alta script returns an error code, we return "failure".
		try:
			output = subprocess.check_output("lock=%s key=%s %s %s/unlock_check.js" % (self.lock_id, self.key, NODE_CMD, SCRIPT_PATH), shell=True, stderr=subprocess.STDOUT) 
		except subprocess.CalledProcessError:
			return "failure"

		# Parse the output.  If we don't find text indicating success or that the lock is already unlocked, we return "failure".
		if re.search(r'This lock/unlock script was successful!!', output): return "success"
		elif re.search(r'authenticated!\nFinished', output): return "already unlocked"
		else: return "failure"


# Class for the server that communicates directly with the lock.
class lock_server:
	def __init__(self, lock, bridge_addr, lock_port):
		self.lock = lock
		self.bridge_addr = bridge_addr
		self.lock_port = lock_port

	def serve(self):
		while True:
			# Intialize a socket to talk to the bridge server.
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.connect((self.bridge_addr, self.lock_port))
			self.sock_file = self.sock.makefile('rw', 0) # read / write, unbuffered

			# Read commands, handle them and send responses.
			while True:
				command = self.sock_file.readline()
				if not command: break
				command = command.strip()
				print "received command " + command
				
				# Respond to the command.  All we do is call the function corresponding to the command, and write its output
				# back to the bridge server.
				if command == "state":
					result = self.lock.get_state()
					self.sock_file.write(result + '\n')
					print "wrote response " + result
				elif command == "lock":
					result = self.lock.lock()
					self.sock_file.write(result + '\n')
					print "wrote response " + result
				elif command == "unlock":
					result = self.lock.unlock()
					self.sock_file.write(result + '\n')
					print "wrote response " + result
				else:
					self.sock_file.write("unknown command\n")
					print "wrote response unknown command"


# Class for the bridge server.
class bridge_server:
	def __init__(self, client_port, lock_port):
		# Initialize the socket the client connects to.
		self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.client_sock.bind(('', client_port))

		# Initialize the socket the lock server connects to.
		self.lock_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.lock_sock.bind(('', lock_port))

	def serve(self):
		# First, wait for the lock server to connect.  We can't do anything else until that happens.
		self.lock_sock.listen(1)
		self.lock_conn, self.lock_addr = self.lock_sock.accept()
		self.lock_file = self.lock_conn.makefile('rw', 0) # read / write, unbuffered

		print "lock server connected"

		# Next, we loop, accepting connections from clients and forwarding the commands they send to the lock server,
		# and forwarding the responses from the lock server back to the client.
		self.client_sock.listen(1)
		while True:
			self.client_conn, self.client_addr = self.client_sock.accept()
			self.client_file = self.client_conn.makefile('rw', 0) # read / write, unbuffered

			print "client connected"

			while True:
				# Read the command from the client and send it to the lock server, logging both the read and the write.
				command = self.client_file.readline()
				if not command: break
				command = command.strip()
				print "received command " + command
				self.lock_file.write(command + '\n')
				print "wrote command " + command

				# Read the response from the lock server and send it to the client, logging both the read and the write.
				response = self.lock_file.readline()
				if not response: break
				response = response.strip()
				print "received response " + response
				self.client_file.write(response + '\n')
				print "wrote response " + response


# Class for the client.
class lock_client: pass
