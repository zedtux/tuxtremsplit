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
import logging


class TuXtremSplit(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TuXtremSplit, cls).__new__(
                cls, *args, **kwargs)
            logging.basicConfig(
                format="%(levelname)s\t%(message)s [%(filename)s:%(lineno)s]")
            cls._instance.__logger = logging.getLogger("TuXtremSplit")
            cls._instance.__logger.setLevel(logging.DEBUG)
        return cls._instance

    def get_logger(self):
        return self.__logger
    logger = property(get_logger)
