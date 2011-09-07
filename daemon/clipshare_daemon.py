import logging
import logging.handlers
from util.daemon import Daemon
import util.clipshare_util as util
import util.constants as constants
import os
import sys
import server.clipshare_server as server
import watcher.clipshare_watcher as watcher
import announcer.clipshare_announcer as announcer
import cleaner.clipshare_cleaner as cleaner
import time

class ClipshareDaemon(Daemon):
    logger = logging.getLogger(__name__)

    def __init__(self, conf, pid, stdin=os.devnull, stdout=os.devnull, stderr=os.devnull):
        Daemon.__init__(self, pid, stdin, stdout, stderr)
        self.conf = conf


    def run(self):
        logging.info('Clipshare started.')
        self.drop_privs()
        #first check whether a key exists
        if not 'keyfile' in self.conf or not os.path.exists(os.path.expanduser(self.conf['keyfile'])):
            self.logger.error("No keyfile present, aborting!")
            sys.exit(2)

        #start a registration server
        if 'port' in self.conf:
            port = int(self.conf['port'])
        else:
            port = constants.PORT

        try:
            self.logger.info('Setting up server...')
            serv = server.ClipshareServer(port=port, buf_size=constants.BUF_SIZE, conf=self.conf)
            serv.daemon = True
            serv.start()
            self.logger.info('Server setup complete.')

            self.logger.info('Setting up clipboard watcher...')
            cswatcher = watcher.ClipshareWatcher(self.conf, serv)
            cswatcher.run()
            self.logger.info('Clipboard watcher setup complete.')

            self.logger.info('Setting up announcer...')
            csannouncer = announcer.ClipshareAnnouncer(self.conf)
            csannouncer.run()
            self.logger.info('Announcer setup complete.')

            self.logger.info('Setting up cleaner...')
            cscleaner = cleaner.ClipshareCleaner(self.conf, serv)
            cscleaner.run()
            self.logger.info('Cleaner setup complete.')

            self.logger.info('All threads setup, let\'s go!.')
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    def drop_privs(self):
        self.logger.info('Logging setup complete, dropping privileges...')
        user = 'nobody'
        group = 'nogroup'
        if 'user' in self.conf and 'group' in self.conf:
            user = self.conf['user']
            group = self.conf['group']

        util.drop_privileges(user, group)

