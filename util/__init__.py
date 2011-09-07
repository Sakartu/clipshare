import sys
#test whether the required modules are available
try:
    from M2Crypto import EVP
except ImportError:
    print "The M2Crypto library is required to run Clipshare!"
    sys.exit(-1)

try:
    import netifaces
except ImportError:
    print "The netifaces library is required to run Clipshare!"
    sys.exit(-1)
