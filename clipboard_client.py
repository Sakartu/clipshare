import time
import socket
import threading, thread
import sys
import cliputil
from ncrypt.cipher import EncryptCipher, CipherType

class ClipboardClient(threading.Thread):
	kill_received = False
	def __init__(self, conf, logger, clipboard=None):
		try:
			threading.Thread.__init__(self)
			#fix the logger
			self.logger = logger

			#fix the config file
			self.conf = conf

			#then setup a broadcast socket
			self.broadcast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.broadcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.broadcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
			if 'port' in conf:
				self.broadcast_sock.connect(('<broadcast>', int(conf['port'])))
			else:
				self.broadcast_sock.connect(('<broadcast>', 1234)) #default to port 1234

			#and set the clipboard
			self.clipboard = clipboard

			self.new_client_list = []
			self.client_list = []
		except socket.error, (value, message):
			if self.broadcast_sock:
				self.broadcast_sock.close()
			self.logger.error( "Could not open socket: " + str(message))
			sys.exit(-1)
		
	def run(self):
		#initial broadcast
		broadcast_id()
		#then setup key material
		keyfile = open(self.conf['key'], 'r')
		keyline = keyfile.readline()
		ct = CipherType( 'AES-256', 'CBC' )
		#we run indefinitly
		self.lasttext = ''
		while not self.kill_received:
			time.sleep(1)
			text = self.clipboard.wait_for_text()
			if text and text != self.lasttext:
				encr = EncryptCipher(ct, keyline, 'b' * ct.ivLength()) #use static IV
				self.logger.debug("Sending over message \"" + text + "\"...")
				for sock in client_list:
					try:
						sock.send(encr.finish(text))
					except socket.error:
						sock.close() #client gone offline?
						client_list.remove(sock)
			self.lasttext = text
			handle_new_clients() #check if we have received new client messages
	
	def handle_new_clients():
		for (ip, port) in new_client_list:
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			sock.connect((ip, int(port)))
			client_list.append(sock)
			new_client_list.remove(ip, port)
		if len(new_client_list) > 0:
			broadcast_id()

			
def broadcast_id():
	message = "CSHELO:"
	if 'ip' in conf and cliputil.safe_ip(conf['ip']):
		message += conf['ip'] + ":"
	else:
		pass #TODO: find own ip based on something
	if 'port' in conf and cliputil.safe_port(conf['port']):
		message += conf['port'] + ':'
	else:
		message += '1234:'
		self.broadcast_sock.send(message)
