# -*- coding: utf-8 -*-

import os
import sys
import time


class Logger2:
    "Sjutils log class"
    _file = ""
    _label = ""

    def __init__(self, logfile, _label=None):
        self._file = open(logfile, "a", 1)

    def write(self, *args):
        tgmt = time.gmtime()
        tstring = "%02d/%02d/%02d GMT %02d:%02d:%02d" % (tgmt[2], tgmt[1], tgmt[0], tgmt[3], tgmt[4], tgmt[5])
        tstring += " " + str(os.getpid())
        for arg in args:
            if type(arg) == type((1,)):
                tstring += " " + " ".join(map(str, arg))
            else:
                tstring += " " + str(arg)
        self._file.write(tstring + "\n")

    def redirect_stdout_stderr(self):
        sys.stdout = sys.stderr = self._file

    def close(self):
        self._file.close()
