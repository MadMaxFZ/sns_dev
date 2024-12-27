#!/usr/bin/env python3

#  Copyright <YEAR> <COPYRIGHT HOLDER>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# This module defines a "controller" class that is responsible for directing the operation of
# he "model" and "viewer" class instances in the simulation
from model_proc import ModelProcess


class SimController:
    """
    The SimController serves the function of a conductor in an orchestra.
    It makes sure necessary objects exist and regulates their function.
    """
    @classmethod
    def initialize_viewer(cls):
        """
        This function will return an instance of the viewer object.
        """
        return "Viewer"

    def __init__(self, cmd_q, rsp_q):
        """
        Here we initialize the controller, which needs to ensure that the controller
        has access to all objects as necessary to regulate the simulation.
        """
        self._command_q = cmd_q
        self._respond_q = rsp_q
        self._model = None
        self._viewer = None

    def generate_model(self, sim_data=None):
        """
            This method creates an instance of ModelProcess,
            returns the Model Process.
        """
        # if no sim_data given, generate it
        if sim_data is None:
            from datastore import SystemDataStore
            sim_data = SystemDataStore()

        self._model = ModelProcess(self._command_q,
                                   self._respond_q,
                                   # sim_data
                                   )
