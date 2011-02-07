import gtk
import daemon
from clipboard_server import ClipboardServer
from clipboard_client import ClipboardClient
class ClipboardDaemon(daemon.Daemon):
	#def __init__(self, pid, conf, logger, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
	def __init__(self, pid, conf, logger, stdin='/dev/stdin', stdout='/dev/stdout', stderr='/dev/stderr'):
		daemon.Daemon.__init__(self, pid, stdin, stdout, stderr)
		self.conf = conf
		self.logger = logger

	def run(self):
		self.logger.debug('Setting up server...')
		self.s = ClipboardServer(self.conf, self.logger, gtk.clipboard_get())
		self.logger.debug('Setting up client...')
		self.c = ClipboardClient(self.conf, self.logger, gtk.clipboard_get())
		self.s.start()
		self.c.start()
		try:
			while True: #to remain responsive to ^c we join with timeout
				self.s.join(1)
				self.c.join(1)
		except KeyboardInterrupt:
			self.logger.debug('Received keyboard interrupt, shutting down threads')
			self.s.kill_received = True
			self.c.kill_received = True

