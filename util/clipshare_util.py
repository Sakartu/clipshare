from M2Crypto import EVP
import netifaces
import gtk
import threading
import socket
import re
import os
import sys
import pwd 
import grp
import util.constants as constants
import logging

cb = gtk.clipboard_get()
cblock = threading.Lock()

types = {
    'CSHELO' : r'CSHELO:(([0-9]{1,3}\.){3}[0-9]{1,3}):([0-9]{1,5}):OLEHSC',
    'CSCONTENT' : r'CSCONTENT:(.*):TNETNOCSC'
    }

logger = logging.getLogger(__name__)

def store_in_clipboard(content):
    """
    A  method that uses the gtk python library to store
    the given contents in the current clipboard
    """
    if cb and content:
    cblock.acquire()
    cb.set_text(content)
    cb.store()
    cblock.release()

def get_from_clipboard():
    """
    A method that uses the gtk python library to get
    content from the current clipboard
    """
    if cb:
    cblock.acquire()
    text = cb.wait_for_text()
    cblock.release()
    return text

#def decrypt(keyfile, ciphertext):
#    """ 
#    A decryption function which takes a keyfile and a ciphertext and returns
#    the AES decrypted plaintext of this ciphertext
#    """
#    if type(keyfile).__name__ == 'str':
#    keyfile = open_file(keyfile)
#    keyline = keyfile.readline()
#    ct = CipherType( 'AES-256', 'CBC' )
#    decr = DecryptCipher(ct, keyline, 'b' * ct.ivLength()) #use static IV
#    return decr.finish(ciphertext)

#def encrypt(keyfile, plaintext):
#    """ 
#    An encryption function which takes a keyfile and a plaintext and returns
#    the AES encrypted ciphertext of this plaintext
#    """
#    if type(keyfile).__name__ == 'str':
#    keyfile = open_file(keyfile)
#    keyline = keyfile.readline()
#    ct = CipherType( 'AES-256', 'CBC' )
#    encr = EncryptCipher(ct, keyline, 'b' * ct.ivLength()) #use static IV
#    return encr.finish(plaintext)

def decrypt(keyfile, data):
    """ 
    A decryption function which takes a keyfile and a ciphertext and returns
    the AES decrypted plaintext of this ciphertext
    """
    if type(keyfile).__name__ == 'str':
    keyfile = open_file(keyfile)
    keyline = keyfile.readline()
    cipher = EVP.Cipher(alg='aes_256_ecb', key=keyline, iv='\0' * 16, padding=False, op=0)
    dec = cipher.update(data)
    dec += cipher.final()
    return dec.rstrip("\0")

def encrypt(keyfile, data):
    """ 
    An encryption function which takes a keyfile and a plaintext and returns
    the AES encrypted ciphertext of this plaintext
    """
    if type(keyfile).__name__ == 'str':
    keyfile = open_file(keyfile)
    keyline = keyfile.readline()
    cipher = EVP.Cipher(alg='aes_256_ecb', key=keyline, iv='\0' * 16, padding=False, op=1)
    dec = cipher.update(padr(data,256/8,"\0"))
    dec += cipher.final()
    return dec

# Padding
def paddedlength(data,n):
    if len(data) % n == 0:
    return len(data)
    return len(data) + (n - (len(data) % n))

def padr(data,n,c):
    return data.ljust(paddedlength(data,n),c)

def padl(data,n,c):
    return data.rjust(paddedlength(data,n),c)

def chunks(data,n):
    return [data[i:i+n] for i in range(0, len(data), n)]

def get_message_type(message):
    """
    A method that parses a given message and tries to find out what message 
    type it is using the regex definitions in the types dict
    """
    if message:
    for (t, rx) in types.items():
        m = re.compile(rx, re.MULTILINE|re.DOTALL).match(message)
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
    """
    A method to udp broadcast the given content to all ip's
    at the given port
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', 0))
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.sendto(content, ('<broadcast>', port))

def parse_bool(boolstr):
    return boolstr.lower() in ['yes', 'true', 'y', '1']

def open_file(path):
    return open(os.path.expanduser(path))

def get_ip(conf):
    '''
    This method tries to find the ip of the local machine. If the ip
    is given in the configfile, it will use this. If the interface 
    on which clipshare should run is specified in the configfile, 
    it will try to find the ip belonging to that iface. Otherwise,
    it will try to find the ip in a smart way.
    '''

    if 'ip' in conf:
    return conf['ip']
    ips = []

    #check if an interface is specified
    if 'iface' in conf:
    preferred_iface = conf['iface']
    iface = netifaces.ifaddresses(preferred_iface)
    if netifaces.AF_INET in iface:
        ips.extend([i['addr'] for i in iface[netifaces.AF_INET]])
    #if ips is still empty, we either don't have a specified iface in the
    #conf, or the interface specified in the configuration didn't have an
    #ip address
    if ips == []:
    for ifaceName in netifaces.interfaces():
        iface = netifaces.ifaddresses(ifaceName)
        if netifaces.AF_INET in iface:
        ips.extend([i['addr'] for i in iface[netifaces.AF_INET]])

    result = ''
    #remove 127.x.x.x addresses
    ips = filter(lambda x : x[0:3] != '127', ips)
    #pick local addresses (starting with 192.168.x.x) before others
    for ip in ips:
    if ip[0:7] ==  '192.168':
        result = ip
    if not result and len(ips):
    #if no 192.168.x.x address can be found, simply take the first one
    #in the list
    result = ips[0]
    #if we still have no ip, too bad, a higher method will see this and
    #handle accordingly
    return result

def genkey(conf):
    ct = CipherType('AES-256', 'CBC')
    default_path = constants.KEY_PATH
    if 'keyfile' in conf:
    default_path = conf['keyfile']
    try:
    path = raw_input('Where would you like your key (Enter for default or ^D to exit)? [%s]: ' % default_path)
    except EOFError:
    #user pressed ^D
    print ''
    sys.exit(2)

    if path == '':
    path = default_path

    try:
    key = open(os.path.expanduser(path), 'w')
    key.write(os.urandom(ct.keyLength()))
    print('Key successfully written!\nDon\'t forget to add it to your configfile!')
    except:
    print('Something went wrong, maybe no permissions to write key?')

def drop_privileges(uid_name='nobody', gid_name='nogroup'):
    starting_uid = os.getuid()

    logger.info('Dropping privileges...')

    if os.getuid() != 0:
    # We're not root so, like, whatever dude
    logger.warn("We're not root, so we can't drop privileges!")
    return


    # If we started as root, drop privs and become the specified user/group
    if starting_uid == 0:


    # Get the uid/gid from the name
    running_uid = pwd.getpwnam(uid_name)[2]
    running_gid = grp.getgrnam(gid_name)[2]


    # Try setting the new uid/gid
    try:
        os.setgid(running_gid)
    except OSError, e:
        logger.error('Could not set effective group id: %s' % e) 

    try:
        os.setuid(running_uid)
    except OSError, e:
        logger.error('Could not set effective user id: %s' % e)


    # Ensure a very convervative umask
    new_umask = 077
    os.umask(new_umask)
