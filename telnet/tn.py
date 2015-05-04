#!/usr/bin/env python
"""

"""
import argparse
import time
from threading import Thread
parser = argparse.ArgumentParser(description='Creates a simple TCP port forwarder.')


def thread1():
    i = 0
    while i < 100:
        i += 1
        print "Thread 1, Loop: %s" % i
        time.sleep(.1)


if __name__ == '__main__':
    t1 = Thread(target=thread1)
    t1.start()
    j = 0
    while j < 50:
        j += 1
        print "Main Thread, Loop %s" % j
        time.sleep(.1)
    print "waiting for thread 1"
    t1.join()


