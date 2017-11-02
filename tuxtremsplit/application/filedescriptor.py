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
import hashlib
from tuxtremsplit.application.fileextension import FileExtension
from tuxtremsplit.customexceptions import NotInitializedFileError
from tuxtremsplit.core.xtmheader import XtmHeader
from tuxtremsplit.core.xtmsfx import XtmSfx
from tuxtremsplit.application.tools import Tools
from tuxtremsplit.gtk2.actionwindow import ActionWindow


class FileDescriptor(object):
    """ Parse a file and provide some methods about it """

    def __init__(self, file_path):
        """ Constructor """
        TuXtremSplit().logger.debug("FileDescriptor#__init__(%s)" % file_path)
        self.__file_path = file_path
        self.__filename = None
        self.__base_path = None
        self.__filesize = 0
        self.__extension = None
        self.__header = None
        self.__id = None
        self.__file = None
        self.__file_is_open = False
        self.__md5_valid = None
        self.group = None
        self.__stop = False

        self.parse()

        TuXtremSplit().logger.debug(
            "New FileDescriptor for %s" % self.__file_path)

    def parse(self):
        """ Parse file from FileDescriptor#path """
        self.__filename = os.path.basename(self.__file_path)
        self.__extension = FileExtension(self.__filename)
        if self.__extension.found:
            self.__filename = self.__filename[0:
                ((len(self.__extension) + 1) * -1)]
            try:
                self.__id = int(re.search(r'\.(\d{3})(\.(xtm|exe))?$',
                                          self.__filename).group(1))
            except AttributeError:
                # The filename doesn't have a .XXX.extension
                pass
        self.__base_path = os.path.dirname(self.__file_path)
        if os.path.exists(self.__file_path):
            self.__filesize = os.path.getsize(self.__file_path)
            TuXtremSplit().logger.debug("Size of %s from disk is %d octets" %
                                        (self.name, self.__filesize))

    def open_file(self, filename=None, write=False, append=False):
        if self.__file_is_open:
            return self

        if write:
            options = "w"
            if append:
                options = "a"
        else:
            options = "r"
        options += "b"
        TuXtremSplit().logger.debug(
            "Opening %s with options %s" % (self.path, options))

        # Can override the default file name
        # (Usefull when output file and user want another filename)
        if filename:
            open_path = os.path.join(self.basepath, filename)
        else:
            open_path = self.path
        self.__file = open(open_path, options)
        self.__file_is_open = True
        return self

    def close_file(self):
        if not self.__file_is_open:
            return None

        TuXtremSplit().logger.debug("Closing %s" % self.path)
        self.__file.close()
        self.__file_is_open = False

    def move_after_xtm_sfx_header(self):
        """
        Do a seek on opened file to the defined XTM SFX header size + 1
        """
        if not self.__file:
            raise NotInitializedFileError(
                "You must call FileDescriptor#open_file() before "
                "FileDescriptor#move_after_xtm_sfx_header()")
        TuXtremSplit().logger.debug("Moving after XTM SFX Header...")
        from tuxtremsplit.application import Application
        self.__file.seek(Application().settings.xtm_sfx.header_size)

    def move_after_xtm_header(self):
        """ Do a seek on opened file to the defined XTM header size + 1 """
        if not self.__file:
            raise NotInitializedFileError(
                "You must call FileDescriptor#open_file() before "
                "FileDescriptor#move_after_xtm_header()")
        TuXtremSplit().logger.debug("Moving after XTM Header...")
        from tuxtremsplit.application import Application
        self.__file.seek(self.__file.tell() + \
                         Application().settings.xtm_header.size)

    def write_sfx_header(self):
        """ Copy Xtm SFX as first bytes of the file """
        if not self.is_open:
            raise NotInitializedFileError(
                "You must call FileDescriptor#open_file() before "
                "FileDescriptor#write_sfx()")

        XtmSfx().write_header_to(self.file)

    def write_xtm_header(self, xtm_group):
        """ Write the Xtm header to the current file """
        if not self.is_open:
            raise NotInitializedFileError(
                "You must call FileDescriptor#open_file() before "
                "FileDescriptor#write_xtm_header()")

        XtmHeader().write_to(self, xtm_group.size)

    def write_sfx_footer(self):
        """ Xtremsplit SFX need a footer at the end of the first xtm file """
        if not self.is_open:
            raise NotInitializedFileError(
                "You must call FileDescriptor#open_file() before "
                "FileDescriptor#write_sfx_footer()")

        XtmSfx().write_footer_to(self.file, self.size_without_sfx_and_header)

    def get_id(self):
        return self.__id
    id = property(get_id)

    def get_file(self):
        return self.__file
    file = property(get_file)

    def get_is_main_file(self):
        """ Return True if the filename contains .001. """
        return self.name.find(".001.") > -1 and \
               (self.extension.is_xtm or self.extension.is_exe)
    is_main_file = property(get_is_main_file)

    def get_path(self):
        """ Return the file path """
        return os.path.join(self.__base_path, self.name)
    path = property(get_path)

    def get_extension(self):
        """ Return the file extension object """
        return self.__extension
    extension = property(get_extension)

    def get_is_file(self):
        """ Return always True """
        return True
    is_file = property(get_is_file)

    def get_is_directory(self):
        """ Return always False """
        return False
    is_directory = property(get_is_directory)

    def get_name(self):
        """ Return described file name """
        if self.__extension.found:
            return "%s.%s" % (self.__filename, str(self.__extension))
        else:
            return self.__filename
    name = property(get_name)

    def get_basepath(self):
        """ Return described file base path """
        return self.__base_path
    basepath = property(get_basepath)

    def get_size(self):
        return self.__filesize

    def set_size(self, size):
        self.__filesize = size
        TuXtremSplit().logger.debug("%s file size is now %d octets" %
                                    (self.name, self.__filesize))
    size = property(get_size, set_size)

    def get_size_without_sfx(self):
        part_size = self.size
        if self.is_main_file and self.extension.is_exe:
            from tuxtremsplit.application import Application
            part_size -= Application().settings.xtm_sfx.header_size
            part_size -= Application().settings.xtm_sfx.footer_size
        return part_size
    size_without_sfx = property(get_size_without_sfx)

    def get_size_without_sfx_and_header(self):
        from tuxtremsplit.application import Application
        return self.size_without_sfx - Application().settings.xtm_header.size
    size_without_sfx_and_header = property(get_size_without_sfx_and_header)

    def get_header(self):
        return self.__header

    def set_header(self, header):
        self.__header = header
    header = property(get_header, set_header)

    def get_is_open(self):
        """
        Return True if FileDescriptor file is open otherwise return False
        """
        return self.__file_is_open
    is_open = property(get_is_open)

    def get_name_without_xtm_identificator(self):
        """ Return the filename without the .XXX.xtm from the end """
        if self.extension.is_xtm or self.extension.is_exe:
            return self.name[0:-8]
        else:
            return self.name
    name_without_xtm_identificator = property(
        get_name_without_xtm_identificator)

    def get_name_without_extension(self):
        """ Return the filename without the extension """
        return self.__filename
    name_without_extension = property(get_name_without_extension)

    def get_is_valid(self):
        return self.__md5_valid
    valid = property(get_is_valid)

    def extract_md5_sums_for(self, number_of_files):
        """ Read last bytes of the file to extract MD5 sums """
        self.open_file()

        # 32 is the size of a MD5 sum
        md5_sums_size = 32 * number_of_files
        self.file.seek(self.size - md5_sums_size)
        md5_sums_string = self.file.read(md5_sums_size)
        md5_sums = Tools().split_len(md5_sums_string, 32)

        self.close_file()

        return md5_sums

    def stop_md5_check(self):
        self.__stop = True

    def check_md5_sum(self, md5_sum, ignore=None):
        """ Check that the current file match the given md5 sum """
        TuXtremSplit().logger.debug("Calculating MD5 sum of %s" % self.name)
        self.open_file()

        md5 = hashlib.md5()
        chunk_size = 128 * md5.block_size
        readed_size = 0
        md5_sums_size = 0
        if ignore:
            md5_sums_size = 32 * ignore
        while not self.__stop:
            # ignore value contains a value only when working on last file.
            # The goal is to ignore latest bytes because it is MD5 sums.
            if ignore:
                if ((self.size - md5_sums_size) - readed_size) < chunk_size:
                    chunk_size = ((self.size - md5_sums_size) - readed_size)

            chunk = self.file.read(chunk_size)
            if not chunk:
                break
            md5.update(chunk)
            readed_size += len(chunk)

            # Global progressbar
            ActionWindow().update_progressbar((self.group.already_checked + \
                (readed_size * 1.0)) / self.group.size_of_all_files)
            # Current file progressbar
            ActionWindow().update_file_progressbar(self.id,
                (readed_size * 1.0) / self.size)

        self.close_file()
        self.group.already_checked += (readed_size * 1.0)

        current_md5_sum = md5.hexdigest().upper()
        if not md5_sum == current_md5_sum:
            ActionWindow().update_file_status(self.id, failed=True)
            self.__md5_valid = False
            TuXtremSplit().logger.warning(
                "%s MD5 sum (%s) mismatch from Xtm Header (%s)." %
                (self.name, current_md5_sum, md5_sum))
        else:
            self.__md5_valid = True
            ActionWindow().update_file_status(self.id, failed=False)

    def md5_sum(self):
        """ Return the MD5 sum of the current file """
        md5 = hashlib.md5()
        self.open_file()

        # If the file is a .001.exe file,
        # MD5 sum calculation must ignore SFX Header data
        from tuxtremsplit.application import Application
        if self.is_main_file and self.extension.is_exe:
            self.file.seek(Application().settings.xtm_sfx.header_size)

        chunk_size = 128 * md5.block_size
        readed_size = self.file.tell()
        for chunk in iter(lambda: self.file.read(chunk_size), ""):
            md5.update(chunk)
            # If the file is a .001.exe file,
            # MD5 sum calculation must ignore SFX footer data
            if self.is_main_file and self.extension.is_exe:
                readed_size += len(chunk)
                if (readed_size + chunk_size) > self.size:
                    chunk_size = ((self.size - readed_size) -
                                  Application().settings.xtm_sfx.footer_size)
                    md5.update(self.file.read(chunk_size))
                    break
        self.close_file()
        return md5.hexdigest()
