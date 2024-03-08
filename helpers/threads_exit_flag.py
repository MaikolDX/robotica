# threads_exit_flag.py

import threading

# create a threading event to signal thread exit
exit_flag = threading.Event()


def set_exit_flag():
    # set the exit_flag to signal the thread to exit
    exit_flag.set()

def get_exit_flag():
    # get the exit_flag
    return exit_flag