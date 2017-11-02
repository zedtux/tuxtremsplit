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

import os
from tuxtremsplit.application.pathdescriptor import PathDescriptor
from tuxtremsplit.application.filedescriptor import FileDescriptor


class DescriptorFactory(object):
    """ Build and return a PathDescription or a FileDescriptor """

    def build_from(self, path):
        """ Build and Return generated object """
        if os.path.isfile(path):
            return FileDescriptor(path)
        else:
            return PathDescriptor(path)
