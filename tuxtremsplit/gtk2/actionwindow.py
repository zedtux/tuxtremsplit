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
import gobject
import threading

from tuxtremsplit.application.tools import Tools
from tuxtremsplit.gtk2.eventsbus import EventsBus


class ActionWindow(gtk.Window):
    """ GTK2 Graphical User Interface mother class """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ActionWindow, cls).__new__(
                cls, *args, **kwargs)
        return cls._instance

    def start(self, standalone=True):
        """ Initialize entire GTK Window """
        self.__standalone = standalone

        if self.__standalone:
            TuXtremSplit().logger.debug("Starting ActionWindow in "
                                        "standalone mode.")
        else:
            TuXtremSplit().logger.debug("Starting ActionWindow not in "
                                        "standalone mode.")

        TuXtremSplit().logger.debug("Building GTK interface with Builder...")
        from tuxtremsplit.application import Application
        self.__builder = gtk.Builder()
        self.__builder.add_from_file(
            Application().path_to("glade/actionwindow.glade"))
        self.__builder.connect_signals(self)

        # Prepare Window
        txs_logo = gtk.gdk.pixbuf_new_from_file(
            Application().path_to("pixmaps/small_tuxtremsplit.png"))
        self.__window = self.__builder.get_object("ActionWindow")
        if self.__standalone:
            self.__window.set_icon(txs_logo)
        self.__window.set_default_size(200, -1)
        self.__window_logo = self.__builder.get_object("ImageLogo")
        self.__window_logo.set_from_pixbuf(txs_logo)

        #
        # Build hooks
        #

        # Action
        self.__status_label = self.__builder.get_object("StatusLabel")
        self.__status_label_text = self.__status_label.get_text()

        # Action description
        self.__description_label = self.__builder.get_object(
            "DescriptionLabel")

        self.__action_progressbar = self.__builder.get_object("Progressbar")

        # Show details
        self.__treeview_xtm_statuses = self.__builder.get_object(
            "treeviewXtmStatuses")
        self.__xtm_liststore = self.__treeview_xtm_statuses.get_model()
        self.__scrolledwindow_xtm_statuses = self.__builder.get_object(
            "scrolledwindowXtmStatuses")
        self.__expander_label = self.__builder.get_object("expanderLabel")
        self.__expander_label_original_text = self.__expander_label.get_text()
        self.__treeviewcolumn_md5 = self.__builder.get_object(
            "treeviewcolumnMd5")

        # Buttons: Skip and Cancel
        self.__hbuttonbox_skip_cancel = self.__builder.get_object(
            "hbuttonboxSkipCancel")
        # Buttons: Skip
        self.__button_skip_button = self.__builder.get_object("SkipButton")
        # Buttons: Cancel
        self.__button_cancel_button = self.__builder.get_object(
            "CancelButton")
        # Buttons: After MD5 check
        self.__hbuttonbox_after_check = self.__builder.get_object(
            "hbuttonboxAfterCheck")
        self.__hbuttonbox_after_check.hide()
        # Buttons: Close
        self.__hbuttonbox_end = self.__builder.get_object("hbuttonboxEnd")
        self.__hbuttonbox_end.hide()
        # Buttons: I d'ont care, join all files, Oops... Let me check.
        self.__hbuttonbox_after_check = self.__builder.get_object(
            "hbuttonboxAfterCheck")
        self.__hbuttonbox_after_check.hide()

        # This window can be started in standalone mode
        # (double click on xtm file for example)
        # or from main window
        if self.__standalone:
            gobject.threads_init()
            TuXtremSplit().logger.debug("Creating thread for GTK...")
            thread = threading.Thread(target=gtk.main)
            TuXtremSplit().logger.debug("Starting GTK thread...")
            thread.start()

    def render(self, xtm_group):
        """ Update the GtkTreeView for the given XtmGroup instance """
        xtm_group.reset_file_position()
        filename = xtm_group.main_file
        while filename:
            self.__xtm_liststore.append([0, "Idle", filename.name])
            filename = xtm_group.next_file()

    def kill_processing_task(self):
        EventsBus().stop_action_if_processing()

    def skip_processing_task(self):
        gobject.idle_add(EventsBus().skip_action)

    def quit_gtk(self):
        TuXtremSplit().logger.debug("Quitting GTK Main loop")
        gtk.main_quit()

    def splitting(self, filename, filesize, parts_count, from_path):
        """ Describe to the user the current action """
        description = "I'm splitting into %d parts " % parts_count
        description += "the file <b>%s</b> " % filename
        description += ("(%s) " %
                        Tools().number_to_human_size(filesize))
        description += "from %s" % from_path
        self._update_status_text("splitting", parts_count)
        self.update_description_text(description)

    def joining(self, filename, filesize, parts_count, from_path):
        """ Describe to the user the current action """
        description = "I'm joining from %d parts " % parts_count
        description += "the file <b>%s</b> " % filename
        description += ("(%s) " %
                        Tools().number_to_human_size(filesize))
        description += "from %s" % from_path
        self._update_status_text("joining", parts_count)
        self.update_description_text(description)

    def checking_md5_sums(self, parts_count, from_path):
        """ Describe to the user the current action """
        description = "I'm checking %d parts " % parts_count
        description += "from %s" % from_path
        self._update_status_text("checking", parts_count)
        self.update_description_text(description)

    def _update_status_text(self, action_name, count=1):
        gobject.idle_add(self.__status_label.set_text,
                         self.__status_label_text %
                         (action_name, "s" if count > 1 else ""))

    def update_description_text(self, description):
        gobject.idle_add(self.__description_label.set_markup, description)


    # ~~~ Progress bar ~~~
    def update_progressbar(self, fraction):
        """ Update total treatment progressbar """
        gobject.idle_add(self.__action_progressbar.set_fraction, fraction)

    def update_file_progressbar(self, file_id, fraction):
        """ Update given file id treatment progressbar """
        row = self.__xtm_liststore.iter_nth_child(None, (file_id - 1))
        gobject.idle_add(self.__xtm_liststore.set_value,
                         row, 0, fraction * 100)

    def update_file_status(self, file_id, failed):
        row = self.__xtm_liststore.iter_nth_child(None, (file_id - 1))
        if failed:
            color, text = "red", "Dying"
        else:
            color, text = "darkgreen", "Healthy"
        gobject.idle_add(self.__xtm_liststore.set_value,
                         row, 1, "<span foreground=\"%s\"><b>%s</b></span>" %
                         (color, text))

    def reset_files_percentage(self):
        gobject.idle_add(self.__action_progressbar.set_fraction, 0.0)
        iter = self.__xtm_liststore.get_iter_first()
        while True:
            gobject.idle_add(self.__xtm_liststore.set_value, iter, 0, 0.0)
            iter = self.__xtm_liststore.iter_next(iter)
            if not iter:
                break

    # ~~~ Buttons ~~~
    # Close
    def show_close_button(self):
        gobject.idle_add(self.__hbuttonbox_end.show)
        gobject.idle_add(self.__hbuttonbox_skip_cancel.hide)

    def show_buttons_after_md5_check_failed(self):
        gobject.idle_add(self.__hbuttonbox_skip_cancel.hide)
        gobject.idle_add(self.__hbuttonbox_after_check.show)

    #-------------------------------------------------------------------------
    # Window GTK widget callback methods
    #-------------------------------------------------------------------------
    def on_delete_event(self, widget, event):
        self.kill_processing_task()
        self.quit_gtk()

    def on_CloseButton_clicked(self, widget):
        self.quit_gtk()

    def on_ContinueButton_clicked(self, widget):
        TuXtremSplit().logger.debug("ContinueButton clicked")

    def on_OopsButton_clicked(self, widget):
        self.quit_gtk()

    def on_SkipButton_clicked(self, widget):
        self.skip_processing_task()
        self.reset_files_percentage()

    def on_CancelButton_clicked(self, widget):
        self.kill_processing_task()

    def on_expanderXtmFilesStatuses_activate(self, widget):
        """ Ensure window size is always optimum """
        if widget.get_expanded():
            # Resize the window to the normal size
            widget.remove(widget.child)
            gobject.idle_add(self.__window.resize, 200, 1)
        else:
            gobject.idle_add(self.__window.resize, 200, 350)
            if not widget.get_child():
                widget.add(self.__scrolledwindow_xtm_statuses)

    def on_action_success(self):
        gobject.idle_add(self.__expander_label.set_markup, "%s %s" %
            (self.__expander_label_original_text,
            "<span foreground=\"darkgreen\"><b>Success</b></span>"))
        self.show_close_button()

    def on_action_failed(self):
        gobject.idle_add(self.__expander_label.set_markup, "%s %s" %
            (self.__expander_label_original_text,
            "<span foreground=\"red\"><b>Failed</b></span>"))
        self.show_close_button()

    def after_md5_check(self):
        gobject.idle_add(self.__button_skip_button.hide)
        gobject.idle_add(self.__treeviewcolumn_md5.set_visible, False)
