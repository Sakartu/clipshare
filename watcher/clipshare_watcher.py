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
		if content == self.server.just_in:
			self.previous = content
		if content != self.previous and content != None:
			self.logger.info('Changed clipboard contents found, sending...')
			#new content, send it around
			enc = util.encrypt(self.conf['keyfile'], 'CSCONTENT:' + content + ':TNETNOCSC')
			self.server.clientlistlock.acquire()
			for (ip, (port, _)) in self.server.clientlist.items():
				util.send_content(ip, port, enc)
			self.server.clientlistlock.release()
			self.previous = content


