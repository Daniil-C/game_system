"""
Module, containing Monitor class.
"""
import threading


class Monitor:
    """
    Base class for objects, accessable from multiple threads.
    """
    def __init__(self):
        object.__setattr__(self, "_Monitor_sem", threading.Semaphore(1))

    def __setattr__(self, name, value):
        object.__getattribute__(self, "_Monitor_sem").acquire()
        object.__setattr__(self, name, value)
        object.__getattribute__(self, "_Monitor_sem").release()

    def __getattribute__(self, name):
        object.__getattribute__(self, "_Monitor_sem").acquire()
        val = object.__getattribute__(self, name)
        object.__getattribute__(self, "_Monitor_sem").release()
        return val
