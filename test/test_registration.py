import sys
sys.path.append("../")
import util.clipshare_util as util
from socket import *
import time

s = socket(AF_INET, SOCK_DGRAM)
s.bind(('', 0))
s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

data = 'CSHELO:192.168.1.124:50244:OLEHSC'
enc = util.encrypt(open('/home/peter/.clipshare/clipshare.key'), data)
s.sendto(enc, ('<broadcast>', 50244))
time.sleep(2)

data = 'CSCONTENT:bla:' + "CSCONTENT"[::-1]
enc = util.encrypt(open('/home/peter/.clipshare/clipshare.key'), data)
s = socket(AF_INET, SOCK_DGRAM)
s.sendto(enc, ('127.0.0.1', 50244))

