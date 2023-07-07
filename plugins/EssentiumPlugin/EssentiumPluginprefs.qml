import QtQuick 2.15
import QtQuick.Controls 2.1
import QtQuick.Layouts 1.1
import QtQuick.Window 2.1

import UM 1.5 as UM

UM.Dialog
{
    id: base
    property string installStatusText
    height: minimumHeight
    width: minimumWidth
    minimumWidth: 400 * screenScaleFactor
    minimumHeight: 180 * screenScaleFactor
    title: "Essentium Plugin Preferences"

    function checkBooleanVals(val) {
        if (val == "True") {
            return true
        } else if (val == undefined || val == "False" ) {
            return false
        } else {
            return val
        }
    }

    function getIPAddress(val) {
        if (val == undefined)
        {
            return "XXX.XXX.XXX.XXX"
        } else
        {
            return val
        }
    }


    Column  {
        anchors.fill: parent
        anchors.margins: margin
        anchors.top: parent.top
        anchors.left: parent.left
        height: parent.height
        width: parent.width
        GroupBox {
            title: "General Settings"
            width: Math.round(parent.width)
            height: 85*screenScaleFactor
            Row {
                id: buttonRow
                spacing: UM.Theme.getSize("default_margin").height
                width: Math.round(parent.width)
                anchors.bottom: parent.bottom

                Button
                {
                    id: openWebsiteButton
                    width: 150*screenScaleFactor
                    property int renderType: Text.NativeRendering
                    text: "Open Github - Essentium Plugin"
                    onClicked: manager.openPluginWebsite()
                } // end Button

                Button
                {
                    id: helpButton
                    width: 100*screenScaleFactor
                    property int renderType: Text.NativeRendering
                    text: "Help"
                    ToolTip.timeout: 1000
                    ToolTip.visible: hovered
                    ToolTip.text: "Open the pdf help document."
                    onClicked: manager.showHelp()
                } // end Button
            } // end Row
        } // end GroupBox
    } // end ColumnLayout
} // end UM.Dialog
