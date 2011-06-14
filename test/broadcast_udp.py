import sys, time
from socket import *


s = socket(AF_INET, SOCK_DGRAM)
s.bind(('', 0))
s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

data = repr(time.time()) + '\n'
s.sendto(data, ('<broadcast>', 50244))
time.sleep(2)

