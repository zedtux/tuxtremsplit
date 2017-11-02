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

from tuxtremsplit.core.xtmgroupidentificator import XtmGroupIdentificator
from tuxtremsplit.core.xtmheadervalidator import XtmHeaderValidator


class XtmIdentificator(object):
    """ Identify and collect from the given path all valid XTM files """

    def __init__(self, descriptor):
        """ Constructor """
        self.__valid_groups = []

        self._identify_and_collect_from(descriptor)

    def _identify_and_collect_from(self, descriptor):
        """ Browse given path or chech given file for valid XTM file(s) """
        if descriptor.is_file:
            self._identify_from(descriptor)
        else:
            for xtm_file in descriptor.first_xtm_files:
                self._identify_from(xtm_file)

    def _identify_from(self, descriptor):
        """ Check valid XTM file from given path """
        TuXtremSplit().logger.debug("Identifying XTM files from %s..." %
                                    descriptor.path)

        TuXtremSplit().logger.debug("Checking file %s" % descriptor.path)
        xtm_header = XtmHeaderValidator().for_given(descriptor)
        xtm_header.inspect()
        if xtm_header.is_valid():
            TuXtremSplit().logger.debug("%s has a valid XTM header" %
                                        descriptor.name)
            descriptor.header = xtm_header
        else:
            from tuxtremsplit.customexceptions import InvalidHeaderError
            raise InvalidHeaderError("%s header isn't valid." %
                                     descriptor.name)

        group_identificator = XtmGroupIdentificator()
        group_identificator.identify_from(descriptor)
        if not group_identificator.empty() and group_identificator.is_valid():
            TuXtremSplit().logger.debug("Adding new group of XTM files.")
            self.__valid_groups.append(group_identificator.group)

    def get_have_identified(self):
        return len(self.groups) > 0
    have_identified = property(get_have_identified)

    def get_groups(self):
        """ Return list of groups """
        return self.__valid_groups
    groups = property(get_groups)

    def set_groups_destination(self, destination_descriptor):
        for group in self.groups:
            group.to(destination_descriptor)
