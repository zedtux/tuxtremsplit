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

class AlreadyExistingFileError(Exception):
    pass


class ArgumentError(Exception):
    pass


class BelongsNotToTheGroupError(Exception):
    pass


class InvalidHeaderError(Exception):
    pass


class InvalidHeaderFieldSizeError(Exception):
    pass


class InvalidHeaderSizeError(Exception):
    pass


class InvalidSourceError(Exception):
    pass


class Md5SumsNotEnabledInXtmHeaderError(Exception):
    pass


class NoDescriptorError(Exception):
    pass


class NoEnoughSpaceError(Exception):
    pass


class NoSourceError(Exception):
    pass


class NotInitializedFileError(Exception):
    pass
