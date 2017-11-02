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
import re
from tuxtremsplit.application.filedescriptor import FileDescriptor
from tuxtremsplit.core.xtmgroup import XtmGroup
from tuxtremsplit.customexceptions import Md5SumsNotEnabledInXtmHeaderError


class XtmGroupIdentificator(object):
    """ Manage XTM files group """

    def __init__(self):
        """ Constructor """
        self.__group = None

    def identify_from(self, file_descriptor):
        """ Populate the XtmGroup from given path """
        # Put directly the .001.xtm file in the group
        self.__group = XtmGroup(file_descriptor)

        TuXtremSplit().logger.debug("Gathering other XTM files for %s" %
                                    file_descriptor.name)

        # Now search all other files matching the pattern
        for filename in os.listdir(file_descriptor.basepath):
            file_path = os.path.join(file_descriptor.basepath, filename)
            if os.path.isfile(file_path):
                file = FileDescriptor(file_path)
                # Collect all matching files except the .001.xtm that has
                # already appended to the collection of XTM files
                if re.search(self.__group.pattern, file.name) and \
                   file.name.find(".001.") == -1:
                    TuXtremSplit().logger.debug("%s match the group." %
                                                file.name)
                    self.__group.append(file)

        TuXtremSplit().logger.debug("%s group contain %d parts." %
                                    (file_descriptor.name, self.size))
        self.__group.inspect()

    def get_size(self):
        """ Return the count of collected files """
        return self.__group.size
    size = property(get_size)

    def empty(self):
        """ Return True if the group is empty otherwise return False """
        return self.size == 0

    def get_xtm_files(self):
        """ Return the collection of XTM files """
        return self.__group
    group = property(get_xtm_files)

    def is_valid(self):
        """
        Verify that the number of xtm_files in the group
        is the same than described in the XTM Header
        And if md5 option is enabled check md5 of files.
        """
        if not self.size == self.__group.main_file.header.number_of_parts:
            return False

        try:
            self.__group.check_md5sums()
            if not self.__group.valid:
                return False
        except Md5SumsNotEnabledInXtmHeaderError as warning:
            try:
                TuXtremSplit().logger.warn(unicode(warning))
            except:
                TuXtremSplit().logger.warn(warning)

        return True
