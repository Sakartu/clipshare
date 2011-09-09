#!/usr/bin/env python
import pygtk
pygtk.require('2.0')

import gtk
import gnomeapplet
import gobject

import sys

class Clipshare(gnomeapplet.Applet):
    #Reads a utf-8 file, reads all lines and returns them as a list with newlines stripped
#    def readFile(self,fileName):
#        f = codecs.open(fileName)
#        allLines = f.readlines()
#        f.close()
#        strippedLines = [line.strip()  for line in allLines]
#        return strippedLines
#
#    #Picks a random word from the list. If its empty, it starts with original list again.
#    def getNextWord(self):
#        if len(self.wordsToShow) == 0:
#            self.wordsToShow = self.allWords[:]
#        selectedWord = random.choice(self.wordsToShow)
#        self.wordsToShow.remove(selectedWord)
#        english,hindi = selectedWord.split("|")
#        wordInMarkups = "<b>" + english + "</b>   " + hindi
#        return wordInMarkups
#
#    #Displays the next word to GUI. Uses set_markup to use HTML
#    def displayNextWord(self):
#        wordToShow = self.getNextWord()
#        self.label.set_markup(wordToShow)
#        return True

    def __init__(self,applet,iid):
        self.applet = applet

        self.label = gtk.Label("")
        self.label.set_markup("<b>Blablabla</b>")
        self.applet.add(self.label)

        self.applet.show_all()
        #gobject.timeout_add(self.timeout_interval, self.displayNextWord)

#Register the applet datatype
gobject.type_register(Clipshare)

def clipshare_factory(applet,iid):
    Clipshare(applet,iid)
    return gtk.TRUE

#Very useful if I want to debug. To run in debug mode python hindiScroller.py -d
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

#If called via gnome panel, run it in the proper way
if __name__ == '__main__':
    gnomeapplet.bonobo_factory("OAFIID:GNOME_Clipshare_Factory", Clipshare.__gtype__, "hello", "0", clipshare_factory)
