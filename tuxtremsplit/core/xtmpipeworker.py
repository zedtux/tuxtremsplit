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

from tuxtremsplit.application.filedescriptor import FileDescriptor
from tuxtremsplit.application.pathdescriptor import PathDescriptor
from tuxtremsplit.core.xtmgroup import XtmGroup
from tuxtremsplit.customexceptions import NoDescriptorError
from tuxtremsplit.gtk2.actionwindow import ActionWindow
from tuxtremsplit.application.exceptionthread import ExceptionThread


class XtmPipeWorkerThread(ExceptionThread):
    """
    XTM Pipe Worker
    Split or Join files from input to output.
    """

    def __init__(self):
        """ Constructor """
        TuXtremSplit().logger.debug("XtmPipeWorkerThread#__init__()")
        # Callbacks
        self.after_finished = None
        self.setup_is_one_to_many = None
        self.setup_is_many_to_one = None
        # Variables
        self.input = None
        self.current_input = None
        self.current_input_size = None
        self.output = None
        self.current_output = None
        self.current_output_size = None
        self.total_size = None
        self.buffer_size = None
        self.output_filename = None
        self.__stop = False
        ExceptionThread.__init__(self)

    def stop(self):
        self.__stop = True

    def _inputs_pop(self):
        """ Pop the first or the next input item """
        TuXtremSplit().logger.debug("Popuping input...")

        if self.setup_is_one_to_many():
            # Split a big file
            if not self.current_input:
                TuXtremSplit().logger.debug("Initializing input...")
                return self.input.open_file()
            else:
                return self.current_input

        elif self.setup_is_many_to_one():
            # Joining xtm files
            # First call
            if not self.current_input:
                # Return the .001.xtm or .001.exe file
                self.input.reset_file_position()
                input = self.input.main_file
            else:
                # Close the input file
                self.current_input.close_file()
                # Reset readed size for next file
                self.current_input_size = 0
                input = self.input.next_file()

            if input:
                # Initialize the input file in order to use it directly
                input.open_file()

                # First call
                if not self.current_input:
                    # Set the output filename from the XTM header
                    self.output_filename = input.header.original_filename
                    if input.is_main_file and input.extension.is_exe:
                        # Do not copy the Xtremsplit SFX header data
                        input.move_after_xtm_sfx_header()
                    # Do not copy the header in the output file
                    input.move_after_xtm_header()
                    self.current_input_size = input.file.tell()

                TuXtremSplit().logger.debug("Output filename is %s" %
                                            self.output_filename)
                return input

    def _outputs_pop(self):
        """ Pop the first or the next output item """
        TuXtremSplit().logger.debug("Popuping output...")
        if self.setup_is_one_to_many():
            # Split a big file
            # First call
            if not self.current_output:
                # Return the .001.xtm file
                self.output.reset_file_position()
                output = self.output.main_file
            else:
                # Write Xtremsplit SFX footer before to close the first xtm
                if self.output.create_sfx and \
                   self.current_output.is_main_file:
                    TuXtremSplit().logger.debug("Writting SFX footer...")
                    self.current_output.write_sfx_footer()

                # Close the output file
                self.current_output.close_file()
                self.current_output_size = 0
                output = self.output.next_file()

            if output:
                # Initialize the input file in order to use it directly
                output.open_file(write=True)

                # First call
                if not self.current_output:
                    if self.output.create_sfx:
                        TuXtremSplit().logger.debug("Writting SFX Header...")
                        output.write_sfx_header()
                    TuXtremSplit().logger.debug("Writting XTM Header...")
                    # Write the Xtm Header to the first file
                    output.write_xtm_header(self.output)
                    self.current_output_size = output.file.tell()

                return output

        elif self.setup_is_many_to_one():
            # Joining xtm files
            # First call
            if not self.current_output:
                # Check and create the output file
                # from the header of the very first XTM file
                return self.output.open_file(self.output_filename, write=True)
            else:
                return self.current_output

    def _buffer_size(self):
        """
        Calculate the buffer size to use
        depending the mode of the pipe and the current file.

        - Ignore MD5 chechsums at the end of the last file
            when joining xtm files.
        """
        from tuxtremsplit.application import Application

        # When splitting file
        if self.setup_is_one_to_many():
            # Use normal buffer size while the current output size
            # is not too high
            if (self.current_output_size + self.buffer_size) < \
                self.current_output.size_without_sfx:
                return self.buffer_size
            else:
                new_buffer_size = (self.current_output.size -
                                   self.current_output_size)
                if self.current_output.is_main_file and \
                   self.current_output.extension.is_exe:
                    new_buffer_size -= Application().settings\
                                                    .xtm_sfx.footer_size
                return new_buffer_size

        elif self.setup_is_many_to_one():

            # Only when joining an .001.exe file
            if self.current_input.is_main_file and \
               self.current_input.extension.is_exe:
                # Ignore the XTM SFX footer
                if (self.current_input_size + self.buffer_size) > \
                   (self.current_input.size - Application().settings.xtm_sfx\
                                                           .footer_size):
                    return (self.current_input.size - \
                            self.current_input_size - \
                            Application().settings.xtm_sfx.footer_size)

            # Only when current file is the last one from the group
            elif self.input.is_the_last_file(self.current_input):
                # Last file may contains the MD5 checksums of XTM parts
                if self.input.main_file.header.md5_enabled:
                    # Only when arriving near the end of the last file
                    if (self.current_input_size + self.buffer_size) > \
                        (self.current_input.size -
                         (32 * self.input.main_file.header.number_of_parts)):
                        return (self.current_input.size - (32 * \
                                self.input.main_file.header.number_of_parts) -
                                self.current_input_size)
        return self.buffer_size

    def _rotate(self):
        """ Rotate Inputs and Outputs """
        TuXtremSplit().logger.debug("Rotating inputs / outputs...")
        # Input file
        before_rotation = self.current_input
        self.current_input = self._inputs_pop()
        if self.current_input and self.current_input != before_rotation:
            TuXtremSplit().logger.info("In: %s" % self.current_input.name)

        # Output file
        before_rotation = self.current_output
        self.current_output = self._outputs_pop()
        if self.current_output and self.current_output != before_rotation:
            TuXtremSplit().logger.info("Out: %s" % self.current_output.name)

        return (self.current_input and self.current_output)

    def run_with_exception(self):
        data = None
        while not self.__stop:
            # Read a block of bytes from the current input
            if self.current_input:
                data = self.current_input.file.read(self._buffer_size())

            # End of file from current input
            if not data:
                # No more input or output file
                if not self._rotate():
                    TuXtremSplit().logger.info("Finished")
                    # End of worker
                    break
                else:
                    TuXtremSplit().logger.debug("Input starting point %d" %
                        self.current_input.file.tell())

            if data:
                # Write block of bytes from the current input
                # to the current output
                self.current_output.file.write(data)

                # Update sizes
                self.current_input_size += len(data)
                self.current_output_size += len(data)
                self.total_size += len(data)

                # Global progressbar
                ActionWindow().update_progressbar(
                    (self.total_size * 1.0) / self.action_size)
                # Current file progressbar
                ActionWindow().update_file_progressbar(
                    self.group_file_id(),
                    self.group_file_percentage())

                if (self.setup_is_one_to_many() and \
                    self.current_output_size % 5000 == 0) or \
                   (self.setup_is_many_to_one() and \
                    self.current_input_size % 5000 == 0):
                    TuXtremSplit().logger.debug(
                        "Readed size: Current: %d | Total: %d" %
                        (self.current_input_size, self.total_size))

        self.after_finished()

    def group_file_id(self):
        """
        A group file is a .XXX.xtm file when joining or splitting.
        This method return the id of the current group file
        """
        # When splitting file
        if self.setup_is_one_to_many():
            return self.current_output.id
        # When joining files
        elif self.setup_is_many_to_one():
            return self.current_input.id

    def group_file_percentage(self):
        """
        A group file is a .XXX.xtm file when joining or splitting.
        This method return the pourcentage of processed group file size
        """
        # When splitting file
        if self.setup_is_one_to_many():
            current_size = self.current_output_size
            final_size = self.current_output.size
        # When joining files
        elif self.setup_is_many_to_one():
            current_size = self.current_input_size
            final_size = self.current_input.size
        return ((current_size * 1.0) / final_size)


