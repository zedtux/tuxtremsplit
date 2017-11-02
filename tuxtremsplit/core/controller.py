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
from tuxtremsplit.core.xtmidentificator import XtmIdentificator
from tuxtremsplit.customexceptions import InvalidSourceError, \
                                          NoSourceError, \
                                          ArgumentError
from tuxtremsplit.application.descriptorfactory import DescriptorFactory
from tuxtremsplit.core.xtmgroup import XtmGroup
from tuxtremsplit.application.tools import Tools


class Controller(object):
    """
    THE Controller class

    Check, validate, and determine what should be done.
    """

    def __init__(self, args, options):
        """ Constructor """
        self.source = None
        self.__xtm_identificator = None
        self.__xtm_group = None

        # Check passed file paths if exist
        for arg in args:
            if not os.path.exists(arg):
                raise IOError(
                    "[Errno 2] No such file or directory: '%s'" % arg)

        # Source
        self.source = DescriptorFactory().build_from(
                os.path.realpath(args[0]))
        TuXtremSplit().logger.debug("Source: %s" % self.source.path)

        # Destination
        if len(args) == 1:
            self.destination = self._source_to_destination()
        else:
            self.destination = DescriptorFactory().build_from(
                os.path.realpath(args[1]))
        TuXtremSplit().logger.debug("Destination: %s" % self.destination.path)

        # The source is a file with the extension 'xtm'
        # or source is a directory with files
        if (self.source.is_file and (self.source.extension.is_xtm or
                                     self.source.extension.is_exe)) or \
            self.source.is_directory:
                if options.parts:
                    TuXtremSplit().logger.warn("parts option (-p) is useless "
                                               "when joining xtm files.")
                if options.size:
                    TuXtremSplit().logger.warn("size option (-s) is useless "
                                               "when joining xtm files.")
                if options.sfx:
                    TuXtremSplit().logger.warn("sfx option (-x) is useless "
                                               "when joining xtm files.")
                # Search all other XTM files
                self.__xtm_identificator = XtmIdentificator(self.source)
                if not self.__xtm_identificator.have_identified:
                    if self.source.is_file:
                        raise InvalidSourceError(
                            "%s is not a valid XTM file." % self.source.path)
                    else:
                        raise NoSourceError(
                            "No valid XTM file found in %s" %
                            self.source.path)
                self.__xtm_identificator.set_groups_destination(
                    self.destination)

        # When splitting a file check options and prepare XtmGroup
        elif self.source.is_file and not self.source.extension.is_xtm:
            if not options.parts and not options.size:
                raise ArgumentError("When splitting a file you must specify "
                                    "-p or -s option.")
            elif options.parts:
                self.__xtm_group = XtmGroup().create_from(self.source)\
                                             .to(self.destination)\
                                             .dividing_from_parts(
                                                options.parts)
            elif options.size:
                self.__xtm_group = XtmGroup().create_from(self.source)\
                                             .to(self.destination)\
                                             .dividing_from_size(
                                                Tools().human_size_to_number(
                                                    options.size))

            self.__xtm_group.create_sfx = options.sfx is True

    def source(self):
        """ Return the single source """
        return self.source

    def _source_to_destination(self):
        """ Return the path of the source """
        if os.path.isfile(self.source.path):
            return DescriptorFactory().build_from(
                os.path.dirname(self.source.path))
        else:
            return self.source

    def get_xtm_identificator(self):
        """ Return current instance of the instance variable """
        return self.__xtm_identificator
    xtm_identificator = property(get_xtm_identificator)

    def get_identified_groups(self):
        """ Return groups from XtmIdentificator """
        return self.__xtm_identificator.groups
    identified_groups = property(get_identified_groups)

    def get_destinations(self):
        """ Return an instance of XtmGroup of future files when splitting """
        return self.__xtm_group
    destinations = property(get_destinations)
