#!/usr/bin/python

import os, string, dircache, time, sys, md5

def ismd5(DIR):
        hex="0123456789abcdef"
        if len(DIR) != 32:
                return False
        for a in DIR:
                if string.find(hex, a) == -1:
                        return False
        return True

def md5sum(f):
	f = file(f)
	md = md5.new()
	tmp = f.read(16384)
	while tmp:
		md.update(tmp)
		tmp = f.read(16384)
	f.close()
	return md.hexdigest()

def sha1sum(path):
    sha1 = None
    try:
        sh = sha.new()
        fd = open(path, 'r')
        buf = fd.read(16384)
        while buf:
            sh.update(buf)
            buf = fd.read(16384)
        fd.close()
        sha1 = sh.hexdigest()
    except:
        pass
    return sha1

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
        _label = ""
        
        def __init__(self, logfile, label):
                self._file = open(logfile, "a", 1)
                self._label = label
                
        def write(self, str):
                t = time.gmtime()
                ts = "%02d/%02d/%02d GMT %02d:%02d:%02d " % (t[2], t[1], t[0], t[3], t[4], t[5])
                self._file.write(ts + "[" + self._label + "] " + str + "\n")

        def redirect_stdout_stderr(self):
                sys.stdout = sys.stderr = self._file

        def close(self):
                self._file.close()

