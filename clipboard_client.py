import time
import socket
import threading, thread
import sys
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
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
			self.sock.connect(('<broadcast>', int(conf['port'])))

			#and set the clipboard
			self.clipboard = clipboard
		except socket.error, (value, message):
			if self.sock:
				self.sock.close()
			self.logger.error( "Could not open socket: " + str(message))
			sys.exit(-1)
		
	def run(self):
		keyfile = open(self.conf['key'], 'r')
		keyline = keyfile.readline()
		ct = CipherType( 'AES-256', 'CBC' )
		#we run indefinitly
		self.lasttext = ''
		while not self.kill_received:
			time.sleep(1)
			text = self.clipboard.wait_for_text()
			if text and text != self.lasttext:
				encr = EncryptCipher(ct, keyline, 'b' * ct.ivLength())
				self.logger.debug("Sending over message \"" + text + "\"...")
				self.sock.send(encr.finish(text))
			self.lasttext = text

