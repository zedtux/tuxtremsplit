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

import struct
from ..application.tools import Tools
from ..application.binarywriter import BinaryWriter


class XtmHeader(object):
    """ Xtremsplit Header class """

    def __init__(self):
        """ Constructor """
        self.__outfile = None
        self.__header = None
        self.application_name = None
        self.application_version = None
        self.creation_date = None
        self.original_filename = None
        self.md5_enabled = None
        self.number_of_parts = None
        self.original_filesize = None

    def read_from(self, descriptor):
        """ Parse XTM file header and fill in all Header fields """
        TuXtremSplit().logger.debug("Parsing header from %s" %
                                    descriptor.path)

        from tuxtremsplit.application import Application

        try:
            # Read header from FileDescriptor
            xtm_file = open(descriptor.path, "rb")
        except IOError:
            return self

        # For auto-extractable
        if descriptor.is_main_file and descriptor.extension.is_exe:
            # Jump over the SFX header
            xtm_file.seek(Application().settings.xtm_sfx.header_size)

        self.__header = xtm_file.read(Application().settings.xtm_header.size)
        xtm_file.close()

        TuXtremSplit().logger.debug("Header size is %d" % len(self.__header))
        # Check readed header size
        if not len(self.__header) == Application().settings.xtm_header.size:
            from tuxtremsplit.customexceptions import InvalidHeaderSizeError
            raise InvalidHeaderSizeError(
                "Header size should be %d but is %d" % (
                    Application().settings.xtm_header.size,
                    len(self.__header)))
        else:
            TuXtremSplit().logger.debug("Header size is valid.")

        try:
            self.parse_header()
        except UnicodeDecodeError:
            from tuxtremsplit.customexceptions import InvalidHeaderError
            raise InvalidHeaderError(
                "This file doesn't have a valid XTM header. "
                "Please try another file.")

        return self

    def parse_header(self):
        """ Validate readed header """
        from tuxtremsplit.application import Application
        xtm_header = Application().settings.xtm_header

        from tuxtremsplit.customexceptions import InvalidHeaderFieldSizeError

        # 1/ First octet is the size of the application name
        position = xtm_header.application_name_lenght.position
        size = xtm_header.application_name_lenght.size
        TuXtremSplit().logger.debug("Application name size from %d to %d" %
                                    (position, size))
        bytes_from_header = self.__header[position:position+size]
        application_name_size = struct.unpack("b", bytes_from_header)[0]
        TuXtremSplit().logger.debug("Application name size: %d" %
                                    application_name_size)
        if application_name_size > xtm_header.application_name.size:
            raise InvalidHeaderFieldSizeError("Application name size from the"
            " header (%d) is bigger than allowed size of %d." % (
                    application_name_size, xtm_header.application_name.size))
        if not application_name_size > 1:
            raise InvalidHeaderFieldSizeError(
                "Application name size is too small.")

        # 2/ Read the application name
        position = xtm_header.application_name.position
        size = application_name_size
        TuXtremSplit().logger.debug("Application name from %d to %d" %
                                    (position, size))
        bytes_from_header = self.__header[position:position+size]
        self.application_name = struct.unpack(
            "%ss" % size, bytes_from_header)[0].decode("ASCII")
        TuXtremSplit().logger.debug("Application name: %s" %
                                    self.application_name)

        # 3/ Read application version size
        position = xtm_header.application_version_lenght.position
        size = xtm_header.application_version_lenght.size
        TuXtremSplit().logger.debug("Application version size from %d to %d" %
                                    (position, size))
        bytes_from_header = self.__header[position:position+size]
        application_version_size = struct.unpack("b", bytes_from_header)[0]
        TuXtremSplit().logger.debug(
            "Application version size: %d" % application_version_size)
        if application_version_size > xtm_header.application_version.size:
            raise InvalidHeaderFieldSizeError(
                "Application version size from the header (%d) is bigger than"
                " allowed size of %d." % (application_version_size,
                                         xtm_header.application_version.size))

        # 4/ Read application version
        position = xtm_header.application_version.position
        size = application_version_size
        TuXtremSplit().logger.debug("Application version from %d to %d" %
                                    (position, size))
        bytes_from_header = self.__header[position:position+size]
        self.application_version = struct.unpack(
            "%ss" % size, bytes_from_header)[0].decode("ASCII")
        TuXtremSplit().logger.debug("Application version: %s" %
                                    self.application_version)

        # 5/ Read the creation date
        position = xtm_header.creation_date.position
        size = xtm_header.creation_date.size
        TuXtremSplit().logger.debug("Creation date from %d to %d" %
                                    (position, size))
        bytes_from_header = self.__header[position:position+size]
        self.creation_date = Tools().TDateTime2UnixTimestamp(
            struct.unpack("f", bytes_from_header)[0])
        TuXtremSplit().logger.debug("Creation date: %s" % self.creation_date)

        # 6/ Read the original filename size
        position = xtm_header.original_filename_lenght.position
        size = xtm_header.original_filename_lenght.size
        TuXtremSplit().logger.debug("Original filename size from %d to %d" %
                                    (position, size))
        bytes_from_header = self.__header[position:position+size]
        original_filename_size = struct.unpack("b", bytes_from_header)[0]
        TuXtremSplit().logger.debug("Original filename size: %d" %
                                    original_filename_size)
        if original_filename_size > xtm_header.original_filename.size:
            raise InvalidHeaderFieldSizeError(
                "Application version size from the header (%d) is bigger than"
                " allowed size of %d." % (original_filename_size,
                                          xtm_header.original_filename.size))

        # 7/ Read the original file name
        position = xtm_header.original_filename.position
        size = original_filename_size
        TuXtremSplit().logger.debug("Original filename from %d to %d" %
                                    (position, size))
        bytes_from_header = self.__header[position:position+size]
        self.original_filename = struct.unpack(
            "%ss" % size, bytes_from_header)[0].decode("utf-8")
        TuXtremSplit().logger.debug("Original filename: %s" %
                                    self.original_filename)

        # 8/ Read the HashMD5 flag
        position = xtm_header.md5.position
        size = xtm_header.md5.size
        TuXtremSplit().logger.debug("MD5 Enabled from %d to %d" %
                                    (position, size))
        bytes_from_header = self.__header[position:position+size]
        self.md5_enabled = struct.unpack("?", bytes_from_header)[0]
        TuXtremSplit().logger.debug("MD5 Enabled size: %r" % self.md5_enabled)

        # 9/ Read number of part
        position = xtm_header.number_of_parts.position
        size = xtm_header.number_of_parts.size
        TuXtremSplit().logger.debug("Number of parts from %d to %d" %
                                    (position, size))
        bytes_from_header = self.__header[position:position+size]
        self.number_of_parts = struct.unpack("i", bytes_from_header)[0]
        TuXtremSplit().logger.debug("Number of parts: %d" %
                                    self.number_of_parts)

        # 10/ Read the original filesize
        position = xtm_header.original_filesize.position
        size = xtm_header.original_filesize.size
        TuXtremSplit().logger.debug("Original filesize from %d to %d" %
                                    (position, size))
        bytes_from_header = self.__header[position:position+size]
        self.original_filesize = struct.unpack("II", bytes_from_header)[0]
        TuXtremSplit().logger.debug("Original filesize: %d" %
                                    self.original_filesize)

    def is_valid(self):
        """ Return True if XTM Header is valid otherwise return False """
        return  self.application_name and \
                self.application_version and \
                not self.creation_date is None and \
                self.original_filename and \
                not self.md5_enabled is None and \
                self.number_of_parts and \
                self.original_filesize

    def write_to(self, descriptor, number_of_parts):
        """
        Generate and return binary string of the Xtm header
        from given descriptor
        """
        binary_writer = BinaryWriter(descriptor.file)

        from tuxtremsplit.application import Application

        self.application_name = Application().settings.name
        self.application_version = Application().settings.short_version
        self.creation_date = 0.0
        self.original_filename = descriptor.name_without_xtm_identificator
        self.md5_enabled = Application().arguments.md5 is True
        self.number_of_parts = number_of_parts
        self.original_filesize = descriptor.size

        TuXtremSplit().logger.debug("Generated XTM Header:")
        self.inspect()

        binary_writer.move_to(0)

        # 1/ Write the size of the application name
        binary_writer.write_number(len(self.application_name), 1)

        # 2/ Write the application name
        binary_writer.write_string(self.application_name, 20)

        binary_writer.move_to(21)

        # 3/ Write the application version size
        binary_writer.write_number(len(self.application_version), 1)

        # 4/ Write the application version
        binary_writer.write_string(self.application_version, 4)

        # TODO: Write current date
        # binary_writer.move_to(starting_byte + 36)

        binary_writer.move_to(40)

        # 5/ Write original filename size
        binary_writer.write_number(len(self.original_filename), 1)

        # 6/ Write the original filename
        binary_writer.write_string(self.original_filename, 50)

        binary_writer.move_to(91)

        # 7/ Write the HashMD5 flag
        binary_writer.write_boolean(self.md5_enabled, 1)

        binary_writer.move_to(92)

        # 8/ Write number of part
        binary_writer.write_number(self.number_of_parts, 4)

        binary_writer.move_to(96)

        # 8/ Write the original filesize
        binary_writer.write_number(self.original_filesize, 8)

        TuXtremSplit().logger.debug("Header written successfully.")

    def inspect(self):
        TuXtremSplit().logger.debug("application_name: %s" %
                                    self.application_name)
        TuXtremSplit().logger.debug("application_version: %s" %
                                    self.application_version)
        TuXtremSplit().logger.debug("creation_date: %s" % self.creation_date)
        TuXtremSplit().logger.debug("original_filename: %s" %
                                    self.original_filename)
        TuXtremSplit().logger.debug("md5_enabled: %r" % self.md5_enabled)
        TuXtremSplit().logger.debug("number_of_parts: %d" %
                                    self.number_of_parts)
        TuXtremSplit().logger.debug("original_filesize: %d" %
                                    self.original_filesize)
        TuXtremSplit().logger.debug("Generated header is%s valid." %
                                    ("" if self.is_valid() else " not"))
