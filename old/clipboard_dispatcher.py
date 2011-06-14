import SocketServer
import clipboard_util
import gtk

class ClipboardContentRequestHandler(SocketServer.StreamRequestHandler):
	def handle(self):
		#we got new incoming content, check whether it contains sane content 
		#after decrypting and if so set the local clipboard 
		data = self.rfile.readline().strip()
		#data is still encrypted, so decrypt it first
		if 'key' not in self.server.dispatcher.conf:
			return
		keyfile = open('r', self.server.dispatcher.conf['key'])
		decrypted = clipboard_util.decrypt(keyfile, data)
		content = clipboard_util.parse_cs_content_msg(decrypted)
		if content:
			self.server.logger.debug("Client %s sent: \"%s\"" % (self.client_address[0], content))
			clipboard_util.store_in_clipboard(content)

class ClipboardNewClientRequestHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		data = self.request[0].strip()
		socket = self.request[1]
		self.server.logger.debug("New client \"%s\"" % self.client_address[0])
		self.server.logger.debug("Data sent: \"%s\"" % data)
		#a new client is here, create handlers for it
		parsed = clipboard_util.parse_cs_helo_msg(data)
		if parsed:
			ip = parsed[0]
			port = parsed[1]
			#if the sent message contains sane values and we don't know them already
			#log them as a new peer
			if (ip, port) not in self.server.dispatcher.connections:
				self.server.dispatcher.connections[ip] = port

class ClipboardDispatcher():
	def __init__(self, conf, logger):
		print "Setting up Dispatcher"
		self.conf = conf
		self.logger = logger
		self.connections = {}

	def run(self):
		#first we send our listening ip and port in a CSHELO message we try to 
		#find out our own ip the best we can. this is ugly and won't always 
		#work, but hey, a python script's gotta try rite :)
		self.conf = clipboard_util.get_ip(self.conf)
		if 'ip' in self.conf and 'port' in self.conf:
			clipboard_util.send_cs_helo(self.conf['ip'], self.conf['port'])
		else:
			self.logger.error('No local ip could be found, aborting!')
			return
		#setup a listening UDP server which handles new clients and a listening
		#TCP server which handles incoming content
		#if the listening port is configured, use this, else use default port 
		#1234
		if 'port' in self.conf:
			new_clients_server = SocketServer.UDPServer(('localhost', int(self.conf['port'])), ClipboardNewClientRequestHandler)
			new_content_server = SocketServer.TCPServer(('localhost', int(self.conf['port'])), ClipboardContentRequestHandler)
		else:
			new_clients_server = SocketServer.UDPServer(('localhost', 1234), ClipboardNewClientRequestHandler)
			new_content_server = SocketServer.TCPServer(('localhost', 1234), ClipboardContentRequestHandler)
		new_clients_server.dispatcher = self
		new_clients_server.serve_forever()
		new_content_server.dispatcher = self
		new_content_server.serve_forever()

		#also setup the thread that will monitor the clipboard
		monitor = ClipboardMonitor(self.connections)
		monitor.run()
