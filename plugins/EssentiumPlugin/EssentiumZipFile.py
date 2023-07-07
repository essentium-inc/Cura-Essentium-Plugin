import os  # for listdir
import os.path  # for isfile and join and path
import stat     # For setting file permissions correctly
import traceback
import zipfile  # For unzipping the printer files

from UM.Message import Message
from UM.Logger import Logger

from PyQt6.QtWidgets import (QWidget, QSlider, QLineEdit, QLabel, QDialog, QPushButton, QScrollArea, QApplication,
                             QHBoxLayout, QVBoxLayout, QMainWindow, QDialogButtonBox)
from PyQt6.QtCore import Qt, QSize

class EssentiumZipFile:
    def __init__(self, zip_file_path, unzip_dir_path, catalog):
        self.zip_path = zip_file_path
        self.unzip_dir_path = unzip_dir_path
        self.catalog = catalog

        if self.zip_path is None:
            self.zip_path = ""

        if self.unzip_dir_path is None:
            self.unzip_dir_path = ""

        self.duplicate_file_infos = []
        self.existing_file_paths = []

    def try_unzip_and_install(self, platform):
        try:
            Logger.log('i', "Installing: " + self.zip_path + "     to: " + self.unzip_dir_path)

            installed_paths = []

            # unzip and install
            with zipfile.ZipFile(self.zip_path, "r") as zip_ref:
                for info in zip_ref.infolist():
                    x = info.filename.lower()

                    if x == "version notes.txt":
                        # corner case, only file at top level, want to keep this in special place
                        Logger.log("w", "TODO handle the version notes file")
                        # todo pick somewhere for this, then read this data for an About page, to show details of
                        # the last installed resources
                        continue

                    # skip Mac files when using Windows or Linux
                    if platform == "Mac" and not x.startswith("__mac"):
                        continue

                    # skip Windows files when using Mac
                    if platform != "Mac" and x.startswith("__mac"):
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

                    # For some reason, looks like all resource files fall into one of the following 5 file types
                    if x.endswith(".fdm_material") or x.endswith(".cfg") or x.endswith(".def.json") or \
                       x.endswith(".stl") or x.endswith(".py"):
                        # used 'x' variable until now, to force lowercase string comparison, now use real thing

                        new_file_path = os.path.join(self.unzip_dir_path, info.filename)
                        Logger.log("i", "Extracting resource: " + new_file_path)
                        zip_ref.extract(info.filename, path=self.unzip_dir_path)

                        installed_paths.append(new_file_path)

                        permissions = os.stat(new_file_path).st_mode
                        os.chmod(new_file_path, permissions | stat.S_IEXEC)  # Make these files executable.
                    else:
                        Logger.log("w", "Found unexpected resource in zip file: " + info.filename)

            success_message = str(len(installed_paths)) + " resources installed\n\n"

            for p in installed_paths:
                success_message += p + "\n"

            success_dialog = CustomDialog("Successfully Imported Resources", success_message, False)
            success_dialog.exec()
            Logger.log('i', success_message)
            return True

        except Exception as e:
            Logger.log("e", repr(e))
            Logger.log("e", traceback.format_exc())

            message = Message(self.catalog.i18nc("@warning:status", 'Essentium Plugin - Error, failed to import ' +
                                                 'resources from: ' + self.zip_path + "     " + repr(e)))
            message.show()
            return False

    # Check that we are ready for install, prompt the user if necessary. Return False to fail validation.
    def validation_check(self, platform):
        try:
            if not os.path.exists(self.zip_path):
                Logger.log("i", "Failed validation.. Zip file does not exist: " + self.zip_path)
                return False

            self.duplicate_file_infos = []
            self.existing_file_paths = []

            # check for existing files
            with zipfile.ZipFile(self.zip_path, "r") as zip_ref:
                for info in zip_ref.infolist():
                    x = info.filename.lower()

                    if x == "version notes.txt":
                        continue

                    # skip Mac files when using Windows or Linux
                    if platform == "Mac" and not x.startswith("__mac"):
                        continue

                    # skip Windows files when using Mac
                    if platform != "Mac" and x.startswith("__mac"):
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

                    # For some reason, looks like all resource files fall into one of the following 5 file types
                    if x.endswith(".fdm_material") or x.endswith(".cfg") or x.endswith(".def.json") or \
                       x.endswith(".stl") or x.endswith(".py"):
                        # used 'x' variable until now, to force lowercase string comparison, now use real thing

                        new_file_path = os.path.join(self.unzip_dir_path, info.filename)

                        if os.path.exists(new_file_path):
                            Logger.log("i", "Found duplicate resource: " + new_file_path)
                            self.duplicate_file_infos.append(info.filename)
                            self.existing_file_paths.append(new_file_path)
                    else:
                        Logger.log("w", "Found unexpected resource in zip file: " + info.filename)

            # prompt user if existing files found
            if len(self.existing_file_paths) > 0:
                Logger.log("w", "Duplicate resources detected")

                duplicate_message = "Overwrite " + str(len(self.existing_file_paths)) + " existing resource files?\n\n"

                for p in self.existing_file_paths:
                    duplicate_message += p + "\n"

                dialog_duplicates = CustomDialog("Overwrite existing resources?", duplicate_message)
                if dialog_duplicates.exec():
                    Logger.log("i", "Passed validation, accepting duplicates. TODO something..")
                    return True
                else:
                    Logger.log("i", "Rejecting duplicates. TODO")
                    return False

            Logger.log('i', "Passed validation, no duplicate resources detected: " + self.zip_path)
            return True

        except Exception as e:
            Logger.log("e", repr(e))
            Logger.log("e", traceback.format_exc())

            message = Message(self.catalog.i18nc("@warning:status", 'Essentium Plugin - Error, failed to import ' +
                                                 'resources from: ' + self.zip_path + "     " + repr(e)))
            message.show()
            return False


# https://www.pythonguis.com/tutorials/pyqt-dialogs/
class CustomDialog(QDialog):
    def __init__(self, title, message, include_cancel_button=True):
        super().__init__()

        self.setWindowTitle(title)
        if include_cancel_button:
            self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        else:
            self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        # define scroll area, put message inside of that
        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)

        # message is a 'QLabel' widget, which is inside a scroll area widget
        scroll.setWidget(QLabel(message))

        # dialog has scrolling message area, then the buttons
        layout = QVBoxLayout()
        layout.addWidget(scroll)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
