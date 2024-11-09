#!/usr/bin/env python3
# This module defines a subclass of Process that implements the storage of the simulation model state
# This process will accept commands from the controller to update the state of the model.
# This process will expose body states in a shared memory segment that can be accessed by the viewer class instance.

from multiprocessing import Process


class ModelProcess(Process):
    """
    """
    def __init__(self, cmd_q, rsp_q, args, kwargs):
        """
        """
        super().__init__(*args, **kwargs)
        self._command_q = cmd_q
        self._response_q = rsp_q
