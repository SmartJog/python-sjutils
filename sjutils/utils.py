import os, string, dircache, time, sys, md5, sha, re
from htmlentitydefs import entitydefs

def ismd5(md5):
    hex = "0123456789abcdef"
    if len(md5) != 32:
        return False
    for a in md5:
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
    f = file(path)
    sh = sha.new()
    tmp = f.read(16384)
    while tmp:
        sh.update(tmp)
        tmp = f.read(16384)
    f.close()
    return sh.hexdigest()

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

def delete_directory_branch(branch_path, path_limit=None):
    """ Try to delete branch_path until the directory is not empty
    and until it's not the limit path.
    Ex : delete_directory_branch('/root/toto/tata/titi', '/root') remove
    'titi' if empty and different to path_limit, then 'tata' if... etc
    """
    if os.path.isdir(branch_path):
        if path_limit and os.path.samefile(branch_path, path_limit):
            return
        try:
            os.rmdir(branch_path)
        except:
            pass
        else:
            delete_directory_branch( os.path.dirname(branch_path), path_limit )

def create_symlink(linkvalue, linkpath):
    if os.path.islink(linkpath): # linkpath exists and is a link
        if os.readlink(linkpath) != linkvalue: # comparing link value
            os.unlink(linkpath)
            os.symlink(linkvalue, linkpath)
    elif not os.path.exists(linkpath): # linkpath is not a link, maybe it doesn't exist
        os.symlink(linkvalue, linkpath)
    else: # linkpath is not a link, and exists, so it is a file
        os.unlink(linkpath)
        os.symlink(linkvalue, linkpath)

class Logger:
    "Sjutils log class"
    _file = ""
    _label = ""

    def __init__(self, logfile, label=None):
        self._file = open(logfile, "a", 1)
        self._label = label and "[%s]" % label or ""

    def write(self, str):
        t = time.gmtime()
        ts = "%02d/%02d/%02d GMT %02d:%02d:%02d " % (t[2], t[1], t[0], t[3], t[4], t[5])
        self._file.write(ts + self._label + str + "\n")

    def redirect_stdout_stderr(self):
        sys.stdout = sys.stderr = self._file

    def close(self):
        self._file.close()


entitydefs_inverted = {}
for k, v in entitydefs.items():
    entitydefs_inverted[v] = k

_badchars_regex = re.compile('|'.join(entitydefs.values()))
_been_fixed_regex = re.compile('&\w+;|&#[0-9]+;')

def html_entity_fixer(text, skipchars=[], extra_careful=1):
    # if extra_careful we don't attempt to do anything to
    # the string if it might have been converted already.
    if extra_careful and _been_fixed_regex.findall(text):
        return text

    if type(skipchars) == type('s'):
        skipchars = [skipchars]

    keyholder = []
    for x in _badchars_regex.findall(text):
        if x not in skipchars:
            keyholder.append(x)
    text = text.replace('&','&amp;')
    text = text.replace('\x80', '&#8364;')
    for each in keyholder:
        if each == '&':
            continue

        better = entitydefs_inverted[each]
        if not better.startswith('&#'):
            better = '&%s;' % entitydefs_inverted[each]

        text = text.replace(each, better)
    return text


class Logger2:
    "Sjutils log class"
    _file = ""
    _label = ""

    def __init__(self, logfile, label=None):
        self._file = open(logfile, "a", 1)

    def write(self, *args):
        t = time.gmtime()
        ts = "%02d/%02d/%02d GMT %02d:%02d:%02d" % (t[2], t[1], t[0], t[3], t[4], t[5])
        ts += " " + str(os.getpid())
        for arg in args:
            if type(arg) == type((1,)):
                ts += " " + " ".join(map(str, arg))
            else:
                ts += " " + str(arg)
        self._file.write(ts + "\n")

    def redirect_stdout_stderr(self):
        sys.stdout = sys.stderr = self._file

    def close(self):
        self._file.close()

class DefaultDict(dict):
    """Trivial DefaultDict implementation. Basically returns the
    default value for missing keys.

    TODO: Python2.5 has __missing__ for dict subclasses, we should use
    this (or collections.defaultdict) instead when switching to 2.5"""

    def __init__(self, default = None, *args, **kw):
        dict.__init__(self, *args, **kw)
        self.default = default

    def __getitem__(self, key):
        return self.get(key, self.default)
