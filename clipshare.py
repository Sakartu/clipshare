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
from ncrypt.cipher import CipherType
import util.clipshare_util as util
import util.constants as constants
import readline

conf = None

usagestr = \
'''Usage: %prog <command> [options]

This program can be used to share your clipboard over multiple
machines. It establishes which other devices are in the vicinity
running the same software and distributes your cliboard amongst
all of them. All transfers are encrypted using an AES cipher
based on the key you provide in the config file. As it is a
symmetric crypto, the same keyfile should be used everywhere.
By default, all the related files for clipshare are stored in
~/.clipshare/

The different possible commands are:

    start/stop/restart
        this starts/stops/restarts clipshare as a daemon

    genkey
        this will generate a key for you 
'''

def initialize():
	""" 
	A method that initializes the clipshare program.
	It parses the configuration files and the arguments and options
	"""

	#we parse the options and the config file
	(conf, args) = parse_opts()

	return (conf, args)


def parse_opts():
	parser = optparse.OptionParser(usage=usagestr)
	parser.add_option('-c', '--conf', nargs=1, dest="new_path", help='NEW_PATH specifies a different configuration file')
	parser.add_option('-d', '--debug', dest="debug", action='store_true', help='This puts the program in debugging mode, so it will log everything')

	(options, args) = parser.parse_args()

	config = ConfigParser.SafeConfigParser()																															   
	path = os.path.expanduser(constants.CONF_PATH)
	if options.new_path:
		path = options.new_path
	
	if os.path.exists(path) and os.access(path, os.F_OK) and os.access(path, os.W_OK):
		config.read(path)
	else:
		print "No configfile found, aborting!"
		sys.exit(2)

	result = dict(config.items('clipshare'))

	if options.debug or 'debug' in result:
		result['debug'] = True

	return (result, args)

def usage():
	print(usagestr)
	print("Usage: %s start|stop|restart|genkey [options]" % (sys.argv[0]))
	sys.exit(0)

if __name__ == '__main__':
	(conf, args) = initialize()

	daemon = None
	if 'debug' in conf and conf['debug'] == True:
		daemon = ClipshareDaemon(conf, '/tmp/clipshare.pid', stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
	else:
		daemon = ClipshareDaemon(conf, '/tmp/clipshare.pid')

	if 'start' in args or 'restart' in args and 'logfile' in conf:
		print("Will be running as daemon, all error messages will appear in the logfile!")


	if 'debug' in conf:
		daemon.run()
	elif 'start' in args:
		daemon.start()
	elif 'stop' in args:
		daemon.stop()
	elif 'restart' in args:
		daemon.restart()
	elif 'genkey' in args:
		util.genkey(conf)
	else:
		usage()

