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

import yaml
from .settingsgroup import SettingsGroup


class Settings(object):
    """ Settings object tree """

    def __init__(self, settings_path):
        """
        Settings constructor

        Create dynamic methods for each values from
        the settings.yml file.
        """
        self.__settings_groups = {}
        self.__current_group = None
        self.build_settings_groups_from(self.read(settings_path))

    def build_settings_groups_from(self, new_attributes):
        """ Build a hierarchie of SettingsGroup """
        self.read_attributes_for(None, None, new_attributes)

    def read_attributes_for(self, parent, group_name, attributes):
        """ Browse given attributes """

        if group_name:
            new_group = SettingsGroup()
            setattr(parent, group_name, new_group)
            current_group = new_group
        else:
            current_group = self

        for key, value in attributes.items():
            if isinstance(value, dict):
                self.read_attributes_for(current_group, key, value)
            else:
                setattr(current_group, key, value)

    def make_group(self, name):
        self.__current_group.group = SettingsGroup()
        return self.__current_group.group

    def open_settings_yml(self, settings_path):
        settings_yml = open(settings_path, "r")
        settings = settings_yml.read()
        settings_yml.close()
        return settings

    def read(self, settings_path):
        """ Load YAML file and return values """
        return yaml.load(self.open_settings_yml(settings_path))
