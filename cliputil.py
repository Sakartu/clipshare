def safe_ip(ip):
	result = True
	try:
		result
		result &= len(filter(lambda x : int(x) > 0 and int(x) < 256, ip.split('.'))) > 0
	except ValueError:
		return False
	return result

def safe_port(port):
	result = True
	try:
		result &= int(port) > 1024 and int(port) < 2 ** 16
	except ValueError:
		return False
	return result
