# TuXtremSplit - A Linux Xtremsplit file tool
#
# Copyright (C) 2010 zedtux <zedtux@zedroot.org>
#
# TuXtremSplit is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# TuXtremSplit is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TuXtremSplit; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

import os
import gtk
import xdg.Mime
import nautilus
import threading

from tuxtremsplit.common.consts import APPLICATION_TITLE, VERSION, ICON_PATH
from urlparse import urlparse

print _("Initializing %s-nautilus-extension version %s" % (APPLICATION_TITLE, VERSION))

# nautilus.LocationWidgetProvider: Nautilus will request a widget to be
#                                  displayed at the top of the directory listing.
class TxsNautilusBar(nautilus.LocationWidgetProvider):
    
    def __init__(self):
        self.__window = None
        self.__working_path = ""
    
    def get_widget(self, uri, window):
        """ This method is automatically called by nautilus """
        self.__window = window
        return self.make_widget_if(self.have_xtm_file_in(uri))
    
    def have_xtm_file_in(self, uri):
        """ Verify that xtm file exists and return True if exists, else False """
        parsed_url = urlparse(uri)
        if parsed_url.scheme == "file" and parsed_url.path:
            for file in os.listdir(parsed_url.path):
                mime = xdg.Mime.get_type_by_name(file)
                print "file:%s mime:%s" % (file, mime)
                if mime and str(mime) == "application/x-extension-xtm":
                    self.__working_path = parsed_url.path
                    return True
                    break
        return False
    
    def switch_widget_state(self, on=True):
        """ Current path contain Xtm file, so show the banner """
        self.initialize_widget() if on else None
    
    def make_widget_if(self, show):
        return self.initialize_widget() if show else None
    
    def initialize_widget(self):
        """ Create and initialize gtk.HBox, gtk.Lable and gtk.Button """
        icon = gtk.Image()
        icon.set_from_file(ICON_PATH)
        icon.show()
        
        label_description = gtk.Label(_("This folder contains Xtremsplit files. You can use TuXtremSplit to join them."))
        label_description.set_alignment(0.0, 0.5)
        label_description.set_line_wrap(False)
        label_description.show()
        
        button_start_tuxtremsplit = gtk.Button(_("Join with TuXtremSplit"))
        button_start_tuxtremsplit.connect("clicked", self.on_button_start_tuxtremsplit_clicked)
        button_start_tuxtremsplit.show()
        
        widget = gtk.HBox()
        widget.pack_start(icon, expand=False, fill=False)
        widget.pack_start(label_description, expand=True, fill=True, padding=4)
        widget.pack_start(button_start_tuxtremsplit, expand=False, fill=False, padding=4)
        widget.show()
        
        return widget
    
    def on_button_start_tuxtremsplit_clicked(self, widget):
        """ Start TuXtremSplit passing current path as argument """
        try:
            threading.Thread(target=self.execute_tuxtremsplit).start()
        except Exception, e:
            md = gtk.MessageDialog(self.__window,
                                   gtk.DIALOG_DESTROY_WITH_PARENT,
                                   gtk.MESSAGE_ERROR, 
                                   gtk.BUTTONS_CLOSE,
                                   "Error while creating thread: %s" % e)
            md.run()
            md.destroy()
    
    def execute_tuxtremsplit(self):
        try:
            os.system("txs.py %s" % self.__working_path)
        except Exception, e:
            md = gtk.MessageDialog(self.__window,
                                   gtk.DIALOG_DESTROY_WITH_PARENT,
                                   gtk.MESSAGE_ERROR, 
                                   gtk.BUTTONS_CLOSE,
                                   "Error starting TuXtremSplit: %s" % e)
            md.run()
            md.destroy()
