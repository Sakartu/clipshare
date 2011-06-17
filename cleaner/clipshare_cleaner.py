from util.infinite_timer import InfiniteTimer
from datetime import datetime
import logging
import util.constants as constants

class ClipshareCleaner():
	logger = logging.getLogger(__name__)

	def __init__(self, conf, serv):
		self.conf = conf
		self.serv = serv

	def run(self):
		self.interval = constants.CLEAN
		if 'clean' in self.conf:
			try:
				self.interval = int(self.conf['clean'])
			except ValueError:
				pass
				#weird value in conf, take default

		self.logger.info('Setting up cleaner with interval %d...' % (self.interval))
		t = InfiniteTimer(self.interval, self.clean, immediate=False)
		t.daemon = True
		t.start()

	def clean(self):
		self.logger.debug('Cleaning up ip\'s...')
		now = datetime.now()
		self.serv.clientlistlock.acquire()
		for (ip, (port, timestamp)) in self.serv.clientlist.items():
			diff = (now - timestamp).seconds
			if diff > self.interval:
				self.logger.info('%s hasn\'t been seen in %d seconds, removing from register!' % (ip, diff))
				#last client announce was a long time ago, remove it
				self.serv.clientlist.pop(ip)
		self.serv.clientlistlock.release()

