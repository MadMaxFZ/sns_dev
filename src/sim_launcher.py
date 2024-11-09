#!/usr/bin/env python3
# This module will prepare and launch the simulation

import sys
import os

from controller import SimController            # simulation master controller
from viewer_gui import Viewer                   # simulation display
from datastore import SystemDataStore           # default system data
from multiprocessing import Queue               # Queues needed for IPC
from model_proc import ModelProcess             # model 'server' process

command_q, response_q = Queue, Queue
model = ModelProcess(command_q, response_q)
controller = SimController(command_q, response_q)
viewer = Viewer()
