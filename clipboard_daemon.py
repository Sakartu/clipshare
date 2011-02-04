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

