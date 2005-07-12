#!/usr/bin/python

import os, string, dircache, time

def ismd5(DIR):
        hex="0123456789abcdef"
        if len(DIR) != 32:
                return False
        for a in DIR:
                if string.find(hex, a) == -1:
                        return False
        return True


def delete_recursive(path):
        if os.path.isfile(path):
                os.remove(path)
                return

        for FILE in dircache.listdir(path):
                file_or_dir = os.path.join(path, FILE)
                if os.path.isdir(file_or_dir) and not os.path.islink(file_or_dir):
                        delete_recursive(file_or_dir)
                else:
                        os.remove(file_or_dir)
        os.rmdir(path)

class Logger:
        "Sjutils log class"
        _file = ""
        def __init__(self, logfile, label)
                _file = open(logfile, "a", 1)
                _label = label
                
        def write(self, str)
                _file.write(time.ctime() + " " + _label + " " + str)

        def close(self)
                _file.close()
