# -*- coding: utf-8 -*-
# This module is intended for testing code structuresd and operation
import numpy as np
import psygnal
from vispy.app import use_app
from PyQt5 import QtWidgets, QtCore
# from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QCoreApplication
from multiprocessing import Queue, shared_memory as shm
from ..src import datastore

if __name__ == "__main__":
    # Here the message Queues and SharedMemory should be crated for use in the functions above:
    cmd, out = Queue(), Queue()
    buffer = np.zeros((3, 2), dtype=datastore.vec_type)
    buff_size = buffer.nbytes
    buff_idx = 0
    print(f"BUFFER_SIZE = {buff_size}")
    shared_state = shm.SharedMemory(name='state_buffer', create=True, size=buff_size)

    pass
