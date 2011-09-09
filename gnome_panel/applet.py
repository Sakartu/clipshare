#!/usr/bin/env python
import pygtk
pygtk.require('2.0')

import gtk
import gnomeapplet

import sys

class Clipshare(gnomeapplet.Applet):

    def __init__(self, applet, iid):
        self.applet = applet

        icon = gtk.Image()
        icon.set_from_stock(gtk.STOCK_PASTE, gtk.ICON_SIZE_SMALL_TOOLBAR)
        self.applet.add(icon)
        self.applet.show_all()
        self.create_menu(["Empty"] * 5)

    def create_menu(self, clipboard_contents):
        xml = '<popup name="button3"> <submenu name="History" _label=" _History\
                " pixtype="stock" pixname="gtk-index">'
        verbs = []
        for item in clipboard_contents:
            xml += '<menuitem name="' + item + \
                    '" verb="' + item + \
                    '" label="' + self.shorten(item) + \
                    '" pixtype="stock" pixname="gtk-index"/>'
            verbs.append((item, self.handle_select))
        xml += " </submenu> </popup> "

        self.applet.setup_menu(xml, verbs, None)

    def shorten(self, item):
        if len(item) > 13:
            return item[:10] + '...'
        else:
            return item

    def handle_select(self, obj, name, *data):
        #set the current clipboard contents to name
        pass
        
#Very useful if I want to debug. 
if __name__ == '__main__':
    if len(sys.argv) == 2:
        if sys.argv[1] == "-d": #Debug mode
            main_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
            main_window.set_title("Python Applet")
            main_window.connect("destroy", gtk.main_quit)
            app = gnomeapplet.Applet()
            Clipshare(app, None)
            app.reparent(main_window)
            main_window.show_all()
            gtk.main()
            sys.exit()
    else:
        #If called via gnome panel, run it in the proper way
        print 'starting factory'
        gnomeapplet.bonobo_factory('OAFIID:Clipshare_Factory', gnomeapplet.Applet.__gtype__, 'Sample Applet', '0.1', Clipshare)
