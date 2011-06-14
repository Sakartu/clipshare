from util.infinite_timer import InfiniteTimer
import util.clipshare_util as util
import util.constants as constants

class ClipshareWatcher:
	previous = ''

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

		timer = InfiniteTimer(interval, check_cliboard)
		timer.daemon = True
		timer.start()

	def check_clipboard(self):
		content = util.get_from_clipboard()
		if content != previous:
			#new content, send it around
			for c in self.server.clientlist:
				util.send_content(c.ip, c.port, content)


