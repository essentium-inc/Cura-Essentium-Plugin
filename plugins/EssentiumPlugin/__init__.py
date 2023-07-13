# Copyright (c) 2015 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

from .EssentiumPlugin import EssentiumPlugin

from UM.i18n import i18nCatalog
catalog = i18nCatalog("cura")


def getMetaData():
    return {}  # todo?


def register(app):
    plugin = EssentiumPlugin()
    return {"extension": plugin}
