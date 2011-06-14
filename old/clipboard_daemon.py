from daemon import Daemon
from clipboard_dispatcher import ClipboardDispatcher

import os
class ClipboardDaemon(Daemon):
	def __init__(self, pid, conf, logger, stdin=os.devnull, stdout=os.devnull, stderr=os.devnull):
		Daemon.__init__(self, pidfile=pid, stdin=stdin, stdout=stdout, stderr=stderr)
		self.conf = conf
		self.logger = logger

	def run(self):
		#we are running, let's setup a connection handler
		#this dispatcher is a thread waiting for incoming UDP connections,
		#tasked with building sender and receiver modules for these
		#requests
		dispatcher = ClipboardDispatcher(self.conf, self.logger)
		dispatcher.run()
