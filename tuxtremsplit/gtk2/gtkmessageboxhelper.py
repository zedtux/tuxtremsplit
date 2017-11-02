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
# along with TuXtremSplit; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

# From http://bytes.com/topic/python/answers/717463-showing-message-dialog-thread-using-gtk
import gtk
import gobject


class GtkMessageBoxHelper(gtk.MessageDialog):

    def __init__(self, parent, message, quit_gtk_after_ok=False):
        gtk.MessageDialog.__init__(self, parent,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_ERROR, gtk.BUTTONS_OK)
        self.set_default_response(gtk.RESPONSE_OK)
        self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.set_transient_for(parent)
        self.set_markup("<big><b>Too bad... An error occured:</b></big>")
        self.format_secondary_text(message)
        if quit_gtk_after_ok:
            self.connect("response", gtk.main_quit)
        else:
            self.connect("response", self._handle_clicked)

    def _handle_clicked(self, *args):
        self.destroy()

    def show_dialog(self):
        gobject.timeout_add(0, self._do_show_dialog)

    def _do_show_dialog(self):
        self.show_all()
        return False
