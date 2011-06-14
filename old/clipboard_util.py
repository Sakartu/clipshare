from ncrypt.cipher import DecryptCipher, EncryptCipher, CipherType
import gtk
import threading
import socket

cb = gtk.clipboard_get()
cblock = threading.Lock()

def send_cs_helo(ip, port):
	"""
	A method that can be used to pack an ip and port in a CSHELO message,
	after which it is sent over a broadcast UDP sockt
	"""
	try:
		if ip and port: 
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
			sock.connect(('<broadcast>', int(port)))
			message = "CSHELO:" + ip + ":" + port + ":OLEHSC"
			print "Sending message \"" + message + "\""
			sock.send(message)
			sock.close()
	except:
		pass

def parse_cs_helo_msg(msg):
	"""
	A method that parses an incoming CSHELO message.
	if the message is of the following form:
		CSHELO:<ip>:<port>:OLEHSC
	this method will parse, check and return a tuple of the form ('<ip>', port)
	if anything is out of order, this method returns None
	"""
	import re
	matcher = re.compile(r'CSHELO:(([0-9]{1,3}\.){3}[0-9]{1,3}):([0-9]{1,5}):OLEHSC')
	m = matcher.match(msg)
	try:
		if m:
			ip = m.group(1)
			port = m.group(3)
			if len([x for x in ip.split('.') if int(x) < 255]) == 4 and int(port) < 2**16:
				return (m.group(1), int(m.group(3)))	
		return None
	except:
		return None

def parse_cs_content_msg(msg):
	"""
	A method that parses an incoming CSCONTENT message.
	if the message is of the following form:
		CSCONTENT:<content>
	this method will parse, check and return the content bit
	if anything is out of order, this method returns None
	"""
	if len(msg) > 10 and msg[:10] == 'CSCONTENT:':
		return msg[10:]
	else:
		return None

def send_content(ip, port, content):
	"""
	A simple util method used to open a socket to a given ip-address
	and port, send a message, then close the socket again

	"""
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((ip, port))
	sock.send(content)
	sock.close()

def decrypt(keyfile, ciphertext):
	"""
	A decryption function which takes a keyfile and a ciphertext and returns
	the AES decrypted plaintext of this ciphertext
	"""
	keyline = keyfile.readline()
	ct = CipherType( 'AES-256', 'CBC' )
	decr = DecryptCipher(ct, keyline, 'b' * ct.ivLength()) #use static IV
	return decr.finish(ciphertext)

def encrypt(keyfile, plaintext):
	"""
	An encryption function which takes a keyfile and a plaintext and returns
	the AES encrypted ciphertext of this plaintext
	"""
	keyline = keyfile.readline()
	ct = CipherType( 'AES-256', 'CBC' )
	encr = EncryptCipher(ct, keyline, 'b' * ct.ivLength()) #use static IV
	return encr.finish(plaintext)

def store_in_clipboard(content):
	if cb and content:
		cblock.acquire()
		cb.set_text(content)
		cb.store()
		cblock.release()

def get_from_clipboard():
	if cb:
		cblock.acquire()
		text = cb.wait_for_text()
		cblock.release()
		return text
	
def get_ip(conf):
	if 'ip' in conf:
		return conf
	else:
		#get all local ip's
		ips = socket.gethostbyname_ex(socket.gethostname())[2]
		#remove 127.x.x.x addresses
		ips = filter(lambda x : x[0:3] != 127, ips)
		#pick local addresses (starting with 192.168.x.x) before others
		for ip in ips:
			if ip[0:7] ==  '192.168':
				conf['ip'] = ip
		if 'ip' not in conf:
			#if no 192.168.x.x address can be found, simply take the first one
			#in the list
			conf['ip'] = ips[0]
		#if we still have no ip, too bad, a higher method will see this and
		#handle accordingly
		return conf



