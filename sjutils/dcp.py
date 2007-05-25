#!/usr/bin/python

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import os, base64, tarfile, re

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

def dcp_create_tar(dirpath):
    # Create a tar of all non mxf files or directory and return the tar filename (or None)
    try:
        tar_path = os.path.join(dirpath, os.path.basename(dirpath)) + ".tar"
        tar = tarfile.open(tar_path, 'w')
        root_len = len(dirpath)
        for root, dirs, files in os.walk(dirpath):
            for file in files:
                if file == "INGEST_IT":
                    continue
                ext = os.path.splitext(file)[1]
                if ext != ".mxf" and ext != ".md5" and ext != ".sha":
                    tar.add( os.path.join(root, file), os.path.join(root[root_len:], file) )
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

def get_dcp_hash_from_sha1(sha1):
    if sha1:
        return sha1.decode('hex').encode('base64')[:-1]
    else:
        return None

def get_dcp_hash(path):
    sha = None
    try:
        sha = open(path + '.sha', 'r').readline()
        return get_dcp_hash_from_sha1(sha)
    except:
        return None


# AssetMap : XML Parsing Class (SAX)
class AssetMapHandler(ContentHandler):
    def __init__(self, files, pklsList):
        self.tmp_id = ''
        self.isPackingList = False
        self.buf = ''
        self.files = files
        self.pklsList = pklsList
    def startElement(self, name, attrs):
        self.buf = ''
    def endElement(self, name):
        if name == 'Id':
            self.tmp_id = self.buf
        if name == 'PackingList':
            self.isPackingList = True
        elif name == 'Path':
            if self.buf.startswith('file:///'):
                self.buf = self.buf[8:]
            self.files[self.tmp_id] = [self.buf, None, None, None]
            if self.isPackingList:
                self.pklsList[self.tmp_id] = self.buf
            self.isPackingList = False
    def characters(self, ch):
        self.buf += ch

# PackingFile : XML Parsing Class (SAX)
class PklHandler(ContentHandler):
    def __init__(self, files):
        self.tmp_id = ''
        self.buf = ''
        self.files = files
    def startElement(self, name, attrs):
        self.buf = ''
    def endElement(self, name):
        if name == 'Id':
            self.tmp_id = self.buf
        elif name == 'Hash':
            try:
                self.files[self.tmp_id][1]= self.buf
            except:
                pass
    def characters(self, ch):
        self.buf += ch

def get_dcp_infos(dirpath):
    """ Search the ASSETMAP.xml and all needed files of a DCP
    Return three object :
    - boolean : True if DCP is complete
    - boolean : True if DCP is valid (correct hash values)
    - dictionnay : all files needed ( { id : [filename, hash, found, correct_hash] } )

    If dictionnary is empty, maybe the ASSETMAP file was not found"""

    pklsList = {}
    files = {}

    # ASSETMAP.xml contain all files informations
    assetmap_list = ( 'ASSETMAP', 'ASSETMAP.xml', 'ASSETMAP.XML', 'assetmap', 'assetmap.xml' )
    txt = ""
    found = False
    for assetmap in assetmap_list:
        assetmap_path = os.path.join (dirpath, assetmap)
        if not os.path.isfile( assetmap_path ):
            continue
        try:
            file = open(assetmap_path, 'r')
            txt = file.read()
        except IOError, inst:
            continue
        else:
            found = True
            break

    if not found:
        return False, False, files

    # We search all files needed by the DCP (write it in 'files' variable)
    doc = AssetMapHandler(files, pklsList)
    saxparser = make_parser()
    saxparser.setContentHandler(doc)
    try:
        datasource = open(assetmap_path,"r")
        saxparser.parse(datasource)
    except:
        return False, False, files

    # We find the hash for each file (in PKL files)
    try:
        doc = PklHandler(files)
        saxparser.setContentHandler(doc)
    except:
        return False, False, files

    for id in pklsList.keys():
        try:
            datasource = open( os.path.join(dirpath, pklsList[id]), "r" )
            saxparser.parse(datasource)
            files[id][3] = files[id][2] = True
        except:
            pass

    # We check if the hash is valid
    error = False
    for id in files.keys():
        filepath = os.path.join(dirpath, files[id][0])
        if not os.path.isfile(filepath):
            files[id][2] = False
            error = True
        else:
            files[id][2] = True
            hash = get_dcp_hash(filepath)
            if hash and files[id][1] == hash:
                files[id][3] = True
            elif files[id][1] and id not in pklsList.keys():
                files[id][3] = False
    if error:
        return False, False, files
    else:
        # We check the validity of the DCP
        valid = True
        for id in files.keys():
            if not files[id][3]:
                valid = False
        return True, valid, files

def get_dcp_content_titles(dirpath):
    title_regex = re.compile("<ContentTitleText>(.*)</ContentTitleText>")
    titles = []
    for file in os.listdir(dirpath):
        ext = os.path.splitext(file)[1]
        if ext == ".xml" or ext == ".XML":
            txt = open( os.path.join(dirpath, file), 'r' ).read()
            title = title_regex.findall(txt)
            if title:
                titles.append(title[0])

    titles = list(set(titles))
    return titles

