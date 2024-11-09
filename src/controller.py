#!/usr/bin/env python3
# This module defines a "controller" class that is responsible for directing the operation of
# he "model" and "viewer" class instances in the simulation
from sim_controls import Controls


class SimController:
    """
    """
    def __init__(self, cmd_q, rsp_q):
        """
        """
        controls = Controls()
