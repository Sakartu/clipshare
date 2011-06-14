import threading
import time.sleep
import gtk
import clipboard_util

class ClipboardMonitor(threading.Thread):
	self.old_content = ''
	def __init__(self, connections):
		Thread.__init__(self)
		self.connections = connections
		self.running = True

	def run(self):
		while self.running:
			sleep(1)
			#get new content
			new_content = clipboard_util.get_from_clipboard()
			if old_content != new_content:
				for (ip, port) in connections.items():
					#send content to peers
					clipboard_util.send_content(ip, port, new_content)
					old_content = new_content
				


