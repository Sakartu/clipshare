#!/usr/bin/env python
import socket
import gtk
import threading, thread
import traceback
import time
import logging
import logging.handlers
import os
import sys
import daemon
import getpass
import hashlib
import ConfigParser
from ncrypt.cipher import EncryptCipher, DecryptCipher, CipherType
from clipboard_daemon import ClipboardDaemon

LEVELS = {'debug': logging.DEBUG,
		'info': logging.INFO,
		'warning': logging.WARNING,
		'error': logging.ERROR,
		'critical': logging.CRITICAL}
#global socket used to send and receive clipboard content over
sock = None

#the local clipboard, retrieved from gtk
clipboard = None

#the global logger, can be used to write to the different log locations
logger = None

#a global configuration dictionary, will be filled with config file options as well as parameters
conf = {}

#the path to the configuration file
conf_path = os.path.join(os.getenv('HOME'), '.config/clipshare/clipshare.conf')

def initialize():
	global logger
	#first of all, we initialize the configfile
	parse_conf()
	#then we initialize the logging functionality
	try:
		os.makedirs(os.path.dirname(conf['logfile']))
	except OSError:
		pass
	except:
		print 'Could nog create logfile or dirs, exitting'
		sys.exit(-1)
	logger = logging.getLogger('Clipshare Logger')
	logger.setLevel(LEVELS[conf['loglevel']])
	filehandler = logging.FileHandler(conf['logfile'])
	logger.addHandler(filehandler)
	if 'stdout' in conf:
		consolehandler = logging.StreamHandler()
		logger.addHandler(consolehandler)
	#now see if there's a key
	if not os.path.exists(conf['key']):
		print "No keyfile present, generating one..."
		genkey()

def parse_conf():
	global conf
	config = ConfigParser.SafeConfigParser()
	if(os.path.exists(conf_path) and os.access(conf_path, os.F_OK) and os.access(conf_path, os.W_OK)):
		config.read(conf_path)
	else:
		print "No configfile found, aborting!"
		exit(-1)
	conf = parse_params(dict(config.items('clipshare')))

def parse_params(conf_dict):
	#method that should fill the config dict with additional commandline parameters
	return conf_dict

def genkey():
	passwd = ''
	passwd2 = ''
	while passwd == '' or passwd != passwd2:
		passwd = getpass.getpass("Please enter a passphrase for your AES key: ")
		passwd2 = getpass.getpass("Please enter your passphrase again: ")
	keyhash = hashlib.sha256(passwd).digest()
	keyfile = open(conf['key'], 'w')
	keyfile.write(keyhash)
	keyfile.close()
	logger.debug("Keyfile \"clipshare.key\" written successfully!")

def main():
	initialize()
	daemon = ClipboardDaemon('/tmp/clipshare.pid', conf, logger)
	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			daemon.start()
		elif 'stop' == sys.argv[1]:
			daemon.stop()
		elif 'restart' == sys.argv[1]:
			daemon.restart()
		elif 'genkey' == sys.argv[1]:
			genkey()
		else:
			logger.error("Unknown command")
			sys.exit(2)
		sys.exit(0)
	else:
		logger.error("Usage: %s start|stop|restart|genkey" % sys.argv[0])
		sys.exit(2)
	logger.debug('Everything done...')

if __name__ == '__main__':
	main()

