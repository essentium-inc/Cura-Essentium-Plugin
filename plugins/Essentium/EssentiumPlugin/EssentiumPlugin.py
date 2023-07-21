####################################################################
# Essentium Plugin written by Alexander Yozzo,
# based on the Dremel Printer plugin written by Tim Schoenmackers,
# based on the GcodeWriter plugin written by Ultimaker.
#
# the Essentium plugin source:
# https://github.com/essentium-inc/Cura-Essentium-Plugin
#
# the Dremel Printer plugin source:
# https://github.com/metalman3797/Cura-Dremel-Printer-Plugin/tree/stable
#
# the GcodeWriter plugin source:
# https://github.com/Ultimaker/Cura/tree/master/plugins/GCodeWriter
#
# This plugin is released under the terms of the LGPLv3 or higher.
# The full text of the LGPLv3 License can be found here:
# https://github.com/essentium-inc/Cura-Essentium-Plugin/blob/master/LICENSE
####################################################################

import os
import os.path

from PyQt6.QtCore import QObject, QUrl, pyqtSlot
from PyQt6.QtGui import QDesktopServices
from UM.Application import Application
from UM.Extension import Extension
from UM.Logger import Logger
from UM.Mesh.MeshWriter import MeshWriter
from UM.Message import Message
from UM.PluginRegistry import PluginRegistry
from UM.Resources import Resources
from UM.i18n import i18nCatalog

from .ResourceUtility import ResourceUtility

catalog = i18nCatalog("cura")


class EssentiumPlugin(QObject, MeshWriter, Extension):
    ######################################################################
    #  The version number of this plugin
    #  Please ensure that the version number is the same match in all
    #  three of the following Locations:
    #    1) below (this file)
    #    2) .\plugin.json
    #    3) ..\..\resources\package.json
    ######################################################################
    version = "0.0.2"

    def __init__(self):
        Logger.log("i", "Initializing...")
        super().__init__(add_to_recent_files=False)
        self._application = Application.getInstance()

        if self.get_preference_value("curr_version") is None:
            self.set_preference_value("curr_version", "0.0.0")

        self.cura_resource_root_path = Resources.getStoragePath(Resources.Resources)

        self.this_plugin_path = \
            os.path.join(self.cura_resource_root_path, "plugins", "Essentium", "Essentium")

        self._preferences_window = None
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Import Resources"), self.click_import_resources)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Export Resources"), self.click_export_resources)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Snapshot"), self.click_export_snapshot)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Help"), self.click_help)

        # save the cura.cfg file
        storage_path_x: str = str(Resources.getStoragePath(Resources.Preferences,
                                                           self._application.getApplicationName() + ".cfg"))
        Logger.log("i", "Writing to " + storage_path_x)
        self._application.getPreferences().writeToFile(storage_path_x)

    @pyqtSlot()
    def open_plugin_website(self):
        url = QUrl('https://github.com/essentium-inc/Cura-Essentium-Plugin/releases', QUrl.ParsingMode.TolerantMode)
        if not QDesktopServices.openUrl(url):
            message = Message(catalog.i18nc("@info:warning", "Could not navigate to " +
                                            "https://github.com/essentium-inc/Cura-Essentium-Plugin/releases"))
            message.show()
        return

    @pyqtSlot()
    def click_help(self):
        url = os.path.join(PluginRegistry.getInstance().getPluginPath(self.getPluginId()), "README.pdf")
        Logger.log("i", "Opening help document: " + url)
        try:
            if not QDesktopServices.openUrl(QUrl("file:///" + url, QUrl.ParsingMode.TolerantMode)):
                message = Message(catalog.i18nc("@info:warning", "Essentium Plugin could not open help document.\n Pl" +
                                                "ease download it from here: https://github.com/essentium-inc/Cura-Es" +
                                                "sentium-Plugin/blob/stable/README.pdf"))
                message.show()

        except Exception as e:
            Logger.log('w', 'Error during help button click' + repr(e))
            message = Message(catalog.i18nc("@info:warning", "Essentium Plugin could not open help document.\n " +
                                            "Please download it from here: https://github.com/essentium-inc/Cura-Ess" +
                                            "entium-Plugin/blob/stable/README.pdf"))
            message.show()

        return

    @pyqtSlot()
    def click_import_resources(self):
        resource_utility = ResourceUtility(self.cura_resource_root_path, catalog)
        resource_utility.import_from_user_selection()

    @pyqtSlot()
    def click_export_resources(self):
        resource_utility = ResourceUtility(self.cura_resource_root_path, catalog)
        resource_utility.export_resources_from_user_selection()

    @pyqtSlot()
    def click_export_snapshot(self):
        resource_utility = ResourceUtility(self.cura_resource_root_path, catalog)
        resource_utility.export_snapshot_from_user_selection()

    #  Gets a value from Cura's preferences
    def get_preference_value(self, preference_name):
        return self._application.getPreferences().getValue("Essentium/" + str(preference_name))

    # Sets a value to be stored in Cura's preferences file
    def set_preference_value(self, preference_name, preference_value):
        if preference_value is None:
            return False
        name = "Essentium/" + str(preference_name)
        Logger.log("i", "Setting preference:  " + name + " to " + str(preference_value))

        if self.get_preference_value(preference_name) is None:
            Logger.log("i", "Adding preference " + name)
            self._application.getPreferences().addPreference(name, preference_value)

        self._application.getPreferences().setValue(name, preference_value)
        return self.get_preference_value(preference_name) == preference_value
