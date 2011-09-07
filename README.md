Clipshare
=========

Clipshare is a program that mitigates one of the few downsides of having 
multiple desktop environments running in parallel; it syncs your
clipboard between all your boxes.

The protocol behind Clipshare is rather easy. The first thing a client
does is UDP broadcast it's ip and port over the network to anybody
who is listening and has the correct key. This message gets intercepted
by other machines running Clipshare who will add the new client's ip
and port to their internal register. Afterwards, if one client sees a
change in the clipboard contents it will build an encrypted content
message and send it to all the clients that it knows. In their turn,
these clients can decrypt the message and they will change the local
clipboard to whatever was transmitted.


Dependencies
------------

For Clipshare to work you need the following dependencies:

	- A recent python (tested with 2.6, newer should work, 3.x doesn't due to dependencies)
	- The python-m2crypto library (can be found in the repositories of most distro's)
	- The python-netifaces library (can be found in the repositories of most distro's)

Furthermore, you need a clipshare config file in an accessible location
(default is ~/.clipshare, but this can be changed with the -c param)

If you don't yet have a key Clipshare will ask to build one for you. For
other clients to be able to decrypt your messages they will need the same
key, so you have to bring your key over to your other machines to let
them communicate

Running Clipshare on startup
----------------------------

If you make sure that the logfile clipshare is supposed to log to is in
a writable directory, clipshare does not need any other privileges to run.
This means that you can just call "./clipshare.py start" and clipshare will
start running in the background. The easiest way to run clipshare on 
startup is by adding it to the startup scripts for your desktop environment. 

For Gnome, for instance, this means going to System -> Startup Applications
and adding the command "/path/to/clipshare start" as command.
