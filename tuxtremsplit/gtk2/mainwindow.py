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

import os
import gtk
import math
import pygtk
pygtk.require("2.0")
import threading
import gobject
from urlparse import urlparse
from urllib import unquote
from tuxtremsplit.core.xtmheader import XtmHeader
from tuxtremsplit.application.tools import Tools
from tuxtremsplit.gtk2.aboutwindow import AboutWindow
from tuxtremsplit.application.filedescriptor import FileDescriptor
from tuxtremsplit.customexceptions import InvalidHeaderError, \
                                          InvalidHeaderFieldSizeError
from tuxtremsplit.application.optparsefaker import OptparseFaker

gobject.threads_init()

GREEN_TUXTREMSPLIT = "#84B416"


class MainWindow(gtk.Window):

    def __init__(self):
        pass

    def start(self):
        """ Initialize entire GTK Window """
        from tuxtremsplit.application import Application

        self.__current_file = None
        self.__number_of_parts = 2
        self.__a_part_size = "0 Bytes"

        xtm_content_icon_path = Application().path_to(
                                    "pixmaps/xtm_content.png")
        execute_icon_path = Application().path_to("pixmaps/mini-cube.png")

        TuXtremSplit().logger.debug("Building GTK interface with Builder...")
        self.__builder = gtk.Builder()
        self.__builder.add_from_file(
            Application().path_to("glade/mainwindow.glade"))
        self.__builder.connect_signals(self)

        txs_logo = gtk.gdk.pixbuf_new_from_file(
            Application().path_to("pixmaps/tuxtremsplit.png"))

        self.__window = self.__builder.get_object("MainWindow")
        self.__window.drag_dest_set(0, [], 0)
        self.__window.set_icon(txs_logo)
        self.__window.set_title("%s version %s" %
            (Application().settings.name, Application().settings.version))
        self.__builder.get_object("ImageLogo").set_from_pixbuf(txs_logo)

        self.__label_draghere = self.__builder.get_object("labelDraghere")

        self.__vbox_actions = self.__builder.get_object("vboxActions")
        self.__vbox_actions.hide()

        self.__in_file_icon_fixed = self.__builder.get_object("fixed")
        self.__image_in_file_icon = self.__builder.get_object(
            "imageInFileIcon")
        self.__label_in_file_name = self.__builder.get_object(
            "labelInFileName")
        self.__label_in_file_size = self.__builder.get_object(
            "labelInFileSize")
        self.__label_in_file_is_xtm = self.__builder.get_object(
            "labelInFileIsXtm")
        self.__label_in_file_created_with = self.__builder.get_object(
            "labelCreatedWith")
        self.__label_in_file_part_count = self.__builder.get_object(
            "labelPartCount")
        self.__label_in_file_md5_checksums = self.__builder.get_object(
            "labelMd5Checksums")

        self.__fixed_join = self.__builder.get_object("fixedJoin")
        self.__image_xtm_content_join = self.__builder.get_object(
            "ImageXtmContentJoin")
        self.__image_xtm_content_join.set_from_pixbuf(
            gtk.gdk.pixbuf_new_from_file(xtm_content_icon_path))

        self.__fixed_split = self.__builder.get_object("fixedSplit")
        self.__image_xtm_content_join = self.__builder.get_object(
            "ImageXtmContentSplit")
        self.__image_xtm_content_join.set_from_pixbuf(
            gtk.gdk.pixbuf_new_from_file(xtm_content_icon_path))
        self.__hscal_split = self.__builder.get_object("hscalSplit")
        self.__label_split_parts = self.__builder.get_object(
            "labelSplitParts")
        self.__label_split_of_size = self.__builder.get_object(
            "labelSplitOfSize")
        self.__button_execute_split = self.__builder.get_object(
            "buttonExecuteJoin")
        self.__label_split_out_file_name = self.__builder.get_object(
            "labelSplitOutFileName")

        self.__image_join_out_file_icon = self.__builder.get_object(
            "imageJoinOutFileIcon")
        self.__label_join_out_file_name = self.__builder.get_object(
            "labelJoinOutFileName")
        self.__label_join_out_file_size = self.__builder.get_object(
            "labelJoinOutFileSize")

        self.__image_split_out_file_icon = self.__builder.get_object(
            "imageSplitOutFileIcon")
        self.__label_split_out_file_name = self.__builder.get_object(
            "labelSplitOutFileName")

        self.__builder.get_object("ImageExecuteJoinButton").set_from_pixbuf(
            gtk.gdk.pixbuf_new_from_file(execute_icon_path))
        self.__builder.get_object("ImageExecuteSplitButton").set_from_pixbuf(
            gtk.gdk.pixbuf_new_from_file(execute_icon_path))

        TuXtremSplit().logger.debug("Window is now ready!")
        TuXtremSplit().logger.debug("Creating thread...")
        thread = threading.Thread(target=gtk.main)
        TuXtremSplit().logger.debug("Starting thread...")
        thread.start()

    def quit_gtk(self):
        TuXtremSplit().logger.debug("Quitting GTK Main loop")
        gtk.main_quit()

    def _reset_details(self):
        """ Hide widgets to reset GUI """
        gobject.idle_add(self.__vbox_actions.hide)
        gobject.idle_add(self.__fixed_join.hide)
        gobject.idle_add(self.__fixed_split.hide)
        gobject.idle_add(self.__label_draghere.hide)

    def update_label_in_file_is_xtm(self, markup):
        gobject.idle_add(self.__label_in_file_is_xtm.set_markup, markup)

    def _hide_xtm_details(self):
        """ Hide Xtm details label widgets """
        gobject.idle_add(self.__label_in_file_created_with.hide)
        gobject.idle_add(self.__label_in_file_part_count.hide)
        gobject.idle_add(self.__label_in_file_md5_checksums.hide)

    def _show_xtm_details(self):
        """ Show Xtm details label widgets """
        gobject.idle_add(self.__label_in_file_created_with.show)
        gobject.idle_add(self.__label_in_file_part_count.show)
        gobject.idle_add(self.__label_in_file_md5_checksums.show)

    def _fill_in_xtm_details(self):
        """ Fill in label widgets with Xtm details """
        gobject.idle_add(self.__label_in_file_created_with.set_markup,
                         "<span size='9500'><b>Created by:</b> %s %s</span>" %
                         (self.__current_file.header.application_name,
                          self.__current_file.header.application_version))
        gobject.idle_add(self.__label_in_file_part_count.set_markup,
                         "<span size='9500'><b>Part count:</b> %d</span>" %
                         self.__current_file.header.number_of_parts)
        if self.__current_file.header.md5_enabled:
            md5_sums_content = ("<span foreground='%s'>Present</span>" %
                                GREEN_TUXTREMSPLIT)
        else:
            md5_sums_content = "Absent"

        gobject.idle_add(self.__label_in_file_md5_checksums.set_markup,
                         "<span size='9500'><b>MD5 sums:</b> %s</span>" %
                         md5_sums_content)

    def _show_in_file_info(self):
        """ Show the In file info box and fill in fields """
        gobject.idle_add(self.__vbox_actions.show)

        gobject.idle_add(self.__label_in_file_name.set_markup,
                         "<span size='14000'><b>%s</b></span>" %
                         Tools().truncate(self.__current_file.name, 27))

        gobject.idle_add(self.__label_in_file_size.set_markup,
                         "<b>Size:</b> %s" %
                         Tools().number_to_human_size(
                            self.__current_file.size))

        if self.__current_file.header.is_valid():
            self._fill_in_xtm_details()
            self._show_xtm_details()
            self._show_out_file_info()
        else:
            self._hide_xtm_details()

        gobject.idle_add(self.__image_in_file_icon.set_from_pixbuf,
                         Tools().mime_icon_from_file(
                            self.__current_file.path, size=128))

    def _show_out_file_info(self):
        """ Show the Out file info box and fill in fields """
        gobject.idle_add(self.__fixed_join.show)

        gobject.idle_add(self.__label_join_out_file_name.set_markup,
                         "<span size='14000'><b>%s</b></span>" %
                         Tools().truncate(
                            self.__current_file.header.original_filename, 37))
        gobject.idle_add(self.__label_join_out_file_size.set_markup,
                         "<b>Size:</b> %s" % Tools().number_to_human_size(
                         self.__current_file.header.original_filesize))
        gobject.idle_add(self.__image_join_out_file_icon.set_from_pixbuf,
                         Tools().get_file_mime_icon(self.__current_file, 64))

    def _show_out_file_split(self):
        """ Show the Split box """
        from tuxtremsplit.application import Application
        # Xtm mime icon
        gobject.idle_add(self.__image_split_out_file_icon.set_from_pixbuf,
                         gtk.gdk.pixbuf_new_from_file(
                            Application().path_to("pixmaps/xtm-mime.png")))

        # Name of the output file
        out_filename = self.__current_file.name + ".001.xtm"
        gobject.idle_add(self.__label_split_out_file_name.set_markup,
                         "<span size='14000'><b>%s</b></span>" %
                         Tools().truncate(out_filename, 30))
        gobject.idle_add(self.__image_xtm_content_join.set_tooltip_text,
                         out_filename)

        # Scale to choose outfile size/parts
        upper = Tools().bytes_to_mb(self.__current_file.size)
        ajust = gtk.Adjustment(value=2, lower=2, upper=upper, step_incr=2,
                               page_incr=2)
        gobject.idle_add(self.__hscal_split.set_adjustment, ajust)

        # Outfile size
        self.__a_part_size = self.__current_file.size / 2
        gobject.idle_add(self.__label_split_of_size.set_text,
                         "of %s" %
                         Tools().number_to_human_size(self.__a_part_size))

        gobject.idle_add(self.__fixed_split.show)

    def _update_hscal_split(self, value):
        """ Update labels around the split HScal """
        file_size_mb = Tools().bytes_to_mb(self.__current_file.size)
        value = file_size_mb if value > file_size_mb else value

        self.__number_of_parts = math.floor(value)
        self.__a_part_size = Tools().number_to_human_size(
                                self.__current_file.size / value)

        # Update labels
        gobject.idle_add(self.__label_split_parts.set_text, "%d parts" %
                         self.__number_of_parts)
        gobject.idle_add(self.__label_split_of_size.set_text, "of %s" %
                         self.__a_part_size)

    def _render(self, file_path):
        """
        Show/Hide GTK widgets depending of the given file_path.
        When passing a file with a valid XTM Header then show the join options
        When passing a file that's not a valid XTM file
        then show the split options
        """
        self.__current_file = FileDescriptor(file_path)

        # Don't do anything if passed data do not match a file
        if not os.path.exists(self.__current_file.path):
            return None

        self._reset_details()
        try:
            TuXtremSplit().logger.debug("Checking for a XTM Header...")
            self.__current_file.header = XtmHeader()
            self.__current_file.header.read_from(self.__current_file)
            self._show_in_file_info()
            self.update_label_in_file_is_xtm("<span foreground='%s'>This file"
                                             " is a valid Xtm file.</span>" %
                                             GREEN_TUXTREMSPLIT)
        except (InvalidHeaderError, InvalidHeaderFieldSizeError):
            self.update_label_in_file_is_xtm("Not an Xtm file.")
            self._show_in_file_info()
            self._show_out_file_split()

    def start_action(self, args, options):
        from tuxtremsplit.application import Application
        thread = threading.Thread(target=Application().start,
                                  args=(args, options,))
        thread.start()

    #-------------------------------------------------------------------------
    # Window GTK widget callback methods
    #-------------------------------------------------------------------------
    def on_MainWindow_destroy(self, widget):
        self.quit_gtk()

    def on_MainWindow_drag_motion(self, widget, context, x, y, time):
        context.drag_status(gtk.gdk.ACTION_COPY, time)
        return True

    def on_MainWindow_drag_drop(self, widget, context, x, y, time):
        self.__window.drag_get_data(context, context.targets[-1], time)
        return True

    def on_MainWindow_drag_data_received(self, widget, context, x, y, data,
                                         info, time):
        file_path = unquote(urlparse(data.get_text().strip()).path)
        TuXtremSplit().logger.debug("Dragged and dropped file %s" % file_path)
        self._render(file_path)

    def on_buttonQuit_clicked(self, widget):
        self.quit_gtk()

    def on_buttonAbout_clicked(self, widget):
        AboutWindow(self)

    def on_buttonExecuteSplit_clicked(self, widget):
        self.start_action([str(self.__current_file.path)],
                          OptparseFaker({'debug': None,
                                         'parts': self.__number_of_parts,
                                         'md5': None, 'sfx': None,
                                         'size': None}))

    def on_buttonExecuteJoin_clicked(self, widget):
        self.start_action([str(self.__current_file.path)],
                          OptparseFaker({'debug': None, 'parts': None,
                                         'md5': None, 'sfx': None,
                                         'size': None}))

    def on_hscalSplit_change_value(self, hscal, scroll_jump, value):
        if value < 2:
            return
        self._update_hscal_split(value)
