#!/usr/bin/env python
from server import clipshare_server

conf = None

def main():
	#first parse the program arguments
	parse_args()
	#setup a configuration
	parse_conf()
	#start a server
	serv = clipshare_server.ClipshareRegistrationServer(port=50244, buf_size=8192, conf=conf)
	serv.start()


def parse_args():
	pass

def parse_conf():
	pass


if __name__ == '__main__':
	main()
