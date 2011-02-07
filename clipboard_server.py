import socket
import threading, thread
import traceback
import sys
import re
import cliputil
from ncrypt.cipher import DecryptCipher, CipherType

new_client_matcher = re.compile(r"CSHELO:" +	#beginning header
				"((\d{,3}\.){3}(\d{,3})):" +	#ip address, more or less, should be sanitized before use
				"([0-9]):" +					#port
				"OLEHSC")						#ending header

class ClipboardServer(threading.Thread):
	kill_received = False
	def __init__(self, conf, logger, client, clipboard=None):
		try:
			threading.Thread.__init__(self)
			self.logger = logger
			self.conf = conf
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.sock.settimeout(0.5)
			if 'port' in conf:
				self.sock.bind(('', int(conf['port'])))
			else:
				self.sock.bind(('', 1234)) #default to port 1234
			self.client = client
			self.clipboard = clipboard
		except socket.error, (value, message):
			if self.sock:
				self.sock.close()
			traceback.print_exc()
			sys.exit(-1)

	def run(self):
		keyfile = open(self.conf['key'], 'r') #no need to check existence, key is always present
		keyline = keyfile.readline()
		ct = CipherType( 'AES-256', 'CBC' )
		self.lasttext = ''
		while not self.kill_received:
			try:
				message, address = self.sock.recvfrom(8192)
				#first check whether the message happens to be a CSHELO:
				m = new_client_matcher.match(message)
				if m:
					ip = m.group(1) #the ip address of a new client
					port = m.group(4) #the port number the client wishes to communicate on
					if cliputil.safe_ip(ip) and cliputil.safe_port(port): #we check for sane ip-address and port
						self.client.new_client_list.append((ip, port))
				elif self.lasttext != message:
					decr = DecryptCipher(ct, keyline, 'b' * ct.ivLength())
					decrmsg = decr.finish(message)
					if decrmsg != self.clipboard.wait_for_text():
						logger.debug('Got message \'' + str(decrmsg) + '\' from client \'' + str(address) + '\'...')
						self.clipboard.set_text(decrmsg)
						self.clipboard.store()
				self.lasttext = message
			except socket.timeout:
				pass #we ignore receiving socket timeouts
			except:
				traceback.print_exc()
				sys.exit(2)

		


