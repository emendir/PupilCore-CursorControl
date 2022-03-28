from CursorControl import mouse
import sys
import time

if "linux" in sys.platform:
    from CursorControl.Xlib import X, display, ext
    d = display.Display()
    s = d.screen()
    root = s.root


def OnRightWink():
    """Gets called when the right eye completes a wink
    during which the left eye was always open"""
    if "linux" in sys.platform:
        ext.xtest.fake_input(d, X.ButtonPress, 3)
        d.sync()
        time.sleep(0.001)
        ext.xtest.fake_input(d, X.ButtonRelease, 3)
        d.sync()
    else:
        mouse.click(mouse.LEFT)


def OnLeftWink():
    """Gets called when the left eye completes a wink
    during which the right eye was always open"""
    if "linux" in sys.platform:
        ext.xtest.fake_input(d, X.ButtonPress, 1)
        d.sync()
        time.sleep(0.001)
        ext.xtest.fake_input(d, X.ButtonRelease, 1)
        d.sync()
    else:
        mouse.click(mouse.LEFT)


status_right = ""
status_left = ""


def ProcessSignal(message):
    if not message:
        return
    global status_right
    global status_left
    if message["eye"] == "right":
        if message["type"] == "onset":
            if status_right == "":
                status_right = "onset"
        if message["type"] == "offset":
            if status_right == "onset":
                status_right = ""
                if status_left == "onset":  # if left is closed
                    status_left = ""        # cancel left wink and this
                else:
                    OnRightWink()
    if message["eye"] == "left":
        if message["type"] == "onset":
            if status_left == "":
                status_left = "onset"
        if message["type"] == "offset":
            if status_left == "onset":
                status_left = ""
                if status_right == "onset":  # if right is closed
                    status_right = ""       # cancel right wink and this
                else:
                    OnLeftWink()
