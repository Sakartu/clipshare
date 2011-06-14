import socket
import traceback
import logging
import util.clipshare_util as util
import client.clipshare_remote_client as remote
import threading.Thread

class ClipshareRegistrationServer(threading.Thread):
	s = None
	logger = logging.getLogger('ClipshareRegistrationServer')

	clientlist = []

	def __init__(self, port, buf_size, conf):
		self.port = port
		self.buf_size = buf_size
		self.conf = conf
		self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		self.s.bind(('', self.port))

	def run(self):
		'''
		This method starts the Clipshare registration server and starts
		listening on the given port.

		setup() should have been called before this method is called
		'''
		while True:
			message, address = self.s.recvfrom(buf_size)
			if self.conf != None and self.conf.getboolean('encryption', 'enabled'):
				decrypted = util.decrypt(self.conf.get('encryption', 'keyfile'))
			else:
				decrypted = message
			t = util.get_message_type(decrypted)
			if t == 'CSHELO':
				#new client found, add it to the list
				(ip, port) = util.parse_cs_helo_msg(decrypted)
				self.clientlist.append(remote.ClipshareRemoteClient(ip, port))


