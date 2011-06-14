from util.infinite_timer import InfiniteTimer
import util.clipshare_util as util
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
		#get the local ip
		ip = util.getip(self.conf)
		if ip:
			logger.info('Found local ip %s!' % (ip))
			t = InfiniteTimer(interval, announce, [ip, port])
		else:
			logger.error('No local ip-address could be found and none was specified, exitting!')
			sys.exit(2)

	def announce(self, ip, port):
		msg = "CSHELO:%s:%d:OLEHSC" % (ip, port)
		util.broadcast(msg, constants.PORT)


