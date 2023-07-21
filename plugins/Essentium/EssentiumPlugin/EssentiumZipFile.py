import os
import os.path
import shutil
import sys
import tempfile
import traceback
import zipfile
from pathlib import Path

from PyQt6.QtCore import  Qt
from PyQt6.QtWidgets import QApplication
from UM.Message import Message
from UM.Logger import Logger

from .CustomDialog import CustomDialog


class EssentiumZipFile:
    def __init__(self, zip_file_path, catalog, platform):
        self.zip_path = zip_file_path
        self.catalog = catalog
        self.platform = platform

    def try_install(self, install_root_path, validate, install):
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        try:
            self.install(install_root_path, validate, install)
        except Exception as e:
            Logger.log('e', repr(e))
            Logger.log("e", traceback.format_exc())
            # otherwise silent failure for now

        QApplication.restoreOverrideCursor()

    # Dual use validation and install function, can be used recursively to validate then install
    # reason for this design is to ensure only 1 loop over the zip file exists in code, used for
    # both validation and installation, and validation can be called without installing
    def install(self, install_root_path, validate=True, install=True):

        # recursion corner case
        if not validate and not install:
            Exception("Bad input, validate and/or install must be True")

        # recursion logic
        if validate and install:
            if self.install(install_root_path, True, False):  # if passes validation
                return self.install(install_root_path, False, True)  # install it
            else:
                # Failed validation, do not install, validation failure dialogs already handled
                # return False to represent the failed installation
                return False

        # From here, we are executing either validation or installation, exactly one of those two.
        try:
            if validate:
                if not os.path.exists(self.zip_path):
                    if self.zip_path is None:
                        self.zip_path = ""
                    no_file_dialog = CustomDialog("Import Validation Error", "Zip file does not exist: " +
                                                  self.zip_path, include_cancel_button=False)
                    QApplication.restoreOverrideCursor()
                    no_file_dialog.show()

                    Logger.log("i", "Failed validation.. Zip file does not exist: " + self.zip_path)
                    return False

            existing_file_paths = []
            new_file_paths = []
            installed_file_paths = []

            # partially shared piece - computing installation paths for validation & installation
            # each item is either a new resource, an existing resource, or a throw away that we ignore
            with zipfile.ZipFile(self.zip_path, "r") as zip_ref:
                with tempfile.TemporaryDirectory() as tempdir:
                    if install:
                        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
                        Logger.log('i', "Extracting zip to temp directory:  " + tempdir)
                        zip_ref.extractall(tempdir)
                        Logger.log('i', "Installing zip from temp directory to:   " + install_root_path)

                    for info in zip_ref.infolist():
                        x = info.filename.lower()  # easier string comparisons

                        if x == "version notes.txt":
                            continue

                        # skip Mac files when using Windows or Linux
                        if self.platform == "Mac" and not x.startswith("__macosx"):
                            continue

                        # skip Windows files when using Mac
                        if self.platform != "Mac" and x.startswith("__macosx"):
                            continue

                        # skip Work In Progress files, skips nested in a .wip directory as well as files ending in .wip
                        if ".wip" in x:
                            continue

                        # directory path, not a file
                        if x.endswith("\\") or x.endswith("/"):
                            continue

                        # skip
                        if x.endswith("ds_store"):
                            continue

                        # 5 approved resource file types
                        if x.endswith(".fdm_material") or x.endswith(".cfg") or x.endswith(".def.json") or \
                           x.endswith(".stl") or x.endswith(".py"):
                            # used 'x' variable until now, to force lowercase string comparison, now use real path
                            # hard coding Essentium release style - with resources parent folder

                            # format install path for resources - doesn't affect plugins
                            temp_file_name = info.filename.removeprefix("__MACOSX/")
                            temp_file_name = temp_file_name.removeprefix("resources/")

                            # for install path for plugins - doesn't affect resources
                            if temp_file_name.startswith("plugins"):
                                pieces = temp_file_name.split('/')
                                plugin_name = pieces[1]
                                # duplicate directory name on purpose
                                temp_file_name = temp_file_name.replace(plugin_name + "/",
                                                                        plugin_name + "/" + plugin_name + "/", 1)

                            new_file_path = os.path.join(install_root_path, temp_file_name)
                            new_file_path = new_file_path.replace('/', '\\')

                            # note - this new_file_path seems correct, but I could not get any unzip function
                            # to change the path while unzipping (so I can't use this directly now to install)

                            if validate:
                                # Need to warn user before overwriting existing files
                                if os.path.exists(new_file_path):
                                    Logger.log("i", "File already exists, duplicate resource: " + new_file_path)
                                    existing_file_paths.append(new_file_path)
                                else:
                                    Logger.log("i", "New resource, expected install location: " + new_file_path)
                                    new_file_paths.append(new_file_path)

                            if install:
                                # now have access to install paths, and temp directory paths of unzipped files
                                unzip_file_path = os.path.join(tempdir, info.filename)
                                Logger.log('i', 'Installing resource from: ' +
                                           unzip_file_path + "   to: " + new_file_path)

                                # todo directory creation can fail on windows if not ran as admin
                                # shows somewhat helpful error message, but could be better

                                # create directories if needed, 'meshes' is typically the case for this
                                new_file_parent_dir_path = os.path.dirname(os.path.abspath(new_file_path))
                                os.makedirs(new_file_parent_dir_path, exist_ok=True)

                                # create file by copying from temp directory
                                shutil.copy(unzip_file_path, new_file_path)
                                installed_file_paths.append(new_file_path)
                        else:
                            Logger.log("w", "Found unexpected resource in zip file, not installing: " + info.filename)
                            # Ignoring unapproved file types

            # Validation prompts
            if validate:
                QApplication.restoreOverrideCursor()

                # prompt user if existing files found
                n_existing = len(existing_file_paths)
                n_new = len(new_file_paths)
                if n_existing > 0 or n_new > 0:
                    message = str(n_new) + " New Resources\n" + str(n_existing) + " Duplicate Resources\n\n"

                    if n_existing > 0:
                        message += "Duplicate Resources - Overwrite " + str(n_existing) + " files?\n\n"

                        for p in existing_file_paths:
                            message += p + "\n"

                        message += "\n\n"

                    if n_new > 0:
                        message += "New Resources - Import " + str(n_new) + " files?\n\n"

                        for p in new_file_paths:
                            message += p + "\n"

                    Logger.log('i', message)
                    import_dialog = CustomDialog("Import Resources?", message)

                    if import_dialog.show():
                        Logger.log("i", "User accepted installation.")
                        Logger.log('i', "Passed validation: " + self.zip_path)
                        return True
                    else:
                        Logger.log("i", "User rejected installation.")
                        Logger.log('i', "Passed validation, but user canceled install: " + self.zip_path)
                        return False
                else:
                    Logger.log('w','Import Validation Error - zip file does not contain any approved resources')
                    empty_dialog = CustomDialog("Import Validation Error", "Zip file does not contain any approved "
                                                "resources. You cannot install from this zip.",
                                                include_cancel_button=False)
                    QApplication.restoreOverrideCursor()
                    empty_dialog.show()
                    return False

            # installation prompts
            if install:
                QApplication.restoreOverrideCursor()
                success_message = str(len(installed_file_paths)) + " resources installed - restarting Cura.\n\n"

                for p in installed_file_paths:
                    success_message += p + "\n"

                success_dialog = CustomDialog("Successfully Imported Resources", success_message, False)
                success_dialog.show()
                Logger.log('i', success_message)

                restart_program()  # force Cura to reload the app data we just installed
                return True  # does not execute, but makes PyCharm happy

        except Exception as e:
            Logger.log("e", repr(e))
            Logger.log("e", traceback.format_exc())

            QApplication.restoreOverrideCursor()
            message = Message(self.catalog.i18nc("@warning:status", 'Essentium Plugin - Error, failed to import ' +
                                                 'resources from: ' + self.zip_path + "     " + repr(e)))
            message.show()
            return False


def restart_program():
    """Restarts the current program.
    Note: this function does not return. Any cleanup action (like
    saving data) must be done before calling this function."""
    python = sys.executable
    os.execl(python, python, * sys.argv)
