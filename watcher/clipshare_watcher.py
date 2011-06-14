from util.infinite_timer import InfiniteTimer
import util.clipshare_util as util
import util.constants as constants
import logging

class ClipshareWatcher:
	previous = ''
	logger = logging.getLogger('ClipshareWatcher')

	def __init__(self, conf, server):
		self.conf = conf
		self.server = server

	def run(self):
		interval = constants.INTERVAL
		if 'interval' in self.conf:
			try:
				interval = int(self.conf['interval'])
			except ValueError:
				pass
				#weird value in conf, take default

		timer = InfiniteTimer(interval, self.check_clipboard, immediate=True)
		timer.daemon = True
		timer.start()

	def check_clipboard(self):
		content = util.get_from_clipboard()
		if content != self.previous:
			self.logger.info('Changed clipboard contents found, sending...')
			#new content, send it around
			for c in self.server.clientlist:
				util.send_content(c.ip, c.port, content)
			self.previous = content


