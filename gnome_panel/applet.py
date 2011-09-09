#!/usr/bin/env python
import pygtk
pygtk.require('2.0')

import gtk
import gnomeapplet

import sys

class Clipshare(gnomeapplet.Applet):

    def __init__(self, applet, iid):
        self.applet = applet

        label = gtk.Label("C")
        self.applet.add(label)
        self.applet.show_all()
        self.create_menu("bla")


    def create_menu(self, clipboard_contents):
        xml = """<popup name="button3">
<menuitem name="ItemPreferences" 
          verb="Preferences" 
          label="_Preferences" 
          pixtype="stock" 
          pixname="gtk-preferences"/>
<separator/>
<submenu name="Submenu" _label="Su_bmenu">
<menuitem name="ItemAbout" 
          verb="About" 
          label="_About" 
          pixtype="stock" 
          pixname="gtk-about"/>
</submenu>
</popup>
"""
        verbs = [('About', self.show_about), ('Preferences', self.show_preferences)]
        
        self.applet.setup_menu(xml, verbs, "Hello!")

    def show_about(self, obj, label, *data):
        print label
        print data

    def show_preferences(self, obj, label, *data):
        print label
        print data
        
def clipshare_factory(applet,iid):
    Clipshare(applet, iid)
    print 'Factory started'
    return gtk.TRUE

#Very useful if I want to debug. 
if __name__ == '__main__':
    if len(sys.argv) == 2:
        if sys.argv[1] == "-d": #Debug mode
            main_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
            main_window.set_title("Python Applet")
            main_window.connect("destroy", gtk.main_quit)
            app = gnomeapplet.Applet()
            clipshare_factory(app,None)
            app.reparent(main_window)
            main_window.show_all()
            gtk.main()
            sys.exit()
    else:
        #If called via gnome panel, run it in the proper way
        print 'starting factory'
        gnomeapplet.bonobo_factory('OAFIID:Clipshare_Factory', gnomeapplet.Applet.__gtype__, 'Sample Applet', '0.1', clipshare_factory)
