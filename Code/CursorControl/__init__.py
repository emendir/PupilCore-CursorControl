from methods import denormalize
from plugin import Plugin

import glfw
from pyglui import ui
from pyglui.cygl.utils import RGBA, draw_polyline
import OpenGL.GL as gl

from pupil_apriltags import Detector
import cv2

from math import sqrt, atan, pi, cos, sin
import time

from CursorControl.Line import *
from CursorControl import mouse

from CursorControl.CalibrationScreen import CalibrationScreen
from CursorControl import MouseClicks
# from threading import Thread

print("Running MonitorRecognition")

# Setting for the stabilisation (smoothening) of the Cursor Position over time.
# At the technical level, determines how many of the most recent calculated
# Cursor Position values should be averaged to set the actual position of the
# Cursor on the screen.
cursor_stability = 5    # CALIBRATE: higher values: higher smoothness, higher latency

# working variables for CursorStability
# list of most recent calculated Cursor Positions
cursor_positions = [(0, 0)] * cursor_stability
cur_pos_index = 0  # index of most recent value in the above list


class CursorControl(Plugin):
    order = 0.81  # order must be greater than 0.8, which is the execution order of the WinkDetection plugin
    # whether or not we have already completed the Screen-Calibration
    screen_calibrated = False
    calibration_screen = None   # CalibrationScreen object
    # counts how many cycles the calibration screen has so far been shown for
    calibration_time_counter = 0
    # the size of each AprilTag pixel on the CalibrationScreen
    calib_marker_pixel_size = 0
    gaze_location = None

    def __init__(self, g_pool):
        super().__init__(g_pool)

        # AprilTag detector for AprilTag clips
        self.at_detector = Detector(families="tag16h5")
        # AprilTag detector for CalibrationScreen
        self.calib_detector = Detector(families="tag36h11")

        self.monitor = glfw.get_primary_monitor()
        self.video_mode = glfw.get_video_mode(self.monitor)
        self.screen_resolution = self.video_mode.size   # size of the screen in pixels
        # MouseClicks.Start()

    def gl_display(self):
        """This function gets called periodically during runtime.
        The first time it runs, the content of this function shows
        CalibrationScreen (for Screen-Calibration, not Pupil-Calibration)
        (assuming that the PupilCore Headset is connected).
        When the needed Screen-Calibration data has been collected,
        this function calculates the postion and orientation of the 
        Monitor-Screen on the World-Camera image/frame, and maps the user's
        Eye-Gaze position onto the Monitor-Screen and moves the computer's
        Cursor to that position, the effect for the user being that the Cursor
        always automatically moves to where they look at.
        """
        if self.g_pool.capture._recent_frame:   # if we have a World-Camera frame
            world_cam_img = self.g_pool.capture._recent_frame.img  # WordCamera frame/image

            # if we haven't already done the screen calibration
            if not self.screen_calibrated and self.calibration_time_counter < 10000:
                if not self.calibration_screen:  # if we aren't already calibrating
                    # Show the CalibrationScreen
                    self.calibration_screen = CalibrationScreen()
                    self.calib_marker_pixel_size = self.calibration_screen.pixel_size
                    self.calibration_screen.Show()
                    print("MonitorRecognition: set up calibration screen")
                    self.calibration_screen.Paint()
                    self.calibration_screen.Paint()
                self.calibration_time_counter += 1

                # Reading the postions of the april-tags used for screen calibration
                # CalibrationScreen AprilTags:
                screen_tags = self.calib_detector.detect(cv2.cvtColor(world_cam_img, cv2.COLOR_BGR2GRAY), estimate_tag_pose=False,
                                                         camera_params=None,)
                # External physical AprilTag-clips:
                ext_tags = self.at_detector.detect(cv2.cvtColor(world_cam_img, cv2.COLOR_BGR2GRAY), estimate_tag_pose=False,
                                                   camera_params=None, tag_size=0.013)
                # The CalibrationScreen AprilTags we're looking for:
                scr_tag_0 = None
                scr_tag_1 = None
                scr_tag_2 = None
                scr_tag_3 = None
                # The external physical AprilTags we're looking for:
                ext_tag_0 = None
                ext_tag_1 = None
                ext_tag_2 = None
                ext_tag_3 = None

                for tag in screen_tags:
                    if tag.tag_id == 0:
                        scr_tag_0 = tag
                    elif tag.tag_id == 1:
                        scr_tag_1 = tag
                    elif tag.tag_id == 2:
                        scr_tag_2 = tag
                    elif tag.tag_id == 3:
                        scr_tag_3 = tag

                for tag in ext_tags:
                    if tag.hamming == 0:    # filters out false detections
                        if tag.tag_id == 6:
                            ext_tag_0 = tag
                        elif tag.tag_id == 4:
                            ext_tag_1 = tag
                        elif tag.tag_id == 21:
                            ext_tag_2 = tag
                        elif tag.tag_id == 25:
                            ext_tag_3 = tag
                # If all april-tags are visible, collect calibration data:
                if scr_tag_0 and scr_tag_1 and scr_tag_2 and scr_tag_3 \
                        and ext_tag_0 and ext_tag_1 and ext_tag_2 and ext_tag_3:

                    # Calculating the constants (Screen Calibration Data) necessary
                    # for calculating the positions of the screen corners
                    # from the april-tag positions during runtime:
                    # (Screen Calibration Data):

                    # the positions of the outermost corner of each AprilTag
                    # on the WorldCamera image/frame:
                    scr_0 = scr_tag_0.corners[0]
                    scr_1 = scr_tag_1.corners[1]
                    scr_2 = scr_tag_2.corners[3]
                    scr_3 = scr_tag_3.corners[2]

                    # Lines for the Screen's outline
                    scr_left = Line(scr_0, scr_2)
                    scr_right = Line(scr_1, scr_3)
                    scr_top = Line(scr_2, scr_3)
                    scr_bottom = Line(scr_0, scr_1)

                    # Lines joining the centres of the external physical AprilTags
                    ext_left = Line(ext_tag_0.center, ext_tag_2.center)
                    ext_right = Line(ext_tag_1.center, ext_tag_3.center)
                    ext_top = Line(ext_tag_2.center, ext_tag_3.center)
                    ext_bottom = Line(ext_tag_0.center, ext_tag_1.center)

                    # Lengths of the external-AprilTag-lines
                    ext_left_len = DistanceTwixPoints(
                        ext_tag_0.center, ext_tag_2.center)
                    ext_right_len = DistanceTwixPoints(
                        ext_tag_1.center, ext_tag_3.center)
                    ext_top_len = DistanceTwixPoints(
                        ext_tag_2.center, ext_tag_3.center)
                    ext_bottom_len = DistanceTwixPoints(
                        ext_tag_0.center, ext_tag_1.center)

                    # Ratio between the
                    #           [distance between the centre-positions of the
                    #           external-AprilTag-lines and their intersections
                    #           with the (extended) screen-outline-lines]
                    # and the
                    #           length of the external-AprilTag-lines
                    # (Screen-Calibration-Data)
                    self.left_top_int = DistanceTwixPoints(
                        ext_tag_0.center, Intersection(ext_left, scr_top)) / ext_left_len
                    self.left_bot_int = DistanceTwixPoints(
                        ext_tag_0.center, Intersection(ext_left, scr_bottom)) / ext_left_len
                    self.right_top_int = DistanceTwixPoints(
                        ext_tag_1.center, Intersection(ext_right, scr_top)) / ext_right_len
                    self.right_bot_int = DistanceTwixPoints(
                        ext_tag_1.center, Intersection(ext_right, scr_bottom)) / ext_right_len
                    self.top_left_int = DistanceTwixPoints(
                        ext_tag_2.center, Intersection(ext_top, scr_left)) / ext_top_len
                    self.top_right_int = DistanceTwixPoints(
                        ext_tag_2.center, Intersection(ext_top, scr_right)) / ext_top_len
                    self.bot_left_int = DistanceTwixPoints(
                        ext_tag_0.center, Intersection(ext_bottom, scr_left)) / ext_bottom_len
                    self.bot_right_int = DistanceTwixPoints(
                        ext_tag_0.center, Intersection(ext_bottom, scr_right)) / ext_bottom_len

                    # Set the flag that we've completed ScreenCalibration
                    self.screen_calibrated = True

                # counting how long we've been showing the Calibration-Screen for
                self.calibration_time_counter += 1
                return  # don't execute rest of this function if screen calibration has not been completed
            else:   # we've completed Screen-Calibration
                if self.calibration_screen:   # if we've just finished Screen-Calibration
                    self.calibration_screen.CleanUp()
                    self.calibration_screen = None

                # the AprilTags we're looking for from the external clips
                tag_4 = None    # bottom right
                tag_6 = None    # bottom left
                tag_21 = None   # top left
                tag_25 = None   # top right

                # reading AprilTags
                tags = self.at_detector.detect(cv2.cvtColor(world_cam_img, cv2.COLOR_BGR2GRAY), estimate_tag_pose=False,
                                               camera_params=None, tag_size=0.013)

                for tag in tags:
                    if tag.hamming == 0:    # filters out false detections
                        if tag.tag_id == 4:
                            tag_4 = tag
                            self.DrawTagOutline(tag)
                        elif tag.tag_id == 6:
                            tag_6 = tag
                            self.DrawTagOutline(tag)
                        elif tag.tag_id == 21:
                            tag_21 = tag
                            self.DrawTagOutline(tag)
                        elif tag.tag_id == 25:
                            tag_25 = tag
                            self.DrawTagOutline(tag)

                if tag_4 and tag_6 and tag_21 and tag_25:
                    # coorinates of the april-tag-monitor-clips
                    ext_0 = tag_6.center    # bottom left
                    ext_1 = tag_4.center    # bottom right
                    ext_2 = tag_21.center   # top left
                    ext_3 = tag_25.center   # top right

                    # Calculating the positions of the screen corners:

                    # Lines joining the centres of the external physical AprilTags
                    ext_left = Line(ext_0, ext_2)
                    ext_right = Line(ext_1, ext_3)
                    ext_top = Line(ext_2, ext_3)
                    ext_bottom = Line(ext_0, ext_2)

                    # Predicting the coordinates of the intersections between the
                    # external-AprilTag-lines (extended) screen-outline-lines
                    left_top_int = (ext_0[0] + self.left_top_int * (ext_2[0] - ext_0[0]),
                                    ext_0[1] + self.left_top_int * (ext_2[1] - ext_0[1]))
                    left_bot_int = (ext_0[0] + self.left_bot_int * (ext_2[0] - ext_0[0]),
                                    ext_0[1] + self.left_bot_int * (ext_2[1] - ext_0[1]))
                    right_top_int = (ext_1[0] + self.right_top_int * (ext_3[0] - ext_1[0]),
                                     ext_1[1] + self.right_top_int * (ext_3[1] - ext_1[1]))
                    right_bot_int = (ext_1[0] + self.right_bot_int * (ext_3[0] - ext_1[0]),
                                     ext_1[1] + self.right_bot_int * (ext_3[1] - ext_1[1]))
                    top_left_int = (ext_2[0] + self.top_left_int * (ext_3[0] - ext_2[0]),
                                    ext_2[1] + self.top_left_int * (ext_3[1] - ext_2[1]))
                    top_right_int = (ext_2[0] + self.top_right_int * (ext_3[0] - ext_2[0]),
                                     ext_2[1] + self.top_right_int * (ext_3[1] - ext_2[1]))
                    bot_left_int = (ext_0[0] + self.bot_left_int * (ext_1[0] - ext_0[0]),
                                    ext_0[1] + self.bot_left_int * (ext_1[1] - ext_0[1]))
                    bot_right_int = (ext_0[0] + self.bot_right_int * (ext_1[0] - ext_0[0]),
                                     ext_0[1] + self.bot_right_int * (ext_1[1] - ext_0[1]))

                    # Predicting the screen outlines
                    scr_left = Line(top_left_int, bot_left_int)
                    scr_right = Line(top_right_int, bot_right_int)
                    scr_top = Line(left_top_int, right_top_int)
                    scr_bot = Line(left_bot_int, right_bot_int)

                    # Coordinates of the corners of the screen:
                    scr_0 = Intersection(scr_left, scr_bot)     # bottom left
                    scr_1 = Intersection(scr_right, scr_bot)    # bottom right
                    scr_2 = Intersection(scr_left, scr_top)     # top left
                    scr_3 = Intersection(scr_right, scr_top)    # top right

                    # drawing the screen outline in PupilCapture
                    draw_polyline(
                        [scr_0, scr_1, scr_3, scr_2], 3, RGBA(1.0, 0.0, 0, 1), line_type=gl.GL_LINE_LOOP
                    )

                    if self.gaze_location:   # if PupilCore has gaze location values
                        # NOTE: this code approximates the shape of the screen
                        #       as it appears on the WorldCamera image to a rectangle

                        # the rotation of the screen relative to the WorldCameraImage
                        av_slope = (scr_top.v + scr_bot.v) / 2
                        screen_rotation = atan(av_slope)

                        # coordinates of user's gaze-point on the WorldCamera image
                        # relative to top left screen corner
                        gaze_img_rel_x = self.gaze_location[0] - scr_2[0]
                        gaze_img_rel_y = self.gaze_location[1] - scr_2[1]

                        # calculating the angle of the line joining
                        # the gaze point and the top left screen corner
                        if gaze_img_rel_x == 0:
                            angle_abs = pi / 2
                        else:
                            angle_abs = atan(gaze_img_rel_y / gaze_img_rel_x)

                        # calculating the angle of the line joining
                        # the gaze point and the top left screen corner
                        # relative to the orientation (angle)
                        # of the screen on the WorldCamera image
                        angle_rel = angle_abs - screen_rotation

                        # calculating the distance between the user's gaze-position and
                        # the top left corner of the screen on the WordCamera image
                        d = DistanceTwixPoints(self.gaze_location, scr_2)

                        # calculating the width and height of the screen
                        # on to the WordCamera image
                        screen_width = (DistanceTwixPoints(scr_0, scr_1) +
                                        DistanceTwixPoints(scr_2, scr_3)) / 2
                        screen_height = (DistanceTwixPoints(scr_0, scr_2) +
                                         DistanceTwixPoints(scr_1, scr_3)) / 2

                        # calculating the position of the user's gaze
                        # relative to the monitor/screen's own pixel-coordinate-system
                        #   Note: the calib_marker_pixel_size is there to compensate
                        #   for the fact that the AprilTags used during ScreenCalibration
                        #   are a slight distance away from the corners of the screen
                        gaze_scr_x = int(cos(angle_rel) * d
                                         * (self.screen_resolution[0] - 2 * self.calib_marker_pixel_size) / screen_width) \
                            + self.calib_marker_pixel_size
                        gaze_scr_y = int(sin(angle_rel) * d
                                         * (self.screen_resolution[1] - 2 * self.calib_marker_pixel_size) / screen_height)   \
                            + self.calib_marker_pixel_size

                        # if the measured gaze is only slightly outside of the
                        # screen area, set the gaze point to the screen's edge
                        edge_tolerance = 160  # distance in screen-pixels
                        if gaze_scr_x < 0 and gaze_scr_x > -1 * edge_tolerance:
                            gaze_scr_x = 0
                        if gaze_scr_x > self.screen_resolution[0] and \
                                gaze_scr_x < self.screen_resolution[0] + edge_tolerance:
                            gaze_scr_x = self.screen_resolution[0] - 1
                        if gaze_scr_y < 0 and gaze_scr_y > -1 * edge_tolerance:
                            gaze_scr_y = 0
                        if gaze_scr_y > self.screen_resolution[1] and \
                                gaze_scr_y < self.screen_resolution[1] + edge_tolerance:
                            gaze_scr_y = self.screen_resolution[1] - 1

                        # if the user's gaze is on the screen,
                        # move the mouse to the calculated screen gaze position
                        if not(gaze_scr_x < 0 or gaze_scr_y < 0 or
                               gaze_scr_x > self.screen_resolution[0]
                               or gaze_scr_y > self.screen_resolution[1]):
                            # taking the average position of the gaze positions from the last few cycles
                            global cur_pos_index
                            global cursor_positions
                            global cursor_stability
                            # storing the new gaze point in the list of recent gaze points
                            cursor_positions[cur_pos_index] = (
                                gaze_scr_x, gaze_scr_y)
                            cur_pos_index += 1
                            if cur_pos_index == cursor_stability:
                                cur_pos_index = 0

                            # calculating the average of the last few gaze points
                            sum_x = 0
                            sum_y = 0
                            for pos in cursor_positions:
                                sum_x += pos[0]
                                sum_y += pos[1]
                            gaze_stabilised_x = sum_x / cursor_stability
                            gaze_stabilised_y = sum_y / cursor_stability

                            # moving the cursor to the user's gaze point
                            mouse.move(gaze_stabilised_x, gaze_stabilised_y)

    def recent_events(self, events):
        """Gets the latest values eye-gaze and plugin data."""
        gaze = events["gaze"]
        if gaze and len(gaze) > 0:
            basedata = gaze[0].get('base_data')

            if basedata:
                if gaze[0].get('confidence') < 0.8:
                    self.gaze_location = None
                    return
                loc = gaze[0].get('norm_pos')
                fs = self.g_pool.capture.frame_size  # frame height
                # user's eye-gaze-point relative to the WorldCamra image
                self.gaze_location = denormalize(loc, fs, flip_y=True)
        if "winks" in events:   # if the WinkDetection plugin is loaded
            data = events["winks"]
            if data:
                MouseClicks.ProcessSignal(data[0])

    def DrawTagOutline(self, tag):
        """Draws the outline of the input AprilTag on PupilCapture's
        WoldCamera stream in its graphical user interface."""
        draw_polyline(
            tag.corners.tolist(), 3, RGBA(1.0, 0.0, 0, 1), line_type=gl.GL_LINE_LOOP
        )
