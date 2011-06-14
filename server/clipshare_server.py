from ncrypt.cipher import CipherError
import socket
import traceback
import logging
import util.clipshare_util as util
import client.clipshare_remote_client as remote
from threading import Thread

class ClipshareServer(Thread):
	s = None
	logger = logging.getLogger('ClipshareRegistrationServer')

	clientlist = []

	def __init__(self, port, buf_size, conf):
		Thread.__init__(self)
		self.port = port
		self.buf_size = buf_size
		self.conf = conf
		self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		self.s.bind(('', self.port))

	def run(self):
		'''
		This method starts the Clipshare server and starts
		listening on the given port.
		'''
		while True:
			message, address = self.s.recvfrom(self.buf_size)
			self.logger.info('Got message, decrypting')
			decrypted = None
			try:
				decrypted = util.decrypt(self.conf['keyfile'], message)
			except CipherError:
				#something went wrong during decrypting, probably garbage
				self.logger.info('Got some garbage after decrypting, ignoring')
				
			t = util.get_message_type(decrypted)
			if t == 'CSHELO':
				#new client found, add it to the list
				(ip, port) = util.parse_cs_helo_msg(decrypted)
				self.clientlist.append(remote.ClipshareRemoteClient(ip, port))
				self.logger.info('Added client with ip %s on port %d!' % (ip, port))
			elif t == 'CSCONTENT':
				#new content, put it in clipboard
				content = util.parse_cs_content_msg(decrypted)
				self.logger.info('Got new content: "' + content + '"')
				util.store_in_clipboard(content)
			else:
				#garbage
				pass


