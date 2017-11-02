# -*- coding: utf-8 -*-
# TuXtremSplit - A Linux Xtremsplit file tool
#
# Copyright (C) 2011 zedtux <zedtux@zedroot.org>
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
# along with TuXtremSplit; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA
from tuxtremsplit import TuXtremSplit

import gtk
import pygtk
pygtk.require("2.0")


class AboutWindow(gtk.AboutDialog):

    def __init__(self, parent):
        from tuxtremsplit.application import Application
        app_name = Application().settings.name
        logo_path = Application().path_to("pixmaps/tuxtremsplit.png")
        gtk.AboutDialog.__init__(self)
        self.set_transient_for(parent)
        self.set_name(app_name)
        self.set_version(Application().settings.version)
        self.set_icon(gtk.gdk.pixbuf_new_from_file(logo_path))
        self.set_logo(gtk.gdk.pixbuf_new_from_file(logo_path))
        self.set_website(Application().settings.homepage)
        self.set_website_label("%s Website" % app_name)
        self.set_comments("%s allow you to join Xtremsplit files and "
                          "split a file into Xtremsplit files." % app_name)
        self.set_authors(["%s <%s>" %
                          (Application().settings.author,
                           Application().settings.author_email)])
        self.set_copyright("Copyright © 2012 %s" %
                            Application().settings.author)
        self.set_wrap_license(True)
        self.set_license(Application().settings.licence %
                         (app_name, app_name, app_name))
        self.run()
        self.destroy()
