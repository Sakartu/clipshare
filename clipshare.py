#!/usr/bin/env python
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

#a global variable defining whether we're in debug mode or not
DEBUG = True

#the local clipboard, retrieved from gtk
clipboard = None

#the global logger, can be used to write to the different log locations
logger = None

#a global configuration dictionary, will be filled with config file options as well as parameters
conf = {}

#the path to the configuration file
conf_path = os.path.expanduser('~/.config/clipshare/clipshare.conf')

def initialize():
	global logger
	#first of all, we initialize the configfile
	parse_conf()
	#then we initialize the logging functionality
	logger = logging.getLogger('Clipshare Logger')
	if 'loglevel' in conf:
		logger.setLevel(LEVELS[conf['loglevel']])
	else:
		logger.setLevel(logging.ERROR) #default to ERROR
	if 'logfile' in conf:
		if not os.path.exists(os.path.dirname(conf['logfile'])):
			try:
				os.makedirs(os.path.dirname(conf['logfile']))
			except:
				print 'Could nog create logfile or dirs, exitting'
				sys.exit(2)
		filehandler = logging.FileHandler(conf['logfile'])
		logger.addHandler(filehandler)
	if 'stdout' in conf:
		consolehandler = logging.StreamHandler()
		logger.addHandler(consolehandler)
	#now see if there's a key
	if not 'key' in conf or not os.path.exists(conf['key']):
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
	keyhash = hashlib.sha256(passwd).digest() #use the sha-1 of the given password as passphrase for aes
	if not 'key' in conf:
		conf['key'] = os.path.expanduser('~/.clipshare/clipshare.key')
	if not os.path.exists(os.path.dirname(conf['key'])):
		os.makedirs(os.path.dirname(conf['key']))
	keyfile = open(conf['key'], 'w')
	keyfile.write(keyhash)
	keyfile.close()
	logger.debug("Keyfile \"clipshare.key\" written successfully!")

def usage(exit=True):
	logger.error("Usage: %s start|stop|restart|genkey" % sys.argv[0])
	if exit:
		sys.exit(2)

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
			usage()
	elif DEBUG:
		daemon.run()
	else:
		usage()
	logger.debug('All daemons setup, main process will now exit.')
	sys.exit(0)

if __name__ == '__main__':
	main()

