#!/usr/bin/python

import os, tarfile, re

def get_dcp_directory():
    return '/mnt/space/interfaces/in_ftp/SmartDCP'

def get_dcp_workdir():
    return '/mnt/space/interfaces/in_ftp/.workdir/SmartDCP'

def get_input_dcps():
    """ Return a dirpath list of all input DCP """

    dirlist = []
    try:
        files = os.listdir(get_dcp_workdir())
        for file in files:
            path = os.path.join(get_dcp_workdir(), file)
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

def dcp_create_ingest_demand_file(dcpname):
    path = os.path.join(get_dcp_workdir(), dcpname, 'INGEST_IT')
    try:
        fd = open(path, 'w')
        fd.close()
    except:
        return False
    else:
        return True
