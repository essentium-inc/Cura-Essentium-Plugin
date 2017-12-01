# Cura-Dremel-3D20-Plugin
Dremel Ideabuilder 3D20 plugin for [Cura version 3.x](https://ultimaker.com/en/products/ultimaker-cura-software).  This plugin enables the user to export the proprietary .g3drem files using Cura.  This code is **heavily** based upon the [cura gcode writer plugin](https://github.com/Ultimaker/Cura/tree/master/plugins/GCodeWriter) and has been hacked together in an afternoon.  Although the software functions reasonably well for the author, the author will not guarantee that the software won't break your 3d printer, set it on fire, or do other really bad things.  The software is supplied without warranty and you are responsible if you use this software and bad things happen either to you, your 3D printer, or any of your other propery as a result of using this software, or the files that it creates.  Please remain near your 3D printer while using files generated by this software, and pay close attention to the 3D printer to verify that the machine is functioning properly. The software is provided as-is and any usage of this software or its output files is strictly at your own risk.

![The Cura GUI](/docs/GUI.PNG)
---
# Installation
To install, follow the instructions below:

0.  [Download and install Cura](https://ultimaker.com/en/products/ultimaker-cura-software) on your machine.  This plugin has been tested on Windows 10 Professional 64 bit edition, and MacOS 10.12 (Sierra), but this plugin should work equally well on linux or any other operating system that Cura supports.

1.  Download the plugin files by peforming one of the two actions:

    EITHER
    1. clone the repository onto your machine using the following command
    ```
    git clone https://github.com/timmehtimmeh/Cura-Dremel-3D20-Plugin.git
    ```

    OR

    2.  Click the download zip button on ![this page](https://github.com/timmehtimmeh/Cura-Dremel-3D20-Plugin) and extract the zip file to your computer
    ![Download Zip](/docs/downloadzip.png)

2.  Navigate to the folder where you downloaded or extracted the plugin

3.  Copy the plugins/DremelGCodeWriter folder into your `%CURA_DIR%/plugins` folder.  On MacOS this is located at `Ultimaker Cura.app/Contents/Resources/plugins/plugins/`  The easiest way on the mac to get to this folder is to right click on the Ultimaker Cura.app application and select the "show package contents" option.
![Copy the contents of DremelOutputDevice to the plugin directory of cura](/docs/plugindir.PNG)

4.   Copy the resources/definitions/Dremel3D20.def.json file into the `%CURA_DIR%/resources/definitions` folder.  On MacOS this is located at `Ultimaker Cura.app/Contents/Resources/resources/definitions/`  The easiest way on the mac to get to this folder is to right click on the Ultimaker Cura.app application and select the "show package contents" option
![Copy the contents of Dremel printer json file to the definitions directory of cura](/docs/dremelresource.PNG)

5.  Copy the resources/meshes/dremel_3D20_platform.stl to the `%CURA_DIR%/resources/meshes` folder.  On MacOS this is located at `Ultimaker Cura.app/Contents/Resources/resources/meshes/`  The easiest way on the mac to get to this folder is to right click on the Ultimaker Cura.app application and select the "show package contents" option
![Copy the contents of Dremel print bed file to the meshes directory of cura](/docs/meshesdir.png)

6.  Copy the resources/materials/dremel_pla.xml.fdm_material to the `%CURA_DIR%/resources/materials` folder.   On MacOS this is located at `Ultimaker Cura.app/Contents/Resources/resources/materials/`  The easiest way on the mac to get to this folder is to right click on the Ultimaker Cura.app application and select the "show package contents" option
![Copy the contents of Dremel PLA material to the materials directory of cura](/docs/material.png)    

7.  Congratulations - the plugin is now installed!
---
# Usage
Once the plugin has been installed you can use it by following the steps outlined below:
1. open cura
2. select the Dremel 3D20 as your printer (cura->preferences->printers->add)
![Select the Dremel 3D20](/docs/addprinter.png)

3. select Dremel PLA or any other PLA filament as your filament type
![Select the dremel pla](/docs/selectpla.png)

4. Set the slicing options that you want.

5. <a name="Step5"></a>(Optional, but recommended) Zoom in on the part until it fills the screen.  As the plugin saves out the .g3drem file it will grab a screenshot of the main cura window for use as the preview image that is displayed on the Ideabuilder screen. The area inside the red box shown in the image below will be used in the screenshot (the red box will not appear in the actual cura window when you use the plugin).  **Please Note:** The preview on the Dremel will be **much** better if you zoom in on the part that you're printing until the part fills the screenshot area.

For instance:
![Zoom in on the part](/docs/Zoom_For_Screenshot.PNG)

Will show this on the IdeaBuilder 3D20:
![Ideabuilder Screen](docs/Ideabuilder_screen.jpg)

**Nifty Feature:** The screenshot will work with the visualizer plugins, so feel free to try the "xray view" or "layer view" options if you like those visualizations better. 

6. Click "File->Save As", or "save to file", selecting .g3drem as the output file format.

![Save as .g3drem file](/docs/saveas.PNG)

7. Save this file to a SD card
8. Insert the SD card into your IdeaBuilder 3D20
9. Turn on the printer
10. Select the appropriate file to print.  
    ~~Currently the cura icon~~ ![cura icon](plugins/DremelGCodeWriter/cura80x60.bmp) ~~will be shown on the Dremel IdeaBuilder screen as the preview.~~  
    **New - [Version 0.2](https://github.com/timmehtimmeh/Cura-Dremel-3D20-Plugin/releases/tag/v0.2):** The plugin now grabs a screenshot of the main cura window as it saves out the file (see [Step 5 above](#Step5))
11. Click print
12. Enjoy - if you have any feature suggestions or encounter issues, feel free to raise them in the issues section above!
---
# Note
Please note the following:
* This plugin has only been tested on Cura 3.0.4 on Windows 10, and MacOS Sierra (MacOS 10.12) but there's no reason why it shouldn't work on linux as well.  If you are using another platform and encounter issues with the plugin, feel free to raise an issue with the "Issues" option above (in github)
* The Dremel 3D20 printer file json has not been optimized at all - if you have time and want to improve this file please do so and contribute the changes back.
  * While this plugin works in the basic print case, you may encounter problems with the print head crashing into your parts if you attempt to print multiple parts on the same print bed one-after-another instead of printing them all-at-once.
* The .g3drem file format is not fully understood yet - I've done a bit of reverse engineering on the file format, as described here: http://forums.reprap.org/read.php?263,785652 and have used the information I discovered to create this plugin, however there are still magic numbers in the dremel header that may or may not have an effect on the print.  See more information in the [Technical Details below](#Technical_Details).
---
# Wishlist
The following items would be great to add to this plugin - as I get time I'll work on them, but I'd welcome any collaboration
* ~~Replace the generic bitmap with a bitmap of the actual part being printed~~
    * Improve the picture of the part being printed as displayed on the IdeaBuilder screen
        * to auto-zoom and focus the screenshot on the part being printed, although I quite like giving the user the option of how to position the view, so this may not get implemented
        * ~~to not include the extra GUI on the right~~,
        * ~~to not include the extra GUI on the top and left~~

* Better understanding of the remaining unknown items in the Dremel .g3drem file format
* ~~Optimized Dremel3D20 json file with support for Dremel brand PLA~~
* Optimization of Dremel brand PLA settings
---
# <a name="Technical_Details"></a>Technical Details of the .g3drem File Format
The g3drem file format consists of a few sections.  The header is a mix of binary data and ASCII data, which is followed by an 80x60 pixel bitmap image written to the file, which is then followed by standard 3d printer gcode saved in ASCII format.

**An Example of the binary header looks like this:**

![File Header](/docs/FileHeader.JPG)

A description of the current understanding of this file format is below:

| Binary Data                                     | Description                                  |
|-------------------------------------------------|----------------------------------------------|
`67 33 64 72 65 6d 20 31 2e 30 20 20 20 20 20 20` | Ascii for 'g3drem 1.0      ' (see 1 below )  |
`3a 00 00 00 b0 38 00 00 b0 38 00 00 38 04 00 00` | Magic #s and Time(sec) (See 2 and 3 below )  |
`8f 04 00 00 00 00 00 00 01 00 00 00 19 00 03 00` | Filament(mm), Magic #s (See 4, 5, 6 and 7 )  |
`64 00 00 00 DC 00 00 00 01 ff [80x60 Bmp image]` | Magic #s and BMP image (See 8, 9, 10, 11  )  |
`[standard 3d printer gcode]`                     | Gcode in ASCII         (See 12 below      )  |

**The sections of the file are:**
1. `67 33 64 72 65 6d 20 31 2e 30 20 20 20 20 20 20` = ASCII text 'g3drem 1.0      '
2. `3a 00 00 00 b0 38 00 00 b0 38 00 00` = Some magic numbers that seem to be the same for every file 
3. `38 04 00 00` = four-byte little-endian integer representing the number of seconds that the print will take
4. `8f 04 00 00` = four-byte little-endian integer representing the estimated number of millimeters of filament that the print will use
5. `00 00 00 00 01 00 00 00` = Two four-byte magic numbers that seem to be the same for every file
6. `19 00` = A two-byte number that is different in some files that I've downloaded, but seem to remain the same on all files that I've generated with both the Dremel 3D and Simplify 3D software that I have, and doesn't have an obvious effect on the print.
7. `03 00` = A two-byte magic number that always seems to be the same
8. `64 00 00 00` = Two two-byte, or one four-byte number that is different in some files that I've downloaded, but seem to remain the same on all files that I've generated with both the Dremel 3D and Simplify 3D software that I have, and doesn't have an obvious effect on the print. **Note**, the last two bytes seem to be zeros in all files I've encountered.
9. `DC 00 00 00` = Two two-byte, or one four-byte number that is different in some files that I've downloaded, but seem to remain the same on all files that I've generated with both the Dremel 3D and Simplify 3D software that I have, and doesn't have an obvious effect on the print. **Note**, the last two bytes seem to be zeros in all files I've encountered.
10. `01 ff` = Another magic numbers that don't seem to change across files, and seems to indicate the end of the header
11. An 80x60 bitmap containing the image that the Dremel 3D20 will use to display on the screen (See the usage instructions [step 5](#Step5))
12. Standard 3d printer gcode (Marlin flavor seems to be working, but if you encounter issues please feel free to raise them)

**Interesting observations about the file format:**
1.  The maximum number of minutes that the dremel can read is 0xFFFFFF00, which comes out to 4660 hours and 20 minutes
2.  The maximum fiament length that the file can handle is hex 0xFFFFFFFF, or 4,294,967,295 millimeters. The [Dremel 3D software](https://dremel3d.at/pages/software) reports this value as (after some rounding): 4,294,967.5 meters
3.  The image size seems to be hardcoded inside the dremel firmware (at least for firmware 1.3.20160621).  Storing an image that is larger than 80x60 is allowable in the file, and the Windows-based ["Dremel 3D" software](https://dremel3d.at/pages/software) will read this file with a larger image with no problem.  The Dremel 3D sofware will read and show the correct part to build, but loading this file with the larger image into the actual Ideabuilder will result in the ideabuilder successfully showing the image, and allowing the user to select it, but will result in the IdeaBuilder rebooting when the user tries to print the file.
