import os

PORT = 50244			#default port to listen on
BUF_SIZE = 8192			#in bytes
INTERVAL = 5			#number of seconds between clipboard checks
ANNOUNCE = 20			#number of seconds between CSHELO messages
KEY_PATH = '~/.clipshare/clipshare.key'
CONF_PATH = '~/.clipshare/clipshare.conf'
CLEAN = 120				#number of seconds before clipshare cleans an ip from it's internal table
MAX_LOG_SIZE=3000000	#maximum number of bytes a logfile can grow
