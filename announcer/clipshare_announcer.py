from util.infinite_timer import InfiniteTimer
import util.clipshare_util as util
import util.constants as constants
import logging
import sys

class ClipshareAnnouncer():
	logger = logging.getLogger('ClipshareAnnouncer')
	def __init__(self, conf):
		self.conf = conf

	def run(self):
		interval = constants.ANNOUNCE
		if 'announce' in self.conf:
			try:
				interval = int(self.conf['announce'])
			except ValueError:
				pass
				#weird value in conf, take default
		#get the local ip and set it for later use
		ip = util.get_ip(self.conf)
		self.conf['ip'] = ip
		port = constants.PORT
		if 'port' in self.conf:
			try:
				port = int(self.conf['port'])
			except ValueError:
				#weird value in conf, take default
				pass

		if ip:
			self.logger.info('Found local ip %s!' % (ip))
			self.logger.info('Setting up announcer with interval %d...' % (interval))
			t = InfiniteTimer(interval, self.announce, [ip, port], immediate=True)
			t.daemon = True
			t.start()
		else:
			self.logger.error('No local ip-address could be found and none was specified, exitting!')
			sys.exit(2)

	def announce(self, ip, port):
		self.logger.debug('Announcing %s:%d!' % (ip, port))
		msg = util.encrypt(self.conf['keyfile'],"CSHELO:%s:%d:OLEHSC" % (ip, port))
		util.broadcast(msg, constants.PORT)


