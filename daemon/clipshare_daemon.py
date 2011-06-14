import logging
from util.daemon import Daemon
import util.clipshare_util as util
import util.constants as constants
import os
import sys
import server.clipshare_server as server
import watcher.clipshare_watcher as watcher
import announcer.clipshare_announcer as announcer
import time

class ClipshareDaemon(Daemon):
	logger = logging.getLogger('ClipshareDaemon')

	def __init__(self, conf, pid, stdin=os.devnull, stdout=os.devnull, stderr=os.devnull):
		Daemon.__init__(self, pid, stdin, stdout, stderr)
		self.conf = conf
		self.setup_logging()

	def setup_logging(self):
		#if we're in debugging mode we use loglevel DEBUG, otherwise ERROR
		level = None
		if 'debug' in self.conf:
			level = logging.DEBUG
		else:
			level = logging.ERROR

		#then we initialize the logging functionality
		if 'logfile' in self.conf:
			path = os.path.expanduser(self.conf['logfile'])

			if not os.path.exists(os.path.dirname(path)):
				try:
					os.makedirs(os.path.dirname(path))
				except:
					print 'Could nog create logfile or dirs, exitting'
					sys.exit(2)
			logging.basicConfig(level=level, filename=path)
		elif 'stdout' in self.conf and util.parse_bool(self.conf['stdout']):
			logging.basicConfig(level=level)
		self.logger.info('Logging setup, continuing...')

	def run(self):
		#start a registration server
		if 'port' in self.conf:
			port = int(self.conf['port'])
		else:
			port = constants.PORT

		self.logger.info('Setting up server...')
		serv = server.ClipshareServer(port=port, buf_size=constants.BUF_SIZE, conf=self.conf)
		serv.daemon = True
		serv.start()
		self.logger.info('Server setup complete.')

		self.logger.info('Setting up clipboard watcher...')
		cswatcher = watcher.ClipshareWatcher(self.conf, serv)
		cswatcher.run()
		self.logger.info('Clipboard watcher setup complete.')

		self.logger.info('Setting up announcer...')
		csannouncer = announcer.ClipshareAnnouncer(self.conf)
		csannouncer.run()
		self.logger.info('Announcer setup complete.')


		while True:
			time.sleep(1)
