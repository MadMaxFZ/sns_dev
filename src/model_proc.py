#!/usr/bin/env python3

#  Copyright <YEAR> <COPYRIGHT HOLDER>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# This module defines a subclass of Process that implements the storage of the simulation model state
# This process will accept commands from the controller to update the state of the model.
# This process will expose body states in a shared memory segment that can be accessed by the viewer class instance.

from multiprocessing import Process

from simsystem import SimSystem


class ModelProcess(Process):
    """
    """
    def __init__(self, cmd_q, rsp_q,  # *args, **kwargs
                 ):
        """
            Bare bones initialization of a ModelProces instance
        """
        super().__init__(  # *args, **kwargs
                         )
        self._command_q = cmd_q
        self._respond_q = rsp_q
        self._system    = SimSystem()

    def run(self):
        """
            Here will be the code to operate this model process
        """
        print("MNodel Process generated...")
        print("Here is the payload...")

