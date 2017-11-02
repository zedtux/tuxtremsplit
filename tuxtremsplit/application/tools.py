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

import re
import os
import sys
import gio
import gtk
import uuid
import struct


class Tools:
    """ Collection of tools """

    def TDateTime2UnixTimestamp(self, value):
        """ Convert Delphi TDateTime to readable datetime """
        return 0.0

    def is_installed(self):
        """ Return True if the current file is in the System prefix path """
        return __file__.startswith(sys.prefix)

    def hex_string_endian_swap(self, hexa_string):
        """
        Rearranges character-couples in a little endian hex string to
        a big endian hex string and vice-versa.
        'A0B9E340' => '40E3B9A0'
        """
        if len(hexa_string) % 2 != 0:
            return -1

        swapList = []
        for i in range(0, len(hexa_string), 2):
            swapList.insert(0, hexa_string[i:i + 2])

        return "".join(swapList)

    def to_binary(self, hex_string):
        """ Convert hex values to binary """
        ints = [int(hex_string[i:i + 2], 16)
                for i in range(0, len(hex_string), 2)]
        return struct.pack('B' * len(ints), *ints)

    def number_to_human_size(self, size):
        """
        Return given size as readable by humans.

        Fred Cirera
        http://blogmag.net/blog/read/38/Print_human_readable_file_size
        """
        for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return "%3.2f %s" % (size, x)
            size /= 1024.0

    def human_size_to_number(self, human_size):
        """ Convert human readable file size to number """
        match = re.search(r'(\d*\.?\d+)\s?(Bytes?|KB|MB|GB|TB)', human_size)
        if match:
            size, unit = match.group(1), match.group(2)
            try:
                number = int(size)
            except:
                return None
            if unit == "Byte" or unit == "Bytes":
                number = number
            elif unit == "KB":
                number = number * 1024
            elif unit == "MB":
                number = number * 1024 * 1024
            elif unit == "GB":
                number = number * 1024 * 1024 * 1024
            elif unit == "TB":
                number = number * 1024 * 1024 * 1024 * 1024
            return number
        else:
            return None

    def split_len(self, seq, length):
        """ Return given string splitted with given length """
        return [seq[i:i + length] for i in range(0, len(seq), length)]

    def constantize(self, name):
        return "-".join([word.lower() for word in name.split(" ")])

    def isnumeric(self, value):
        """
        Return True if the given value is numeric, else return False
        """
        try:
            float(value)
            return True
        except:
            return False

    def truncate(self, string, length):
        """
        Split the given string to the given lenght.

        Ex: If the string is 'that_file_name_is_too_long' and the given
        length is 10: 'that..long'
        """
        assert self.isnumeric(length), "Invalid argument type."
        assert string != "", "Missing argument."
        if length and len(string) > length:
            join_string = ".." if (length % 2) == 0 else "..."
            length -= len(join_string)
            extract_length = length / 2
            return "%s%s%s" % (string[0:extract_length],
                               join_string,
                               string[(extract_length * -1):])
        else:
            return string

    def mime_icon_from_file(self, file_path, size=96):
        """
        Find the icon of the given filename as a gtk.gdk.Pixbuf.
        Return None if the icon can't be found.

        If real_file is True, this method will use a gio.File,
        else, the icon will be defined using the filename.
        """
        file_icon = None
        target_file = gio.File(file_path)
        icon = target_file.query_info("standard::icon").get_icon()
        if isinstance(icon, gio.ThemedIcon):
            theme = gtk.icon_theme_get_default()
            theme_icon = theme.choose_icon(icon.get_names(), size, 0)
            if theme_icon:
                file_icon = theme_icon.load_icon()
        elif isinstance(icon, gio.FileIcon):
            iconpath = icon.get_file().get_path()
            file_icon = gtk.gdk.pixbuf_new_from_file(iconpath)

        if icon.get_names()[0] == "application-octet-stream" or not file_icon:
            if not theme:
                theme = gtk.icon_theme_get_default()
            icon_names = gio.content_type_get_icon(
                gio.content_type_guess(file_path)).get_names()
            theme_icon = theme.choose_icon(icon_names, size, 0)
            if theme_icon:
                file_icon = theme_icon.load_icon()
            else:
                file_icon = theme.choose_icon(["application-octet-stream"],
                                              size, 0).load_icon()
        return file_icon

    def get_file_mime_icon(self, file_descriptor, size):
        """
        Create a file in /tmp with the header of the source file
        to retrive the original file mime icon and return it.
        """
        from tuxtremsplit.application import Application
        tmp_file_path = "/tmp/%s" % uuid.uuid4()
        tmp_file = open(tmp_file_path, "w")
        source_file = open(file_descriptor.path)
        source_file.seek(Application().settings.xtm_header.size)
        tmp_file.write(source_file.read(10))
        source_file.close()
        tmp_file.close()
        source_file_icon = self.mime_icon_from_file(tmp_file_path, size=size)
        os.remove(tmp_file_path)
        return source_file_icon

    def bytes_to_mb(self, size):
        return size / 1024.0 / 1024.0
