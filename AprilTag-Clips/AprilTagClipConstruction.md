# AprilTag Clips Construction guide
The AprilTag Clips are 3D-printed spring-loaded clips with [AprilTags](https://roboticsknowledgebase.com/wiki/sensing/apriltags/) pasted on them that get mounted on the corners of a computer monitor so that the CursorControl plugin can work out the position of the monitor's screen on the image frames of the PupilCore headset's World Camera.

## Materials and Tools
- access to a 3D Printer and a 2D (paper) Printer
- 4 coil springs of about 5mmm diameter and 15mm length (or similar)
- most likely a 3D-modelling program (such as [Blender](https://www.blender.org/)) to optimise the 3D-printed clips' shapes and sizes for your monitor
   
## Method
1. Print out the _AprilTag-Clips/3D-Prints/ClipsCompleteSet.stl_ file on a 3D printer.
  ![IMAGE OF 3D PRINTED PARTS](3D-Print-Clips.jpg)

2. Each clip is composed of two 3D-prints and a spring. Position the 3 components as shown in the second picture from the left below, making sure the spring is seated properly in the holes of both 3D-printed parts, then press the two 3D printed parts together around the hinge, so that they lock into place with a click. If your springs don't fit properly into your 3D printed parts, adjust the 3D-models of the clips in a 3D-modelling program (such as [Blender](https://www.blender.org/)).
![CLIP ASSEMBLY](ClipAssymbly.jpg)
3. Print out (on paper) the AprilTagsPrintout.pdf file. Cut out 4 different AprilTags from the piece of paper. They should have an edge length of 16mm-17mm. Paste the paper AprilTags on the 3D-Prints as shown below, observing which of the different AprilTags goes on which 3D-Printed clip, as well as the orientation of the AprilTags.
  ![IMAGE OF APRILTAGS PASTED ON CLIPS](AprilTagsPasted.jpg)

4. Mount the clips on the corners of your monitor, again making sure the correct clip goes on the correct corner. Check that following conditions which be met in order the the CursorControl to work properly are true:
   - The centres of the AprilTags MUST be located in the areas marked in blue relative to the extrapolated edges of the screen's outline (red).
   
   ![IMAGE OF APRILTAG CLIPS MOUNTED ON MONITOR SHOWING APRILTAG POSITION ZONES](AprilTagClipPositioning.png)
   
   Adjust the 3D-models of the clips in a 3D-modelling program (such as [Blender](https://www.blender.org/)) to fit properly on your monitor and reprint them.
