#!/usr/bin/python

import os, string, dircache, time, sys, md5, tarfile, re

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
	tmp = f.read(8192)
	while tmp:
		md.update(tmp)
		tmp = f.read(8192)
	f.close()
	return md.hexdigest()


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

def get_input_dcps():
    """ Return a dirpath list of all input DCP """

    dirlist = []
    try:
        dcp_dir = '/mnt/space/interfaces/in_ftp/.workdir/DCP'
        files = os.listdir(dcp_dir)
        for file in files:
            path = os.path.join(dcp_dir, file)
            if os.path.isdir(path):
                dirlist.append(path)
    except:
        pass

    return dirlist


def dcp_is_complete(dirpath):
    """ Search the ASSETMAP and all needed files of a DCP
    Return two object :
    - boolean : True if DCP is complete
    - dictionnay : all files needed ( { filename : found } )
    
    If dictionnary is empty, maybe the ASSETMAP file was not found"""

    filedic = {}
    # ASSETMAP contain all files informations
    assetmap_path = os.path.join (dirpath, "ASSETMAP")
    if not os.path.isfile( assetmap_path ):
        return False, filedic
    try:
        file = open(assetmap_path, 'r')
        txt = file.read()
    except IOError, inst:
        return False, filedic

    # We search all files needed by the DCP
    file_regex = re.compile("<(am:)?Path>(file:///)?(.*)</(am:)?Path>")
    file_list = file_regex.findall(txt)
    error = False
    for file in file_list:
        if not os.path.isfile( os.path.join(dirpath, file[2]) ):
            filedic[file[2]] = False
            error = True
        else:
            filedic[file[2]] = True
    if error:
        return False, filedic 
    else:
        return True, filedic

def dcp_create_tar(dirpath):
    # Create a tar of all non mxf files or directory and return the tar filename (or None)
    try:
        tar_path = os.path.join(dirpath, os.path.basename(dirpath)) + ".tar"
        tar = tarfile.open(tar_path, 'w')
        files = os.listdir(dirpath)
        for file in files:
            if file == "INGEST_IT":
                continue
            ext = os.path.splitext(file)[1]
            if ext != ".mxf" and ext != ".md5":
                tar.add( os.path.join(dirpath, file), file )
        tar.close()
        return tar_path
    except Exception, error:
        return None

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

