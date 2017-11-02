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
from tuxtremsplit.application.tools import Tools


class BinaryWriter(object):
    """ Write string, numbers, booleans as binary """

    def __init__(self, output_file):
        """ Constructor """
        self.__output_file = output_file
        self.__position = output_file.tell()

    def get_position(self):
        return self.__position
    position = property(get_position)

    def move_to(self, offset):
        """ Move from position of the offset """
        self.__output_file.seek(self.__position + offset)

    def write_number(self, value, bytes):
        """ Write a number as hex value to file """
        write_value = "%0*X" % (bytes * 2, value)
        self.__output_file.write(
            Tools().to_binary(
                Tools().hex_string_endian_swap(write_value)))

    def write_string(self, value, bytes):
        """ Write a string as hex value to file """
        self.__output_file.write(Tools().to_binary(value.encode("hex")))

    def write_boolean(self, value, bytes):
        """ Write a boolean as hex value to file """
        write_value = "%0*X" % (bytes*2, 1 if value else 0)
        self.__output_file.write(Tools().to_binary(write_value))
