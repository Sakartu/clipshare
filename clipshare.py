#!/usr/bin/env python
from server import clipshare_server
import time
import util.daemon as daemon
import logging
import sys
import os
import optparse
import ConfigParser
from daemon.clipshare_daemon import ClipshareDaemon

conf = None


#the path to the configuration file
CONF_PATH = os.path.expanduser('~/.clipshare/clipshare.conf')

def initialize():
	""" 
	A method that initializes the clipshare program.
	It parses the configuration files, and tries to find the aes encryption key
	"""

	#we parse the options and the config file
	(conf, args) = parse_opts()

	#now see if there's a key
	if not 'keyfile' in conf or not os.path.exists(os.path.expanduser(conf['keyfile'])):
		print "No keyfile present, generating one..."
		genkey(conf)
	return (conf, args)


def parse_opts():
	parser = optparse.OptionParser()
	parser.add_option('-c', '--conf', nargs=1, dest="new_path") #to specify a config file
	parser.add_option('-d', '--debug', dest="debug", action='store_true') #to setup debugging

	(options, args) = parser.parse_args()

	config = ConfigParser.SafeConfigParser()																															   
	path = CONF_PATH
	if options.new_path:
		path = options.new_path

	if os.path.exists(path) and os.access(path, os.F_OK) and os.access(path, os.W_OK):
		config.read(path)
	else:
		print "No configfile found, aborting!"
		exit(-1)

	result = dict(config.items('clipshare'))
	if options.debug:
		result['debug'] = 'True'

	return (result, args)

def genkey(conf):
	pass

def usage():
	print("usage:")

if __name__ == '__main__':
	(conf, args) = initialize()
	#d = ClipshareDaemon('/tmp/clipshare.pid')
	daemon = ClipshareDaemon(conf, '/tmp/clipshare.pid', stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)

	#DEBUGGING ONLY
	args.append('debug')


	if 'start' in args:
		daemon.start()
	elif 'stop' in args:
		daemon.stop()
	elif 'restart' in args:
		daemon.restart()
	elif 'genkey' in args:
		genkey(conf)
	elif 'debug' in args:
		daemon.run()
	else:
		usage()

	print('All daemons setup, main process will now exit.')
