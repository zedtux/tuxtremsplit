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

from tuxtremsplit.application.exceptionthread import ExceptionThread


class XtmMd5Checker(ExceptionThread):
    """
    XTM Md5 Checker
    Extract MD5 sums then check files.
    """

    def __init__(self):
        """ Constructor """
        TuXtremSplit().logger.debug("XtmMd5Checker#__init__()")
        # Callbacks
        self.file_with_index = None
        self.after_finished = None
        # Variables
        self.md5_sums = None
        self.last_file = None
        self.size = None
        self.index = None
        self.__stop = False
        self.__all_valid = True
        self.__skipped = False
        ExceptionThread.__init__(self)

    def stop(self, skip=False):
        self.__stop = True
        self.__skipped = skip
        self.__current_file.stop_md5_check()

    def get_success(self):
        return self.__all_valid
    success = property(get_success)

    def get_skipped(self):
        return self.__skipped
    skipped = property(get_skipped)

    def run_with_exception(self):

        # If not already done, extract MD5 sums from last XTM file
        if not self.md5_sums:
            self.md5_sums = self.last_file.extract_md5_sums_for(self.size)
            TuXtremSplit().logger.debug("Sums are %s" % self.md5_sums)

        # Then check each files
        while not self.__stop:
            try:
                # Get an MD5 sum and the file that should match
                md5_sum = self.md5_sums[self.index]
            except:
                break

            self.__current_file = self.file_with_index(self.index + 1)

            if self.size == (self.index + 1):
                self.__current_file.check_md5_sum(md5_sum, ignore=self.size)
            else:
                self.__current_file.check_md5_sum(md5_sum)

            if not self.__current_file.valid:
                self.__all_valid = False

            self.index += 1

        self.after_finished()