class XtmPipeWorker(object):

    def __init__(self):
        TuXtremSplit().logger.debug("XtmPipeWorker#__init__()")
        self.__enqueued_descriptor = None
        self.__stop_worker = False
        self.__action_size = None
        self.__input = None
        self.__current_input = None
        self.__current_input_size = 0
        self.__output = None
        self.__current_output = None
        self.__current_output_size = 0
        self.__total_size = 0
        self.__buffer_size = 2048
        self.__output_filename = None

    def enqueue(self, descriptor):
        """ Should receive a FileDescriptor, PathDescriptor or XtmGroup """
        self.__enqueued_descriptor = descriptor
        return self

    def as_input(self):
        """ Place prepared descriptor as input """
        self._as(input=True)

    def as_output(self):
        """ Place prepared descriptor as output """
        self._as(input=False)

    def _as(self, input):
        if not self.__enqueued_descriptor:
            raise NoDescriptorError(
                "No descriptor ready to be placed as output.")

        TuXtremSplit().logger.debug(
            "Enqueuing %s as %s" %
            (self.__enqueued_descriptor.name, "input" if input else "output"))
        if input:
            self.__input = self.__enqueued_descriptor
        else:
            self.__output = self.__enqueued_descriptor
        self._reset_enqueued_descriptor()

    def _reset_enqueued_descriptor(self):
        self.__enqueued_descriptor = None

    def _setup_is_one_to_many(self):
        """ Return True if input is an instance of class FileDescriptor """
        return isinstance(self.__input, FileDescriptor) or \
               isinstance(self.__input, PathDescriptor)

    def _setup_is_many_to_one(self):
        """ Return True if input is an instance of class XtmGroup """
        return isinstance(self.__input, XtmGroup)

    def stop(self):
        """ Kill current action """
        self.__stop_worker = True
        self.__thread.stop()

    def start(self):
        """ Execute the action """
        if not self.__action_size:
            # When splitting: Size of input file
            if self._setup_is_one_to_many():
                self.__action_size = self.__input.size
            # When joining: Size of output file
            elif self._setup_is_many_to_one():
                self.__action_size = self.__input.main_file.header\
                                                           .original_filesize

        self.__thread = XtmPipeWorkerThread()
        self.configure_thread()
        self.__thread.start()
        self.__thread.join_with_exception()

    def configure_thread(self):
        # Callbacks
        self.__thread.after_finished = self.after_finished
        self.__thread.setup_is_one_to_many = self._setup_is_one_to_many
        self.__thread.setup_is_many_to_one = self._setup_is_many_to_one
        # Variables
        self.__thread.action_size = self.__action_size
        self.__thread.input = self.__input
        self.__thread.current_input = self.__current_input
        self.__thread.current_input_size = self.__current_input_size
        self.__thread.output = self.__output
        self.__thread.current_output = self.__current_output
        self.__thread.current_output_size = self.__current_output_size
        self.__thread.total_size = self.__total_size
        self.__thread.buffer_size = self.__buffer_size
        self.__thread.output_filename = self.__output_filename

    def inspect(self):
        """ Output when debug is enabled some details about the Pipe """
        if self._setup_is_one_to_many():
            TuXtremSplit().logger.debug("1 input and %d outputs" %
                                        self.__output.size)
        elif self._setup_is_many_to_one():
            TuXtremSplit().logger.debug("%s inputs and 1 output" %
                                        self.__input.size)


    #-------------------------------------------------------------------------
    # Worker callback methods
    #-------------------------------------------------------------------------
    def after_finished(self):
        """ Fired method after treatment done """
        if self.__stop_worker:
            ActionWindow().on_action_failed()
        else:
            from tuxtremsplit.application import Application
            if self._setup_is_one_to_many() and Application().arguments.md5:
                self.__output.write_md5_sums()

            ActionWindow().on_action_success()
