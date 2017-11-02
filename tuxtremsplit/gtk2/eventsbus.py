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


class EventsBus(object):
    """
    Centralize all events in the application in order to simplify
    communications between background core code and GUI
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(EventsBus, cls).__new__(
                cls, *args, **kwargs)
            TuXtremSplit().logger.debug("Initializing EventsBus...")
            cls._instance.action_name = None
            cls._instance.__action_stop_callback = None
            cls._instance.__action_start_callback = None
            cls._instance.__action_skip_callback = None
            cls._instance.__running = False
        return cls._instance

    def current_action(self, name, stop_callback, start_callback,
                       skip_callback=None):
        """ Store action name and callback method to stop action """
        self.action_name = name
        self.__action_stop_callback = stop_callback
        self.__action_start_callback = start_callback
        self.__action_skip_callback = skip_callback
        self.__running = True

    def get_is_processing(self):
        return not self.__action_stop_callback is None and self.__running
    is_processing = property(get_is_processing)

    def stop_action_if_processing(self):
        if self.is_processing:
            self.stop_action()

    def stop_action(self):
        TuXtremSplit().logger.debug("Stopping %s..." % self.action_name)
        self.__action_stop_callback()
        self.__running = False

    def start_action(self):
        TuXtremSplit().logger.debug("Starting %s..." % self.action_name)
        self.__action_start_callback()
        TuXtremSplit().logger.debug("Done")
        self.__running = True

    def skip_action(self):
        TuXtremSplit().logger.debug("Skipping %s..." % self.action_name)
        self.__action_skip_callback()
        TuXtremSplit().logger.debug("Done")
        self.__running = False

    def action_finished(self):
        self.__running = False
