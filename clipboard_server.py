import socket
import threading, thread
import traceback
import sys
from ncrypt.cipher import DecryptCipher, CipherType
class ClipboardServer(threading.Thread):
	def __init__(self, conf, logger, clipboard=None):
		try:
			threading.Thread.__init__(self)
			self.logger = logger
			self.conf = conf
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.sock.bind(('', int(conf['port'])))
			self.clipboard = clipboard
		except socket.error, (value, message):
			if self.sock:
				self.sock.close()
			traceback.print_exc()
			sys.exit(-1)

	def run(self):
		keyfile = open(conf['key'], 'r')
		keyline = keyfile.readline()
		ct = CipherType( 'AES-256', 'CBC' )
		self.lasttext = None
		while True:
			try:
				message, address = self.sock.recvfrom(8192)
				if self.lasttext != message:
					decr = DecryptCipher(ct, keyline, 'b' * ct.ivLength())
					decrmsg = decr.finish(message)
					if decrmsg != self.clipboard.wait_for_text():
						logger.debug('Got message \'' + str(decrmsg) + '\' from client \'' + str(address) + '\'...')
						self.clipboard.set_text(decrmsg)
						self.clipboard.store()
				self.lasttext = message
			except (KeyboardInterrupt, SystemExit):
				raise
			except:
				traceback.print_exc()

