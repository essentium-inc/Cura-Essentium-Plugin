# Copyright (c) 2015 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

from . import DremelGCodeWriter

from UM.i18n import i18nCatalog
catalog = i18nCatalog("cura")

def getMetaData():
    return {


        "mesh_writer": {
            "output": [{
                "extension": "g3drem",
                "description": catalog.i18nc("@item:inlistbox", "G3drem File"),
                "mime_type": "text/x-gcode",
                "mode": DremelGCodeWriter.DremelGCodeWriter.OutputMode.BinaryMode
            }]
        }
    }

def register(app):
    return { "mesh_writer": DremelGCodeWriter.DremelGCodeWriter() }