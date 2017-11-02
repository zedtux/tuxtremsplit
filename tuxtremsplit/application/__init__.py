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
import sys
from .settings import Settings
from tuxtremsplit.core.xtmpipe import XtmPipe
from tuxtremsplit.core.action import Action
from tuxtremsplit.core.controller import Controller
from tuxtremsplit.customexceptions import AlreadyExistingFileError, \
                                          ArgumentError, NoEnoughSpaceError, \
                                          InvalidHeaderError, NoSourceError, \
                                          InvalidHeaderFieldSizeError
from tuxtremsplit.gtk2.actionwindow import ActionWindow
from tuxtremsplit.gtk2.mainwindow import MainWindow
from tuxtremsplit.application.tools import Tools


class Application(object):
    """ TuXtremSplit Application """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Application, cls).__new__(
                cls, *args, **kwargs)
            cls._instance.__settings = Settings(
                cls._instance.path_to("config/settings.yml"))
            cls._instance.__arguments = None
        return cls._instance

    def get_settings(self):
        return self.__settings
    settings = property(get_settings)

    def get_arguments(self):
        return self.__arguments

    def set_arguments(self, arguments):
        self.__arguments = arguments
    arguments = property(get_arguments, set_arguments)

    def start(self, args, options):
        """
        Start TuXtremSplit with user arguments
        """
        # Store arguments in order to access them later
        self.arguments = options

        if args:
            standalone = self.arguments.__class__.__name__ != "OptparseFaker"
            ActionWindow().start(standalone=standalone)
        else:
            MainWindow().start()
            return

        try:
            # Controller detect/organize/gather files
            controller = Controller(args, options)

            # With or without MD5 check, at the end, we pass here anyway.
            ActionWindow().after_md5_check()

            # When Joining
            if Action(controller).is_join():
                TuXtremSplit().logger.debug("Current action is Join")
                # Allowed passing a directory with many groups of XTM files
                for group in controller.identified_groups:
                    ActionWindow().joining(
                        group.main_file.header.original_filename,
                        group.main_file.header.original_filesize,
                        group.size, group.main_file.path)
                    ActionWindow().render(group)
                    TuXtremSplit().logger.debug("Configuring XtmPipe "
                        "in order to merge %s to %s" %
                        (group.name, controller.destination.path))
                    # Join XTM files of the current group
                    XtmPipe().merge(group).to(controller.destination)

            # When Spliting
            else:
                TuXtremSplit().logger.debug("Current action is Split")
                # Inform the user of the current action
                ActionWindow().splitting(
                    controller.source.name, controller.source.size,
                    controller.destinations.size, controller.destination.path)
                ActionWindow().render(controller.destinations)
                # Split the source into many XTM files
                XtmPipe().split(controller.source).to(controller.destinations)

        # Errors
        except InvalidHeaderFieldSizeError:
            TuXtremSplit().logger.error("This file is not a valid XTM file. "
                                        "Please choose another one.")
            from tuxtremsplit.gtk2\
                             .gtkmessageboxhelper import GtkMessageBoxHelper
            GtkMessageBoxHelper(ActionWindow(), "This file is not a valid "
                                ".001.xtm or .001.exe. "
                                "Please choose another file",
                                quit_gtk_after_ok=True).show_dialog()
        except (AlreadyExistingFileError, ArgumentError, \
                IOError, NoEnoughSpaceError, InvalidHeaderError) as error:
            from tuxtremsplit.gtk2\
                             .gtkmessageboxhelper import GtkMessageBoxHelper
            try:
                TuXtremSplit().logger.error(unicode(error))
                GtkMessageBoxHelper(ActionWindow(), unicode(error),
                                    quit_gtk_after_ok=True).show_dialog()
            except:
                TuXtremSplit().logger.error(error)
                GtkMessageBoxHelper(ActionWindow(), error,
                                    quit_gtk_after_ok=True).show_dialog()
        # Infos
        except NoSourceError as error:
            try:
                TuXtremSplit().logger.info(unicode(error))
            except:
                TuXtremSplit().logger.info(error)

    def root_path(self):
        """ Return the application root path """
        if Tools().is_installed():
            return os.path.join(sys.prefix, "share/tuxtremsplit/")
        else:
            return ""

    def path_to(self, file_path):
        """ Return given path with application root path before """
        return os.path.join(self.root_path(), file_path)
