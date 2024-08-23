# -*- coding: utf-8 -*-
# This module is intended for testing code structuresd and operation
import numpy as np
import psygnal
from vispy.app import use_app
from PyQt5 import QtWidgets, QtCore
# from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QCoreApplication
from multiprocessing import Queue, shared_memory as shm
from src.datastore import vec_type

if __name__ == "__main__":
    # Here the message Queues and SharedMemory should be crated for use in the functions above:
    num_bods = 11
    cmd, out = Queue(), Queue()
    buffer0 = np.zeros((num_bods, 9), dtype=np.float64)

    print(f"BUFFER0_SIZE = {buffer0.nbytes}\nBUFFER0 SHAPE = {buffer0.shape}")
    shared_state = shm.SharedMemory(name='state_buffer', create=True, size=buffer0.nbytes * num_bods)
    ss_buf = shared_state.buf
    ss_buf = buffer0.flatten()
    print(f"SHMEM_SIZE = {shared_state.buf.nbytes}\nSHMEM SHAPE = {shared_state.buf.shape}")
    print(f"SS_BUF_SIZE = {ss_buf.nbytes}\nSS_BUF_SHAPE = {ss_buf.shape}")

    buffer1 = np.array(shared_state.buf).reshape((num_bods, 9))

    print(f"BUFFER1_SIZE = {buffer1.nbytes}\nBUFFER SHAPE = {buffer1.shape}")
    shared_state.unlink()
    shared_state.close()
    pass
