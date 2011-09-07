#!/usr/bin/env python
import logging
import sys
import os
import optparse
import ConfigParser
from daemon.clipshare_daemon import ClipshareDaemon
import util.clipshare_util as util
import util.constants as constants

#test whether the required modules are available
try:
    import M2Crypto
except ImportError:
    print "The M2Crypto library is required to run Clipshare!"
    sys.exit(-1)

try:
    import netifaces
except ImportError:
    print "The netifaces library is required to run Clipshare!"
    sys.exit(-1)

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
    setup_logging(conf)

    return (conf, args)

def setup_logging(conf):
    #if we're in debugging mode we use loglevel DEBUG, otherwise ERROR
    level = None
    if 'debug' in conf:
        level = logging.DEBUG
    else:
        level = logging.INFO
    format = '%(asctime)s : %(message)s'
    dateformat = '%d/%m/%Y %H:%M:%S'

    #then we initialize the logging functionality
    if 'logfile' in conf:
        path = os.path.expanduser(conf['logfile'])

        if not os.path.exists(os.path.dirname(path)):
            try:
                os.makedirs(os.path.dirname(path))
            except:
                print('Could nog create logfile or dirs, exitting')
                sys.exit(2)
        #logging.basicConfig(level=level, filename=path, format=format, datefmt=dateformat)
        formatter = logging.Formatter(fmt=format, datefmt=dateformat)
        logging.getLogger().setLevel(level)
        handler = logging.handlers.RotatingFileHandler(path, maxBytes=constants.MAX_LOG_SIZE, backupCount=2)
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)
    elif 'stdout' in conf and util.parse_bool(conf['stdout']):
        logging.basicConfig(level=level, format=format, datefmt=dateformat)


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

    d = None
    if 'debug' in conf and conf['debug'] == True:
        d = ClipshareDaemon(conf, '/tmp/clipshare.pid', stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
    else:
        d = ClipshareDaemon(conf, '/tmp/clipshare.pid')

    if ('start' in args or 'restart' in args) and ('logfile' in conf and not 'debug' in conf):
        print("Will be running as daemon, all error messages will appear in the logfile!")


    if 'debug' in conf:
        d.run()
    elif 'start' in args:
        d.start()
    elif 'stop' in args:
        d.stop()
    elif 'restart' in args:
        d.restart()
    elif 'genkey' in args:
        util.genkey(conf)
    else:
        usage()

