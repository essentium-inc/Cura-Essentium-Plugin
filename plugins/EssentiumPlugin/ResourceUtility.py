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

import os  # for listdir
import os.path  # for isfile and join and path
import platform
import shutil
import datetime
import traceback

from PyQt6.QtCore import QThreadPool, Qt
from PyQt6.QtWidgets import QFileDialog, QApplication
from UM.Message import Message
from UM.Logger import Logger

from .EssentiumZipFile import EssentiumZipFile
from .CustomDialog import CustomDialog
from .Worker import Worker


# Detect the platform, and return a simple string.
def detect_platform():
    my_sys = platform.system()
    Logger.log("i", "Detected  - OS Name:          " + os.name)
    Logger.log("i", "Detected  - Platform System:  " + my_sys)
    Logger.log("i", "Detected  - Platform Version: " + platform.release())

    # todo - for our purposes, we really only need special behavior on Mac, so just look for those cases
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
        self.cura_plugin_root = os.path.join(cura, "plugins")
        self.cura_unzip_directory_path = cura
        self.catalog = cura_catalog
        self.platform = detect_platform()
        self.output_zip_path = ""

    # Updates the permissions of a file or directory, and all subdirectories & files.
    @staticmethod
    def update_permissions_recursive(path, status):
        Logger.log('i', "Updating file permissions for: " + path)
        for root, dirs, files in os.walk(path, topdown=False):
            for dir_path in [os.path.join(root, d) for d in dirs]:
                permissions = os.stat(dir_path).st_mode
                os.chmod(dir_path, permissions | status)

            for file in [os.path.join(root, f) for f in files]:
                permissions = os.stat(file).st_mode
                os.chmod(file, permissions | status)  # Make file executable

    def install_from_user_selection(self):
        default_dir = get_downloads_dir_path()

        # returns a tuple, first item is path, second item is file type combobox selection
        file_path = QFileDialog.getOpenFileName(None, "Import Resources - Select Essentium Zip File", default_dir,
                                                "Zip-File (*.zip)")[0]

        if file_path is None or file_path == '':
            Logger.log("i", "User cancelled dialog.")
        else:
            Logger.log("i", "User selected file to install:  " + file_path)
            self.install_zip(file_path)

    # todo - depending on data in zip, bad things can happen with data being overwritten, including stl files
    # need to mitigate that somehow
    def install_zip(self, zip_file_path):
        if zip_file_path is None:
            zip_file_path = ""

        # check zip file exists
        if not os.path.exists(zip_file_path):
            error_message = 'Error while installing, failed to find source directory: ' + zip_file_path
            Logger.log('e', error_message)
            message = Message(self.catalog.i18nc("@warning:status", error_message))
            message.show()
            return

        Logger.log('i', "Installing resources from zip: " + zip_file_path + "   to: " + self.cura_unzip_directory_path)
        zip_file = EssentiumZipFile(zip_file_path, self.cura_unzip_directory_path, self.catalog)

        if zip_file.validation_check(self.platform):
            zip_file.try_unzip_and_install(self.platform)

    # worthy of a background worker, and a spinning cursor
    def export_zip_worker(self, zip_file_path):
        # do not try to do UI in this function, only background tasks
        # the logger will work as expected

        if zip_file_path is None:
            time_now = datetime.datetime.now().strftime("%m-%d-%y_%H-%M-%S")
            file_name = 'Cura_Resources_' + time_now
            zip_file_path = os.path.join(get_downloads_dir_path(), file_name)

        if os.path.exists(zip_file_path):
            Logger.log('i', 'File already exists, removing file:  ' + zip_file_path)
            os.remove(zip_file_path)

        # Set the zip path, and start on another thread
        self.output_zip_path = zip_file_path
        Logger.log("i", "Starting zip export... Zip File Path: " + self.output_zip_path)

        self.output_zip_path = shutil.make_archive(self.output_zip_path, 'zip', self.cura_root)

        if os.path.exists(self.output_zip_path):
            Logger.log('i', 'Created zip file: ' + self.output_zip_path)
        else:
            Logger.log('w', 'Failed to create zip file...')

    # Create a zip file with all resources, display a success or error dialog to confirm result
    def export_resources(self, zip_file_path=None):
        try:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

            # https://www.pythonguis.com/tutorials/multithreading-pyqt6-applications-qthreadpool/
            pool = QThreadPool()
            worker = Worker(self.export_zip_worker, zip_file_path)
            pool.start(worker)
            pool.waitForDone()

            # Dialog's must be on UI thread, not background worker
            if os.path.exists(self.output_zip_path):
                success_message = "Resources exported to:  " + self.output_zip_path
                success_dialog = CustomDialog("Success", success_message, False)
                QApplication.restoreOverrideCursor()
                success_dialog.show()
                Logger.log('i', success_message)
            else:
                fail_message = "Failed To Export Resources - file does not exist:  " + self.output_zip_path
                fail_dialog = CustomDialog("Failure", fail_message, False)
                QApplication.restoreOverrideCursor()
                fail_dialog.show()
                Logger.log('e', fail_message)

        except Exception as e:
            Logger.log('e', 'Exception while trying to create zip file...')
            fail_message = repr(e) + ' ' + traceback.format_exc() + "     Failed To Export Resources:  " + self.output_zip_path
            fail_dialog = CustomDialog("Failure - Exception Thrown", fail_message, False)
            QApplication.restoreOverrideCursor()
            fail_dialog.show()
            Logger.log('e', fail_message)
