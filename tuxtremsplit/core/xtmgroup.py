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

import re
import os
from tuxtremsplit.customexceptions import BelongsNotToTheGroupError, \
                                          ArgumentError, \
                                          NoEnoughSpaceError, \
                                          Md5SumsNotEnabledInXtmHeaderError
from tuxtremsplit.application.filedescriptor import FileDescriptor
from tuxtremsplit.gtk2.eventsbus import EventsBus
from tuxtremsplit.core.xtmmd5checker import XtmMd5Checker
from tuxtremsplit.gtk2.actionwindow import ActionWindow


class XtmGroup(object):
    """ Collection of XTM Files """

    def __init__(self, original_file_descriptor=None):
        """ Constructor """
        self.__zero_zero_one = original_file_descriptor
        if original_file_descriptor:
            original_file_descriptor.group = self
        self.__group_files = []
        self.__current_source = None
        self.__destination = None
        self.__create_sfx = False
        self.__md5_sum_index = 0
        self.already_checked = 0.0
        self.__total_size = None
        self.__thread = None

        self.__interator_index = 0
        self.reset_file_position()

    def get_main_file(self):
        """
        Return the FileDescriptor for the .001.xtm or
        .001.exe file of the group
        """
        return self.__zero_zero_one
    main_file = property(get_main_file)

    def get_matching_pattern(self):
        """ Return the Regular expression to match group files """
        return r"%s\.\d{3}\.(xtm|exe)$" % re.escape(self.main_file.name[0:-8])
    pattern = property(get_matching_pattern)

    def get_size(self):
        """ Return the size of the group """
        return len(self.__group_files) + 1
    size = property(get_size)

    def get_size_of_all_files(self):
        """ Return the size of the group """
        if self.__total_size is None:
            self.__total_size = self.main_file.size
            for file in self.__group_files:
                self.__total_size += file.size
        return self.__total_size
    size_of_all_files = property(get_size_of_all_files)

    def get_group_md5_valid(self):
        if self.__thread:
            return self.__thread.success or self.__thread.skipped
        else:
            return True
    valid = property(get_group_md5_valid)

    def get_create_sfx(self):
        return self.__create_sfx

    def set_create_sfx(self, value):
        self.__create_sfx = value
        TuXtremSplit().logger.debug("XtmGroup will produce an SFX: %r" %
                                    self.__create_sfx)
        self._refresh_main_file()
    create_sfx = property(get_create_sfx, set_create_sfx)

    def get_group_name(self):
        """ Generate a nice name (only for output to the user) """
        return "Group for %s" % self.main_file.name
    name = property(get_group_name)

    def _refresh_main_file(self):
        """ Update the main file depending of the create_sfx attribute """
        from tuxtremsplit.application import Application
        if self.create_sfx:
            self.__zero_zero_one.extension.as_exe()
            self.main_file.size += Application().settings.xtm_sfx.header_size
            self.main_file.size += Application().settings.xtm_sfx.footer_size

    def append(self, file_descriptor):
        """ Add a new FileDescriptor instance to the group """
        TuXtremSplit().logger.debug(
            "Appending %s into %s" % (file_descriptor.name, self.name))
        file_descriptor.group = self
        self.__group_files.append(file_descriptor)

    def inspect(self):
        """ Output the list of files in the group """
        TuXtremSplit().logger.debug(self.__zero_zero_one.path)
        for xtm_file in self.__group_files:
            TuXtremSplit().logger.debug(xtm_file.path)

    def to(self, destination_descriptor):
        """ Define the destination path of the group files """
        self.__destination = destination_descriptor
        return self

    def next_file(self):
        """ Iterator over XTM files of the group """
        TuXtremSplit().logger.debug("Iterating from %d" %
                                    self.__interator_index)
        file = self.file_with_index(self.__interator_index)
        self.__interator_index += 1
        return file

    def reset_file_position(self):
        self.__interator_index = 2

    def is_the_last_file(self, descriptor):
        """
        Return True if the given descriptor describe the latest file
        of the group otherwise return False.
        In the other hand raise an BelongsNotToTheGroupError
        if the descriptor didn't belongs to the group
        """
        if not re.search(self.pattern, descriptor.name):
            raise BelongsNotToTheGroupError(
                "The file %s didn't belongs to the group for %s" %
                (descriptor.name, self.main_file.name))

        xtm_id = re.search(r'\.(\d{3})\.(xtm|exe)$', descriptor.name)
        if not xtm_id:
            raise ArgumentError("Could not extract the XTM id from %s" %
                                descriptor.name)
        return int(xtm_id.group(1)) == self.size

    def create_from(self, source_file_descriptor):
        """ Save the given source FileDescriptor and return self """
        self.__current_source = source_file_descriptor

        # Ruby style
        return self

    def dividing_from_parts(self, parts_count):
        """
        Create the XtmGroup content from the given FileDescriptor
        dividing it using the given parts count
        """
        if not self.__current_source:
            raise ArgumentError(
                "You must define the source using create_from method.")

        parts_count = int(parts_count)
        if not parts_count > 1:
            raise ArgumentError(
                "Only greater values than 1 are accepted for --parts option.")

        size = self.__current_source.size / parts_count
        self._make_group(size, parts_count)

        # Ruby style
        return self

    def dividing_from_size(self, size):
        """
        Create the XtmGroup content from the given FileDescriptor
        dividing it using the given maximum part size
        """
        if not self.__current_source:
            raise ArgumentError(
                "You must define the source using create_from method.")

        if not size:
            raise ArgumentError(
                "Invalid maximum file size. (<size>Byte/Bytes/KB/MB/GB/TB)")

        count = int(round(self.__current_source.size / (size * 1.0)))
        self._make_group(size, count)

        # Ruby style
        return self

    def _make_group(self, size, count):
        """ Populate the group using the part size and count """
        TuXtremSplit().logger.debug(
            "Populating XtmGroup with %d parts of %d octets" % (count, size))

        from tuxtremsplit.application import Application
        for index in range(1, (count + 1)):

            # Initialize a new FileDescriptor for the future file
            new_file = FileDescriptor("%s.%03d.xtm" %
                                      (os.path.join(self.__destination.path,
                                       self.__current_source.name), index))

            # Define its size
            if index == 1:
                new_file.size = size + Application().settings.xtm_header.size
            else:
                new_file.size = size

            # Save it in the group
            if index == 1:
                self.__zero_zero_one = new_file
            else:
                self.append(new_file)

    def check_destination_free_space(self):
        """ Raise an NoEnoughSpaceError exception if no enough space """
        if not self.__current_source and not self.__group_files:
            raise ArgumentError("Group file and source are empty.")

        input_size = 0
        if self.__current_source:
            input_size = self.__current_source.size
        elif self.__group_files:
            for group_file in self.__group_files:
                input_size += group_file.size
        TuXtremSplit().logger.debug("Input size: %d octets" % input_size)

        if not self.__destination.has_enough_free_space(input_size):
            raise NoEnoughSpaceError("There no enough space at %s" %
                                     self.__destination.path)

    def file_with_index(self, index):
        """ Return the file with matching index """
        if index == 1:
            return self.main_file

        for file in self.__group_files:
            if file.name.endswith(".%03d.xtm" % index) or \
               file.name.endswith(".%03d.exe" % index):
                return file

    def last_file(self):
        """ Retrive and return the last file of the group """
        return self.file_with_index(self.size)

    def check_md5sums(self):
        """ Check that all parts are valid using stored MD5 sums """
        from tuxtremsplit.application import Application
        if not Application().arguments.md5:
            return True

        if not self.main_file.header.md5_enabled:
            raise Md5SumsNotEnabledInXtmHeaderError(
                "MD5 disabled in the XTM Header. Can't check files validity.")

        ActionWindow().checking_md5_sums(self.size, self.main_file.path)
        ActionWindow().render(self)

        EventsBus().current_action("checking MD5 sums", self.stop_md5_thread,
            self.start_md5_thread, skip_callback=self.skip_md5_thread)

        self.start_md5_thread()

    def start_md5_thread(self):
        self.__thread = XtmMd5Checker()
        # Callbacks
        self.__thread.file_with_index = self.file_with_index
        self.__thread.after_finished = self.after_md5_check_finished
        # Variables
        self.__thread.last_file = self.last_file()
        self.__thread.size = self.size
        self.__thread.index = self.__md5_sum_index
        self.__thread.start()
        TuXtremSplit().logger.debug("Before join_with_exception")
        self.__thread.join_with_exception()
        TuXtremSplit().logger.debug("After join_with_exception")

    def skip_md5_thread(self):
        self.__thread.stop(skip=True)

    def stop_md5_thread(self):
        self.__thread.stop()

    def after_md5_check_finished(self):
        EventsBus().action_finished()
        if self.__thread.success:
            TuXtremSplit().logger.debug("MD5 check finished with success")
        elif self.__thread.skipped:
            TuXtremSplit().logger.debug("MD5 check skipped")
        else:
            TuXtremSplit().logger.debug("MD5 check finished with failures")
            ActionWindow().show_buttons_after_md5_check_failed()

    def write_md5_sums(self):
        """ Write all MD5 sums at the end of the last file """
        md5_sums = []
        for file_index in range(1, self.size + 1):
            file = self.file_with_index(file_index)
            md5_sums.append(file.md5_sum())
        TuXtremSplit().logger.debug("MD5 sums: %s" % md5_sums)

        last_file = self.last_file()
        last_file.open_file(write=True, append=True)
        last_file.file.seek(0, os.SEEK_END)
        last_file.file.write(("".join(md5_sums)).upper())
        last_file.close_file()
