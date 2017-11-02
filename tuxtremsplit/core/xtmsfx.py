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
from tuxtremsplit.application.binarywriter import BinaryWriter


class XtmSfx(object):
    """ Xtremsplit Footer Writer """

    def write_header_to(self, output_file):
        from tuxtremsplit.application import Application
        xtm_sfx = open(Application().path_to("data/xtm_sfx-1.2.dump"), "rb")
        output_file.write(xtm_sfx.read())
        xtm_sfx.close()

    def write_footer_to(self, output_file, part_size):
        """ Write SFX footer to the given opened file """
        from tuxtremsplit.application import Application
        xtm_sfx = Application().settings.xtm_sfx

        binary_writer = BinaryWriter(output_file)

        # Go to the Xtremsplit SFX name position
        binary_writer.move_to(xtm_sfx.application_name_lenght.position)

        # 1/ Write the size of the Xtremsplit SFX name
        binary_writer.write_number(len(xtm_sfx.application_name.value),
                                   xtm_sfx.application_name_lenght.size)

        # 2/ Write the Xtremsplit SFX name
        binary_writer.write_string(xtm_sfx.application_name.value,
                                   xtm_sfx.application_name.size)

        # Go to the version position
        binary_writer.move_to(xtm_sfx.application_version_lenght.position)

        # 3/ Write the size of the Xtremsplit SFX version
        binary_writer.write_number(len(xtm_sfx.application_version.value),
                                   xtm_sfx.application_version_lenght.size)

        # 4/ Write the Xtremsplit SFX version
        binary_writer.write_string(xtm_sfx.application_version.value,
                                   xtm_sfx.application_version.size)

        # Go to the part size position
        binary_writer.move_to(xtm_sfx.part_size.position)

        # 3/ Write the size of the Xtremsplit SFX version
        binary_writer.write_number(part_size, xtm_sfx.part_size.size)
