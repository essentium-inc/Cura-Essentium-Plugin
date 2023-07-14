####################################################################
# Essentium Plugin written by Alexander Yozzo,
# based on the Dremel Printer plugin written by Tim Schoenmackers,
# based on the GcodeWriter plugin written by Ultimaker.
#
# the Dremel Printer plugin source can be found here:
# https://github.com/metalman3797/Cura-Dremel-Printer-Plugin/tree/stable
#
# the GcodeWriter plugin source can be found here:
# https://github.com/Ultimaker/Cura/tree/master/plugins/GCodeWriter
#
# This plugin is released under the terms of the LGPLv3 or higher.
# The full text of the LGPLv3 License can be found here:
# https://github.com/essentium-inc/Cura-Essentium-Plugin/blob/master/LICENSE
####################################################################

import os
import os.path
import platform
import shutil
import datetime
import traceback
from pathlib import Path

from PyQt6.QtCore import QThreadPool, Qt
from PyQt6.QtWidgets import QFileDialog, QApplication
from UM.Message import Message
from UM.Logger import Logger

from .EssentiumZipFile import EssentiumZipFile
from .CustomDialog import CustomDialog
from .Worker import Worker
from .Zipper import Zipper


# Detect the platform, and return a simple string.
def detect_platform():
    my_sys = platform.system()
    Logger.log("i", "Detected  - OS Name:          " + os.name)
    Logger.log("i", "Detected  - Platform System:  " + my_sys)
    Logger.log("i", "Detected  - Platform Version: " + platform.release())

    # otherwise default to 'windows like' behavior
    if my_sys == "Darwin":
        # OS X
        return "Mac"
    else:
        return "Windows"  # just treat Linux like windows for now


# Get the user's Downloads directory path, safe for Windows & Mac
def get_downloads_dir_path():
    """Returns the default downloads path for linux or windows"""
    if os.name == 'nt':
        import winreg
        sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            location = winreg.QueryValueEx(key, downloads_guid)[0]
        return location
    else:
        return os.path.join(os.path.expanduser('~'), 'downloads')

    # Installs resources from a source directory, to a destination directory
    # this is meant to use the high level parent directories, and be called once


