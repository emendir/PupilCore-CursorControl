

# External ArilTag Clips
For the CursorControl system to be able to accurately detect the position of the monitor on image frames from the video stream of the PupilCore headset's World Camera, we create 3D-printed clips onto which we paste [AprilTags](https://roboticsknowledgebase.com/wiki/sensing/apriltags/) which we can mount on the corner's of the monitor as shown in the picture below. The CursorControl plugin detects the positions of the AprilTags, then works out the shape and position of the monitor's screen's outline on the World Camera's image. See [AprilTag Clip Construction](AprilTagClipConstruction.md) for a step-by-step guide on making the AprilTag clips.

IMAGE OF MONITOR WITH APRILTAG CLIPS

## AprilTag Screen-Calibration
For the CursorControl system to be able to work out the monitor's screen's outline given the positions of the external Aprilag clips, a calibration process is performed when the system starts up. This process involves displaying 4 AprilTags on the screen, so that the PupilCore headset's WorldCamera sees a monitor with 4 AprilTags physically printed onto clips mounted on the corners of the monitor and 4 AprilTags displayed by the monitors screen, in its corners. When the CursorControl plugin sees the 4 physical AprilTags on the clips and the 4 displayed AprilTags representing the corners of the screen, it measures and rembers the relative positions of the physical AprilTags and the corners of the screen, so that it can later (during normal runtime) work out the postion of the screen's corners using just the 4 physical AprilTags on the 3D-printed clips.

### Notes on Pupil CalibrationScreen
- The 2D-Pupil Calibration can yield greater accuracy than 3D Pupil-Calibration, but has its own downsides. [Read the details on PupilCore's website](https://docs.pupil-labs.com/core/best-practices/#choose-the-right-gaze-mapping-pipeline).


![](Pupil-Calibration-2D.png)