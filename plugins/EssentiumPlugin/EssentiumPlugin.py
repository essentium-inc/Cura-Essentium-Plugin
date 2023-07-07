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

import os  # for listdir
import os.path  # for isfile and join and path
import re  # For escaping characters in the settings.
import json
import copy

from . import InstallUtil
from distutils.version import StrictVersion  # for upgrade installations

from UM.i18n import i18nCatalog
from UM.Extension import Extension
from UM.Message import Message
from UM.Resources import Resources
from UM.Logger import Logger
from UM.Mesh.MeshWriter import MeshWriter
from UM.PluginRegistry import PluginRegistry

from UM.Application import Application
from UM.Settings.InstanceContainer import InstanceContainer
from cura.Machines.ContainerTree import ContainerTree

from PyQt6.QtGui import QImageReader, QImage, QDesktopServices
from PyQt6.QtCore import QByteArray, QBuffer, QIODevice, QSize, pyqtSlot, QObject, QUrl, pyqtSlot

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
    version = "0.0.1"

    def __init__(self):
        Logger.log("i", "Initializing...")
        super().__init__(add_to_recent_files=False)
        self._application = Application.getInstance()

        if self.get_preference_value("curr_version") is None:
            self.set_preference_value("curr_version", "0.0.0")

        self.cura_resource_root_path = Resources.getStoragePath(Resources.Resources)

        self.this_plugin_path = \
            os.path.join(self.cura_resource_root_path, "plugins", "EssentiumPlugin", "EssentiumPlugin")

        self._preferences_window = None
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Import Resources"), self.show_install)
        # self.addMenuItem(catalog.i18nc("@item:inmenu", "About"), self.show_about)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Help"), self.show_help)

        # save the cura.cfg file
        storage_path_x: str = str(Resources.getStoragePath(Resources.Preferences,
                                                           self._application.getApplicationName() + ".cfg"))
        Logger.log("i", "Writing to " + storage_path_x)
        self._application.getPreferences().writeToFile(storage_path_x)

    def create_preferences_window(self):
        path_x = os.path.join(PluginRegistry.getInstance().getPluginPath(self.getPluginId()),
                              "EssentiumPluginprefs.qml")
        Logger.log("i", "Creating preferences UI " + path_x)
        self._preferences_window = self._application.createQmlComponent(path_x, {"manager": self})

    def hide_preferences(self):
        if self._preferences_window is not None:
            self._preferences_window.hide()

    @pyqtSlot()
    def open_plugin_website(self):
        url = QUrl('https://github.com/essentium-inc/Cura-Essentium-Plugin/releases', QUrl.ParsingMode.TolerantMode)
        if not QDesktopServices.openUrl(url):
            message = Message(catalog.i18nc("@info:warning", "Could not navigate to " +
                                            "https://github.com/essentium-inc/Cura-Essentium-Plugin/releases"))
            message.show()
        return

    # todo - Essentium help screen
    @pyqtSlot()
    def show_help(self):
        url = os.path.join(PluginRegistry.getInstance().getPluginPath(self.getPluginId()), "README.pdf")
        Logger.log("i", "Opening help document: " + url)
        try:
            if not QDesktopServices.openUrl(QUrl("file:///" + url, QUrl.ParsingMode.TolerantMode)):
                message = Message(catalog.i18nc("@info:warning", "Essentium Plugin could not open help document.\n Pl" +
                                                "ease download it from here: https://github.com/essentium-inc/Cura-Es" +
                                                "sentium-Plugin/blob/stable/README.pdf"))
                message.show()

        except:
            message = Message(catalog.i18nc("@info:warning", "Essentium Plugin could not open help document.\n " +
                                            "Please download it from here: https://github.com/essentium-inc/Cura-Ess" +
                                            "entium-Plugin/blob/stable/README.pdf"))
            message.show()

        return

    # @pyqtSlot()
    # def show_about(self):
    #    return  # todo

    @pyqtSlot()
    def show_install(self):
        installer = InstallUtil.InstallUtil(self.cura_resource_root_path, catalog)
        installer.install_from_user_selection()

    def versions_match(self):
        # get the currently installed plugin version number
        if self.get_preference_value("curr_version") is None:
            self.set_preference_value("curr_version", "0.0.0")

        installed_version = self._application.getPreferences().getValue("EssentiumPlugin/curr_version")

        if StrictVersion(installed_version) == StrictVersion(EssentiumPlugin.version):
            # if the version numbers match, then return true
            Logger.log("i", "Essentium Plugin versions match: " + installed_version + " matches " + self.version)
            return True
        else:
            Logger.log("i", "Essentium Plugin - The currently installed version: " + installed_version +
                       " does not match this version: " + self.version)
            return False

    #  Gets a value from Cura's preferences
    def get_preference_value(self, preference_name):
        return self._application.getPreferences().getValue("EssentiumPlugin/" + str(preference_name))

    # Sets a value to be stored in Cura's preferences file
    def set_preference_value(self, preference_name, preference_value):
        if preference_value is None:
            return False
        name = "EssentiumPlugin/" + str(preference_name)
        Logger.log("i", "Setting preference:  " + name + " to " + str(preference_value))

        if self.get_preference_value(preference_name) is None:
            Logger.log("i", "Adding preference " + name)
            self._application.getPreferences().addPreference(name, preference_value)

        self._application.getPreferences().setValue(name, preference_value)
        return self.get_preference_value(preference_name) == preference_value

    # Create a new container with container 2 as base and container 1 written over it.
    def _create_flattened_container_instance(self, instance_container1, instance_container2):
        flat_container = InstanceContainer(instance_container2.getName())

        # The metadata includes id, name and definition
        flat_container.setMetaData(copy.deepcopy(instance_container2.getMetaData()))

        if instance_container1.getDefinition():
            flat_container.setDefinition(instance_container1.getDefinition().getId())

        for key in instance_container2.getAllKeys():
            flat_container.setProperty(key, "value", instance_container2.getProperty(key, "value"))

        for key in instance_container1.getAllKeys():
            flat_container.setProperty(key, "value", instance_container1.getProperty(key, "value"))

        return flat_container

    ######################################################################
    #  Serialises a container stack to prepare it for writing at the end of the
    #   g-code.
    #
    #   The settings are serialised, and special characters (including newline)
    #   are escaped.
    #
    #   \param settings A container stack to serialise.
    #   \return A serialised string of the settings.
    ######################################################################
    def _serialise_settings(self, stack):
        container_registry = self._application.getContainerRegistry()

        setting_keyword = ";SETTING_"

        prefix = setting_keyword + str(EssentiumPlugin.version) + " "  # The prefix to put before each line.
        prefix_length = len(prefix)

        quality_type = stack.quality.getMetaDataEntry("quality_type")
        container_with_profile = stack.qualityChanges
        machine_definition_id_for_quality = ContainerTree.getInstance().machines[
            stack.definition.getId()].quality_definition
        if container_with_profile.getId() == "empty_quality_changes":
            # If the global quality changes is empty, create a new one
            quality_name = container_registry.uniqueName(stack.quality.getName())
            quality_id = container_registry.uniqueName(
                (stack.definition.getId() + "_" + quality_name).lower().replace(" ", "_"))
            container_with_profile = InstanceContainer(quality_id)
            container_with_profile.setName(quality_name)
            container_with_profile.setMetaDataEntry("type", "quality_changes")
            container_with_profile.setMetaDataEntry("quality_type", quality_type)
            if stack.getMetaDataEntry(
                    "position") is not None:  # For extruder stacks, quality changes should include an intent category
                container_with_profile.setMetaDataEntry("intent_category",
                                                        stack.intent.getMetaDataEntry("intent_category", "default"))
            container_with_profile.setDefinition(machine_definition_id_for_quality)
            container_with_profile.setMetaDataEntry("setting_version",
                                                    stack.quality.getMetaDataEntry("setting_version"))

        flat_global_container = self._create_flattened_container_instance(stack.userChanges, container_with_profile)
        # If the quality changes is not set, we need to set type manually
        if flat_global_container.getMetaDataEntry("type", None) is None:
            flat_global_container.setMetaDataEntry("type", "quality_changes")

        # Ensure that quality_type is set. (Can happen if we have empty quality changes).
        if flat_global_container.getMetaDataEntry("quality_type", None) is None:
            flat_global_container.setMetaDataEntry("quality_type",
                                                   stack.quality.getMetaDataEntry("quality_type", "normal"))

        # Get the machine definition ID for quality profiles
        flat_global_container.setMetaDataEntry("definition", machine_definition_id_for_quality)

        serialized = flat_global_container.serialize()
        data = {"global_quality": serialized}

        all_setting_keys = flat_global_container.getAllKeys()
        for extruder in stack.extruderList:
            extruder_quality = extruder.qualityChanges
            if extruder_quality.getId() == "empty_quality_changes":
                # Same story, if quality changes is empty, create a new one
                quality_name = container_registry.uniqueName(stack.quality.getName())
                quality_id = container_registry.uniqueName(
                    (stack.definition.getId() + "_" + quality_name).lower().replace(" ", "_"))
                extruder_quality = InstanceContainer(quality_id)
                extruder_quality.setName(quality_name)
                extruder_quality.setMetaDataEntry("type", "quality_changes")
                extruder_quality.setMetaDataEntry("quality_type", quality_type)
                extruder_quality.setDefinition(machine_definition_id_for_quality)
                extruder_quality.setMetaDataEntry("setting_version", stack.quality.getMetaDataEntry("setting_version"))

            flat_extruder_quality = self._create_flattened_container_instance(extruder.userChanges, extruder_quality)
            # If the quality changes is not set, we need to set type manually
            if flat_extruder_quality.getMetaDataEntry("type", None) is None:
                flat_extruder_quality.setMetaDataEntry("type", "quality_changes")

            # Ensure that extruder is set. (Can happen if we have empty quality changes).
            if flat_extruder_quality.getMetaDataEntry("position", None) is None:
                flat_extruder_quality.setMetaDataEntry("position", extruder.getMetaDataEntry("position"))

            # Ensure that quality_type is set. (Can happen if we have empty quality changes).
            if flat_extruder_quality.getMetaDataEntry("quality_type", None) is None:
                flat_extruder_quality.setMetaDataEntry("quality_type",
                                                       extruder.quality.getMetaDataEntry("quality_type", "normal"))

            # Change the default definition
            flat_extruder_quality.setMetaDataEntry("definition", machine_definition_id_for_quality)

            extruder_serialized = flat_extruder_quality.serialize()
            data.setdefault("extruder_quality", []).append(extruder_serialized)

            all_setting_keys.update(flat_extruder_quality.getAllKeys())

        # Check if there is any profiles
        if not all_setting_keys:
            Logger.log("i", "No custom settings found, not writing settings to g-code.")
            return ""

        json_string = json.dumps(data)

        # Escape characters that have a special meaning in g-code comments.
        pattern = re.compile("|".join(EssentiumPlugin.escape_characters.keys()))

        # Perform the replacement with a regular expression.
        escaped_string = pattern.sub(lambda m: EssentiumPlugin.escape_characters[re.escape(m.group(0))], json_string)

        # Introduce line breaks so that each comment is no longer than 80 characters. Prepend each line with the prefix.
        result = ""
        # Lines have 80 characters, so the payload of each line is 80 - prefix.
        for pos in range(0, len(escaped_string), 80 - prefix_length):
            result += prefix + escaped_string[pos: pos + 80 - prefix_length] + "\n"
        return result
