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
import statvfs
from tuxtremsplit.application.filedescriptor import FileDescriptor
from tuxtremsplit.customexceptions import AlreadyExistingFileError


class PathDescriptor(object):
    """ Parse a path and provide some methods about it """

    def __init__(self, path):
        """ Constructor """
        self.__path = path
        self.__files = []
        self.__first_xtm_files = []
        TuXtremSplit().logger.debug("New PathDescriptor for %s" % self.__path)

    def collect_files(self):
        """ Collect files from given directory path """
        if len(self.__files) > 0:
            return self.__files

        TuXtremSplit().logger.debug("Collecting files from %s..." % self.path)
        for filename in os.listdir(self.path):
            file_path = os.path.join(self.path, filename)
            if os.path.isfile(file_path):
                TuXtremSplit().logger.debug("Adding file %s" % file_path)
                self.__files.append(FileDescriptor(file_path))

        return self.__files
    files = property(collect_files)

    def collect_first_xtm_files(self):
        """ Collect only files ending by .001.xtm or .001.exe """
        if len(self.__first_xtm_files) > 0:
            return self.__first_xtm_files

        for file in self.files:
            if (file.extension.is_xtm or file.extension.is_exe) and \
               file.is_main_file:
                TuXtremSplit().logger.debug("To be checked: %s" % file.name)
                self.__first_xtm_files.append(file)

        return self.__first_xtm_files
    first_xtm_files = property(collect_first_xtm_files)

    def open_file(self, filename, write):
        """
        Create a FileDescriptor for the output file and return it
        if doesn't otherwise raise an error
        """
        output_file_path = os.path.join(self.path, filename)
        TuXtremSplit().logger.debug(
            "Checking output file %s..." % output_file_path)
        if os.path.exists(output_file_path):
            raise AlreadyExistingFileError(
                "The file %s already exists." % output_file_path)
        TuXtremSplit().logger.debug(
            "Creating output file %s..." % output_file_path)
        # Create a new FileDescriptor and create the output file
        output_file = FileDescriptor(output_file_path)
        output_file.open_file(write=True)
        return output_file

    def get_path(self):
        """ Return the path """
        return self.__path
    path = property(get_path)
    name = property(get_path)

    def get_is_file(self):
        """ Return always False """
        return False
    is_file = property(get_is_file)

    def get_is_directory(self):
        """ Return always True """
        return True
    is_directory = property(get_is_directory)

    def free_space(self):
        """ Return destination free space """
        stats = os.statvfs(self.path)
        return stats[statvfs.F_BAVAIL] * long(stats[statvfs.F_BSIZE])

    def has_enough_free_space(self, size):
        """
        Return True when destination space has enough free space
        otherwise return False
        """
        TuXtremSplit().logger.debug(
            "Destination has %d octets free." % self.free_space())
        return self.free_space() > size
