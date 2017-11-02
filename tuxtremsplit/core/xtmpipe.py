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

from tuxtremsplit.core.xtmgroup import XtmGroup
from tuxtremsplit.gtk2.eventsbus import EventsBus
from tuxtremsplit.core.xtmpipeworker import XtmPipeWorker


class XtmPipe(object):
    """
    XTM Pipe

    Main pipe splitting or joining a source to a destination.
    This is the core and the base of the application.
    """

    def __init__(self):
        """ Constructor """
        self.__current_source = None
        self.__worker = XtmPipeWorker()

    def merge(self, group):
        """ Used when the XtmPipe have to join XTM files """
        self.__current_source = group
        EventsBus().current_action("joining", self.__worker.stop,
                                   self.__worker.start)
        return self

    def split(self, source):
        """ Used when the XtmPipe have to split a file into XTM files """
        self.__current_source = source
        EventsBus().current_action("splitting", self.__worker.stop,
                                   self.__worker.start)
        return self

    def to(self, target):
        """
        Method used for both cases to define the output path of the XtmPipe
        and to engage the XtmPipe
        """
        # Inputs
        self.__worker.enqueue(self.__current_source).as_input()
        # Check destination free space
        if isinstance(target, XtmGroup):
            target.check_destination_free_space()
        else:
            self.__current_source.check_destination_free_space()
        # Outputs
        self.__worker.enqueue(target).as_output()
        # Let's go!
        self.__worker.start()
