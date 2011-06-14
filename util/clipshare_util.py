from ncrypt.cipher import DecryptCipher, EncryptCipher, CipherType
import gtk
import threading
import socket
import re
import os

cb = gtk.clipboard_get()
cblock = threading.Lock()

types = {
		'CSHELO' : r'CSHELO:(([0-9]{1,3}\.){3}[0-9]{1,3}):([0-9]{1,5}):OLEHSC',
		'CSCONTENT' : r'CSCONTENT:(.*):TNETNOCSC'
		}

def store_in_clipboard(content):
	'''
	A  method that uses the gtk python library to store
	the given contents in the current clipboard
	'''
	if cb and content:
		cblock.acquire()
		cb.set_text(content)
		cb.store()
		cblock.release()

def get_from_clipboard():
	'''
	A method that uses the gtk python library to get
	content from the current clipboard
	'''
	if cb:
		cblock.acquire()
		text = cb.wait_for_text()
		cblock.release()
		return text

def decrypt(keyfile, ciphertext):
	""" 
	A decryption function which takes a keyfile and a ciphertext and returns
	the AES decrypted plaintext of this ciphertext
	"""
	if type(keyfile).__name__ == 'str':
		keyfile = open_file(keyfile)
	keyline = keyfile.readline()
	ct = CipherType( 'AES-256', 'CBC' )
	decr = DecryptCipher(ct, keyline, 'b' * ct.ivLength()) #use static IV
	return decr.finish(ciphertext)

def encrypt(keyfile, plaintext):
	""" 
	An encryption function which takes a keyfile and a plaintext and returns
	the AES encrypted ciphertext of this plaintext
	"""
	if type(keyfile).__name__ == 'str':
		keyfile = open_file(keyfile)
	keyline = keyfile.readline()
	ct = CipherType( 'AES-256', 'CBC' )
	encr = EncryptCipher(ct, keyline, 'b' * ct.ivLength()) #use static IV
	return encr.finish(plaintext)

def get_message_type(message):
	'''
	A method that parses a given message and tries to find out what message 
	type it is using the regex definitions in the types dict
	'''
	if message:
		for (t, rx) in types.items():
			m = re.compile(rx).match(message)
			if m:
				return t
	return None

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
		CSCONTENT:<content>:TNETNOCSC
	this method will parse, check and return the content bit
	if anything is out of order, this method returns None
	"""
	if len(msg) > 20 and msg[:10] == 'CSCONTENT:' and msg[-10:] == 'CSCONTENT:'[::-1]:
		return msg[10:-10]
	else:
		return None

def send_content(ip, port, content):
	"""																																									
	A simple util method used to open a socket to a given ip-address
	and port, send a message, then close the socket again

	"""
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.sendto(content, (ip, port))
	sock.close()

def broadcast(content, port):
	'''
	A method to udp broadcast the given content to all ip's
	at the given port
	'''
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind(('', 0))
	s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	s.sendto(content, ('<broadcast>', port))

def parse_bool(boolstr):
	return boolstr.lower() in ['yes', 'true', 'y', '1']

def open_file(path):
	return open(os.path.expanduser(path))

def get_ip(conf):
	result = ''
	if 'ip' in conf:
		return conf['ip']
	else:
		#get all local ip's
		ips = socket.gethostbyname_ex(socket.gethostname())[2]
		#remove 127.x.x.x addresses
		ips = filter(lambda x : x[0:3] != 127, ips)
		#pick local addresses (starting with 192.168.x.x) before others
		for ip in ips:
			if ip[0:7] ==  '192.168':
				result = ip
		if not ip:
			#if no 192.168.x.x address can be found, simply take the first one
			#in the list
			result = ips[0]
		#if we still have no ip, too bad, a higher method will see this and
		#handle accordingly
		return result

