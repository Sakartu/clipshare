import util.clipshare_util as util
class ClipshareRemoteClient:
	def __init__(self, ip, port):
		self.ip = ip
		self.port = port

	def sendMessage(self, message):
		util.send_content(self.ip, self.port, message)

		

