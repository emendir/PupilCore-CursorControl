"""This module displays the Screen-Calibration screen when the MonitorRecognition
plugin is first run.
It is completely independent of the standard main PupilCore Pupil-Calibration.
Its purpose is to allow the MonitorRecognition plugin to calculate the position
of the screen relative to the externally attached april-tag-clips during runtime."""

from pyglui.pyfontstash import fontstash as fs
from pyglui.cygl.utils import RGBA, draw_points, init
from pyglui.cygl.shader import Shader
from pyglui import ui
import glfw
from OpenGL.GL import *

import functools
import logging

import numpy as np
import cv2
import os.path
import time

import sys

# getting the path to where this plugin is stored on the computer
plugin_path = ""
for path in sys.path:
    if os.path.basename(path) == "plugins":
        plugin_path = path

# create logger for the context of this function
logger = logging.getLogger(__name__)


def basic_gl_setup():
    glEnable(GL_POINT_SPRITE)
    glEnable(GL_VERTEX_PROGRAM_POINT_SIZE)  # overwrite pointsize
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_BLEND)
    glClearColor(0.8, 0.8, 0.8, 1.0)
    glEnable(GL_LINE_SMOOTH)
    # glEnable(GL_POINT_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    glEnable(GL_POLYGON_SMOOTH)
    glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)


def adjust_gl_view(w, h, window):
    """
    adjust view onto our scene.
    """
    print(w, h)
    glViewport(0, 0, int(w), int(h))
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, w, h, 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


class CalibrationScreen():
    quit = False

    def Show(self):
        global quit
        quit = False

        # Callback functions
        def on_resize(window, w, h):
            h = max(h, 1)
            w = max(w, 1)
            hdpi_factor = (
                glfw.get_framebuffer_size(
                    window)[0] / glfw.get_window_size(window)[0]
            )
            w, h = w * hdpi_factor, h * hdpi_factor
            active_window = glfw.get_current_context()
            glfw.make_context_current(active_window)
            # norm_size = normalize((w,h),glfw.get_window_size(window))
            # fb_size = denormalize(norm_size,glfw.get_framebuffer_size(window))
            adjust_gl_view(w, h, window)
            glfw.make_context_current(active_window)

        def on_close(window):
            global quit
            quit = True
            self.quit = True
            logger.info("Process closing from window")

        # get glfw started
        glfw.init()
        self.monitor = glfw.get_primary_monitor()
        self.video_mode = glfw.get_video_mode(self.monitor)

        self.window = glfw.create_window(
            self.video_mode.size[0], self.video_mode.size[1], "pyglui demo", None, None)
        # making window full screen
        glfw.set_window_monitor(
            self.window,
            self.monitor,
            0,
            0,
            *self.video_mode.size,
            self.video_mode.refresh_rate,
        )
        if not self.window:
            exit()

        glfw.set_window_pos(self.window, 0, 0)
        # Register callbacks for the window
        glfw.set_window_size_callback(self.window, on_resize)
        glfw.set_window_close_callback(self.window, on_close)
        # test out new paste function
        self.oldcontext = glfw.get_current_context()
        glfw.make_context_current(self.window)
        init()
        basic_gl_setup()
        glfw.swap_interval(0)

        on_resize(self.window, *glfw.get_window_size(self.window))

        glClearColor(1.0, 1.0, 1.0, 1)

    def CleanUp(self):
        print("STOPPING")
        glfw.destroy_window(self.window)
        # glfw.terminate()
        logger.debug("Closed Screen Calibration window.")

    def Paint(self):
        glfw.make_context_current(self.window)
        glClear(GL_COLOR_BUFFER_BIT)

        self.DrawTag("tag36_11_00000.png", (0, 0))
        self.DrawTag("tag36_11_00001.png", (1, 0))
        self.DrawTag("tag36_11_00002.png", (0, 1))
        self.DrawTag("tag36_11_00003.png", (1, 1))

        glfw.swap_buffers(self.window)
        glfw.poll_events()
        glClearColor(0, 0, 0, 1)

    def DrawSquare(self, screen_position, size: int, color: RGBA):
        x, y = screen_position
        points = np.array(
            [[x, y], [x + size, y], [x + size, y + size], [x, y + size]])
        glColor4f(color.r, color.g, color.b, color.a)
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(2, GL_DOUBLE, 0, points)
        glDrawArrays(GL_POLYGON, 0, points.shape[0])

    pixel_size = 15

    def DrawTag(self, imageName, position):
        """Draws the specified AprilTag at the specified position on the screen.
        Parameters:
            imageName (string): the path to the AprilTag png image to draw_points
            position (tuple of bits): which corner of the screen the AprilTag should be drawn in.
        """
        if os.path.exists(imageName):
            image = cv2.imread(imageName)
        else:
            image = cv2.imread(os.path.join(
                plugin_path, "CursorControl", imageName))
        ix, iy, irgb = image.shape

        # working out the position of the AprilTag in pixels
        if position[0] == 0:
            pos_x = 0
        else:
            pos_x = self.video_mode.size[0] - ix * self.pixel_size
        if position[1] == 1:
            pos_y = 0
        else:
            pos_y = self.video_mode.size[1] - iy * self.pixel_size

        # Draw the AprilTag's pixels
        for x in range(ix):
            for y in range(iy):
                self.DrawSquare((pos_x + x * self.pixel_size, pos_y + y * self.pixel_size),
                                self.pixel_size, RGBA(image[y, x][0], image[y, x][1], image[y, x][2], 1))


if __name__ == "__main__":
    a = CalibrationScreen()
    a.Show()
    while(not quit):
        a.Paint()
    a.CleanUp()
