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


class FileExtension(object):
    """ Helper class to manage File extensions """

    def __init__(self, filename):
        """ Constructor """
        self.__filename_with_extension = filename
        self.__filename = None
        self.__extension = None
        TuXtremSplit().logger.debug(
            "New FileExtension for %s" % self.__filename_with_extension)

        self.parse()

    def parse(self):
        """ Parse the filename """
        if self.__filename_with_extension.find(".") > -1:
            TuXtremSplit().logger.debug(
                "%s has an extension" % self.__filename_with_extension)
            self.__filename, _, self.__extension = \
            self.__filename_with_extension.rpartition(".")
        else:
            TuXtremSplit().logger.debug(
                "%s has no extension" % self.__filename_with_extension)
            self.__filename = self.__filename_with_extension

        TuXtremSplit().logger.debug("Filename: %s" % self.__filename)
        TuXtremSplit().logger.debug("Extension: %s" % self.__extension)

    def _is(self, extension_string):
        """ Return True if the extension match the given string """
        return self.__extension and self.__extension != "" and \
               self.__extension.lower() == extension_string

    def get_is_xtm(self):
        """ Return True if the extension is 'xtm' otherwise return False """
        return self._is("xtm")
    is_xtm = property(get_is_xtm)

    def get_is_exe(self):
        """ Return True if the extension is 'exe' otherwise return False """
        return self._is("exe")
    is_exe = property(get_is_exe)

    def __len__(self):
        return len(self.__extension)

    def as_exe(self):
        self.__extension = "exe"

    def as_xtm(self):
        self.__extension = "xtm"

    def __str__(self):
        return self.__extension if self.__extension else ""

    def is_found(self):
        return not self.__extension is None
    found = property(is_found)
