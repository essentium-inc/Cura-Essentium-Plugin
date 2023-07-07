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
from . import EssentiumZipFile
from UM.Message import Message
from UM.Logger import Logger
from PyQt6.QtWidgets import QFileDialog


# Detect the platform, and return a simple string.
def detect_platform():
    my_sys = platform.system()
    Logger.log("i", "Essentium Plugin   -  Detected  - OS Name: " + os.name)
    Logger.log("i", "Essentium Plugin   -  Detected  - Platform System: " + my_sys)
    Logger.log("i", "Essentium Plugin   -  Detected  - Platform Version: " + platform.release())

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


class InstallUtil:
    def __init__(self, cura, cura_catalog):
        self.cura_root = cura
        self.cura_plugin_root = os.path.join(cura, "plugins")
        self.cura_unzip_directory_path = cura   # os.path.join(cura, "unzip") # todo testing
        self.catalog = cura_catalog
        self.platform = detect_platform()

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
        zip_file = EssentiumZipFile.EssentiumZipFile(zip_file_path, self.cura_unzip_directory_path, self.catalog)

        if zip_file.validation_check(self.platform):
            zip_file.try_unzip_and_install(self.platform)
