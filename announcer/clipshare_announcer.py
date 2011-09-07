from util.infinite_timer import InfiniteTimer
import util.clipshare_util as util
import util.constants as constants
import logging
import sys

class ClipshareAnnouncer():
        logger = logging.getLogger(__name__)
        def __init__(self, conf):
                self.conf = conf
                self.ip = constants.IP

        def run(self):
                interval = constants.ANNOUNCE
                if 'announce' in self.conf:
                        try:
                                interval = int(self.conf['announce'])
                        except ValueError:
                                pass
                                #weird value in conf, take default

                port = constants.PORT
                if 'port' in self.conf:
                        try:
                                port = int(self.conf['port'])
                        except ValueError:
                                #weird value in conf, take default
                                pass

                self.logger.info('Setting up announcer with interval %d...' % (interval))
                t = InfiniteTimer(interval, self.announce, [port], immediate=True)
                t.daemon = True
                t.start()

        def announce(self, port):
                #get the local ip and set it for later use
                ip = util.get_ip(self.conf)
                if len(ip) == 0:
                        self.logger.error('No local ip-address could be found and none was specified, using default!')
                        ip = constants.IP

                if ip != self.ip:
                        self.logger.info('Found local ip %s!' % (ip))
                        self.ip = ip

                self.logger.debug('Announcing %s:%d!' % (self.ip, port))
                msg = util.encrypt(self.conf['keyfile'],"CSHELO:%s:%d:OLEHSC" % (self.ip, port))
                util.broadcast(msg, constants.PORT) #use fixed port for sending



