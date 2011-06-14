#!/usr/bin/env python
import logging
import logging.handlers
import os
import sys
import getpass
import hashlib
import ConfigParser
import argparse
import optparse
from clipboard_daemon import ClipboardDaemon

LEVELS = {'debug': logging.DEBUG,
		'info': logging.INFO,
		'warning': logging.WARNING,
		'error': logging.ERROR,
		'critical': logging.CRITICAL}
#global debug setting
debug = False

#the global logger, can be used to write to the different log locations
logger = None

#a global configuration dictionary, will be filled with config file options as well as parameters
conf = {}

#the path to the configuration file
CONF_PATH = os.path.expanduser('~/.config/clipshare/clipshare.conf')

def initialize():
	"""
	A method that initializes the clipshare program.
	It parses the configuration files, sets up the logger
	and tries to find the aes encryption key
	"""

	global logger, conf
	#we parse the options and the config file
	conf = parse_opts()
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
		genkey(logger, conf)

def parse_opts():
	global debug
	from sys import argv
	new_path = ''
	#the stuff below only works in python3
	#parser = argparse.ArgumentParser(description='A simple program that sets up a local p2p network to share clipboard contents accross computers.')
	#parser.add_argument('-c', '--conf', nargs=1, type=file, dest=new_path) #to specify a config file
	#parser.add_argument('-d', '--debug', dest=debug, action='store_true') #to setup debugging
	parser = optparse.OptionParser()
	parser.add_argument('-c', '--conf', nargs=1, dest="new_path") #to specify a config file
	parser.add_argument('-d', '--debug', dest="debug", action='store_true') #to setup debugging



	print debug
	if len(argv) > 1:
		parser.parse_args(argv)
	config = ConfigParser.SafeConfigParser()
	path = CONF_PATH
	if new_path:
		path = new_path
	if os.path.exists(path) and os.access(path, os.F_OK) and os.access(path, os.W_OK):
		config.read(path)
	else:
		print "No configfile found, aborting!"
		exit(-1)
	return dict(config.items('clipshare'))

def usage(exit=True):
	logger.error("Usage: %s start|stop|restart|genkey" % sys.argv[0])
	if exit:
		sys.exit(2)

def main():
	initialize()
	print debug
	if debug:
		daemon = ClipboardDaemon('/tmp/clipshare.pid', conf, logger, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
	else:
		daemon = ClipboardDaemon('/tmp/clipshare.pid', conf, logger)
	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			daemon.start()
		elif 'stop' == sys.argv[1]:
			daemon.stop()
		elif 'restart' == sys.argv[1]:
			daemon.restart()
		elif 'genkey' == sys.argv[1]:
			genkey(logger, conf)
		else:
			usage()
	elif debug:
		daemon.run()
	else:
		usage()
	logger.debug('All daemons setup, main process will now exit.')
	sys.exit(0)

if __name__ == '__main__':
	main()

