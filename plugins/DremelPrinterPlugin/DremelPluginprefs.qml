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
    title: "Dremel Plugin Preferences"

    function checkBooleanVals(val) {
        if(val == "True") {
            return true
        } else if(val == undefined || val == "False" ) {
            return false
        } else {
            return val
        }
    }

    function getIPAddress(val) {
        if(val == undefined)
        {
            return "XXX.XXX.XXX.XXX"
        }else
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
                id: checkBoxRow
                spacing: UM.Theme.getSize("default_margin").height
                width: Math.round(parent.width)
                anchors.top: parent.top
                CheckBox {
                    id: screenshotCB
                    height: UM.Theme.getSize("checkbox").height
                    width: Math.round(parent.width)
                    text: "Select Screenshot Manually"
                    checked: checkBooleanVals(UM.Preferences.getValue("DremelPrinterPlugin/select_screenshot"))
                    onClicked: manager.setSelectScreenshot(checked)
                    spacing: UM.Theme.getSize("default_margin").width
                    ToolTip.timeout: 5000
                    ToolTip.visible: hovered
                    ToolTip.text: "Check this box to allow you when saving a\ng3drem file to manually select a screenshot\nfrom an image stored on your hard drive"
                } //end CheckBox
            } // end Row
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
                    text: "Open plugin website"
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
                    ToolTip.text: "Open documentation"
                    onClicked: manager.showHelp()
                } // end Button
            } // end Row
        } // end GroupBox`

        GroupBox {
            width: Math.round(parent.width)
            height: 60*screenScaleFactor
            title: "Dremel 3D45 IP Address (for camera viewing only)"
            Row{
                spacing: UM.Theme.getSize("default_margin").width
                width: Math.round(parent.width)
                TextField
                {
                    id: ipAddress
                    focus: true
                    text: getIPAddress(UM.Preferences.getValue("DremelPrinterPlugin/ip_address"))
                    width: 150*screenScaleFactor
                    onAccepted: manager.SetIpAddress(text)
                    ToolTip.timeout: 1000
                    ToolTip.visible: hovered
                    ToolTip.text: "Enter the IP address of your Dremel Printer here in order to enable the camera view"
                    validator: RegularExpressionValidator
                    {
                        regularExpression:/^(([01]?[0-9]?[0-9]|2([0-4][0-9]|5[0-5]))\.){3}([01]?[0-9]?[0-9]|2([0-4][0-9]|5[0-5]))$/
                    }
                }
                Button
                {
                    Layout.alignment: Qt.AlignRight
                    //anchors.right: parent.right
                    id: setIPButton
                    width: 100*screenScaleFactor
                    property int renderType: Text.NativeRendering
                    text: "Set IP Address"
                    onClicked: manager.SetIpAddress(ipAddress.text)
                } // end Button
            } // end Row
        } // end GroupBox
    } // end ColumnLayout
} // end UM.Dialog
