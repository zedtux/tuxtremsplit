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

class Action(object):
    """ Helper class to interpret action to execute """

    def __init__(self, controller):
        """ Constructor """
        self.__controller = controller

    def is_join(self):
        """
        Return True if the given controller source is a file with
        xtm extension otherwise return False
        """
        return ((self.__controller.source.is_file and \
                 (self.__controller.source.extension.is_xtm or
                  self.__controller.source.extension.is_exe)) or \
                self.__controller.source.is_directory) and \
                self.__controller.xtm_identificator.have_identified
