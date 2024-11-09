#!/usr/bin/env python3
# This module defines the Viewer class that organizes and manages the textual and
# graphical representations of the Model state.
from PyQt5 import QtWidgets, QtCore
from sim_canvas import CanvasWrapper
from sim_controls import Controls


class Viewer(QtWidgets.QMainWindow):
    """
    """
    def __init__(self, *args, **kwargs):
        """
        """
        super().__init__(*args, **kwargs)
        viewer = "Empty Viewer"