class ResourceUtility:
    def __init__(self, cura, cura_catalog):
        self.cura_root = cura
        self.catalog = cura_catalog
        self.platform = detect_platform()

    def import_from_user_selection(self):
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        default_dir = get_downloads_dir_path()

        # returns a tuple, first item is path, second item is file type combobox selection
        QApplication.restoreOverrideCursor()
        file_path = QFileDialog.getOpenFileName(None, "Import Resources - Select Essentium Zip File", default_dir,
                                                "Zip-File (*.zip)")[0]

        if file_path is None or file_path == '':
            Logger.log("i", "User cancelled dialog.")
        else:
            Logger.log("i", "User selected file to install:  " + file_path)
            self.import_resources(file_path)

    def import_resources(self, zip_file_path):
        if zip_file_path is None:
            zip_file_path = ""

        # check zip file exists
        if not os.path.exists(zip_file_path):
            error_message = 'Error while importing resources, failed to find source directory: ' + zip_file_path
            Logger.log('e', error_message)
            message = Message(self.catalog.i18nc("@warning:status", error_message))
            message.show()
            return

        zip_file = EssentiumZipFile(zip_file_path, self.catalog, self.platform)
        zip_file.try_install(self.cura_root, True, True)

    def export_resources_from_user_selection(self):
        time_now = datetime.datetime.now().strftime("%m-%d-%y_%H-%M-%S")
        file_name = 'Cura_Resources_' + time_now + ".zip"
        default_zip_file_path = os.path.join(get_downloads_dir_path(), file_name)

        # returns a tuple, first item is path, second item is file type combobox selection
        user_selected_file_path = QFileDialog.getSaveFileName(None, "Export Resources", default_zip_file_path,
                                                              "Zip-File (*.zip)")[0]

        # cancel button
        if user_selected_file_path is None or user_selected_file_path == "":
            return

        # this should never happen, due to using current time stamp
        if os.path.exists(user_selected_file_path):
            Logger.log('i', 'File already exists, removing file:  ' + user_selected_file_path)
            os.remove(user_selected_file_path)

        self.export_resources(user_selected_file_path)

    # creates a worker thread to export zip file, and spins the cursor
    def export_resources(self, zip_file_path=None):
        try:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

            # https://www.pythonguis.com/tutorials/multithreading-pyqt6-applications-qthreadpool/
            pool = QThreadPool()
            worker = Worker(self.export_resources_worker, zip_file_path)
            pool.start(worker)
            pool.waitForDone()

            # Dialog's must be on UI thread, not background worker
            if os.path.exists(zip_file_path):
                success_message = "Resources exported to:  " + zip_file_path
                success_dialog = CustomDialog("Success", success_message, False)
                QApplication.restoreOverrideCursor()
                success_dialog.show()
                Logger.log('i', success_message)
            else:
                fail_message = "Failed To Export Resources - file does not exist:  " + zip_file_path
                fail_dialog = CustomDialog("Failure", fail_message, False)
                QApplication.restoreOverrideCursor()
                fail_dialog.show()
                Logger.log('e', fail_message)

        except Exception as e:
            Logger.log('e', 'Exception while trying to export resources...')
            fail_message = repr(e) + ' ' + traceback.format_exc() + "     Failed To Export Resources:  " + zip_file_path
            fail_dialog = CustomDialog("Failure - Exception Thrown", fail_message, False)
            QApplication.restoreOverrideCursor()
            fail_dialog.show()
            Logger.log('e', fail_message)

    # exports resources, ignoring log files, cura.cfg, user folder
    def export_resources_worker(self, zip_file_path):
        # do not try to do UI in this function, only background tasks
        # the logger will work as expected

        Logger.log("i", "Starting zip export... Zip File Path: " + zip_file_path)

        # use zip utility to zip what we want, ignoring what we don't
        zipper = Zipper(self.cura_root, zip_file_path)
        zipper.zip_it(ignore_dir=[".svn", ".git", ".idea", "images", "machine_instances", "themes", "user"],
                      ignore_ext=[".zip", ".log"],
                      ignore_file_names=["packages.json", "plugins.json"],
                      ignore_file_name_contains=["cura.log"],
                      close_zip_file=True)

        if os.path.exists(zip_file_path):
            Logger.log('i', 'Created zip file: ' + zip_file_path)
        else:
            Logger.log('w', 'Failed to create zip file...')

    def export_snapshot_from_user_selection(self):
        time_now = datetime.datetime.now().strftime("%m-%d-%y_%H-%M-%S")
        file_name = 'Cura_Snapshot_' + time_now
        default_zip_file_path = os.path.join(get_downloads_dir_path(), file_name)

        # returns a tuple, first item is path, second item is file type combobox selection
        user_selected_file_path = QFileDialog.getSaveFileName(None, "Create Snapshot", default_zip_file_path,
                                                              "Zip-File (*.zip)")[0]

        # cancel button
        if user_selected_file_path is None or user_selected_file_path == "":
            return

        # this should never happen, due to using current time stamp
        if os.path.exists(user_selected_file_path):
            Logger.log('i', 'File already exists, removing file:  ' + user_selected_file_path)
            os.remove(user_selected_file_path)

        self.export_snapshot(user_selected_file_path)

    # creates a worker thread to export zip file, and spins the cursor
    def export_snapshot(self, zip_file_path=None):
        try:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

            # https://www.pythonguis.com/tutorials/multithreading-pyqt6-applications-qthreadpool/
            pool = QThreadPool()
            zip_file_path_obj = Path(zip_file_path)
            worker = Worker(self.export_snapshot_worker, str(zip_file_path_obj.with_suffix('')))  # removes extension
            pool.start(worker)
            pool.waitForDone()

            # Dialog's must be on UI thread, not background worker
            if os.path.exists(zip_file_path):
                success_message = "Snapshot created:  " + zip_file_path
                success_dialog = CustomDialog("Success", success_message, False)
                QApplication.restoreOverrideCursor()
                success_dialog.show()
                Logger.log('i', success_message)
            else:
                fail_message = "Failed to create Snapshot - file does not exist:  " + zip_file_path
                fail_dialog = CustomDialog("Failure", fail_message, False)
                QApplication.restoreOverrideCursor()
                fail_dialog.show()
                Logger.log('e', fail_message)

        except Exception as e:
            Logger.log('e', 'Exception while trying to create Snapshot...')
            fail_message = repr(
                e) + ' ' + traceback.format_exc() + "     Failed To create Snapshot:  " + zip_file_path
            fail_dialog = CustomDialog("Failure - Exception Thrown", fail_message, False)
            QApplication.restoreOverrideCursor()
            fail_dialog.show()
            Logger.log('e', fail_message)

    # exports snapshot, which is everything, log files included, user config included, etc
    def export_snapshot_worker(self, zip_file_path_no_ext):
        # do not try to do UI in this function, only background tasks
        # the logger will work as expected

        # Set the zip path, and start on another thread
        Logger.log("i", "Starting snapshot export... Zip File Path: " + zip_file_path_no_ext)

        x = shutil.make_archive(zip_file_path_no_ext, 'zip', self.cura_root)

        if os.path.exists(x):
            Logger.log('i', 'Created zip file: ' + x)
        else:
            Logger.log('w', 'Something went wrong, failed to create snapshot...')
