# -*- coding: utf-8 -*-

import os, string, dircache, time, sys, md5, sha, re
from htmlentitydefs import entitydefs
import threading

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

def pretty_size(size, verbose=False):
    """
        returns pretty_size of float 'size', expressed as Bytes, like 424MB.
        If verbose is True, return value will be "424 MegaBytes".
    """
    import gettext
    gettext.install('python-sjutils')
    base = _("Bytes")
    for unit in ["", "Kilo", "Mega", "Giga", "Tera", "Peta", "Exa", "Zetta", "Yotta"]:
        if verbose:
            final_unit =  len(unit) and  (unit + base) or  base
        else:
            final_unit =  len(unit) and  (unit[0] +  base[0]) or base

        if size < 1024.0:
            return "%3.1f %s" % (size, final_unit)

        if (unit != "Yotta"):
            size /= 1024.0

    return "%3.1f %s" % (size, final_unit)

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

def html_escape(text):
    """
    Escape HTML characters / entities in @text.
    """
    # We start by replacing '&'
    text = text.replace('&', '&amp;')
    # We don't want '&' in our dict, as it would mess up any previous
    # replace() we'd done
    entitydefs_inverted = ((value, key)
                           for key, value
                           in entitydefs.iteritems()
                           if value != '&')
    for key, value in entitydefs_inverted:
        text = text.replace(key, '&%s;' % value)
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

import ConfigParser
class OrderedRawConfigParser(ConfigParser.RawConfigParser):
    """RawConfigParser subclass, with an ordered write() method."""

    def write(self, fp):
        """Write an .ini-format representation of the configuration
        state. Sections are written sorted."""
        if self._defaults:
            fp.write("[%s]\n" % DEFAULTSECT)
            for (key, value) in self._defaults.items():
                fp.write("%s = %s\n" % (key, str(value).replace('\n', '\n\t')))
            fp.write("\n")
        tmp_sections = self._sections.keys()
        tmp_sections.sort()
        for section in tmp_sections:
            fp.write("[%s]\n" % section)
            tmp_keys = self._sections[section].keys()
            tmp_keys.sort()
            for key in tmp_keys:
                if key != "__name__":
                    fp.write("%s = %s\n" %
                             (key, str(self._sections[section][key]).replace('\n', '\n\t')))
            fp.write("\n")

class OrderedConfigParser(ConfigParser.ConfigParser, OrderedRawConfigParser):
    """A ConfigParser subclass, with an ordered write() method."""

    def write(self, fp):
        OrderedRawConfigParser.write(self, fp)

class OrderedSafeConfigParser(ConfigParser.SafeConfigParser, OrderedConfigParser):
    """A SafeConfigParser subclass, with an ordered write() method."""

    def write(self, fp):
        OrderedRawConfigParser.write(self, fp)

def any(iterable, predicate = bool, *args, **kw):
    """Return True if predicate(x, *args, **kw) is True for any x in the iterable."""
    for elt in iterable:
        if predicate(elt, *args, **kw):
            return True
    return False

def all(iterable, predicate = bool, *args, **kw):
    """Return True if predicate(x, *args, **kw) is True for all values x in the iterable."""
    for elt in iterable:
        if not predicate(elt, *args, **kw):
            return False
    return True

import os
import logging
import bz2
import gzip
from logging.handlers import BaseRotatingHandler

try:
    import codecs
except ImportError:
    codecs = None

class CompressedRotatingFileHandler(BaseRotatingHandler):

    def __init__(self, filename, mode='a', max_bytes=256, backup_count=5, encoding=None, cmp_type='gzip', cmp_level=9, suffixes='gz'):
        if max_bytes > 0:
            mode = 'a'
        BaseRotatingHandler.__init__(self, filename, mode, encoding)
        self.filename = filename
        self.backup_count = backup_count
        self.max_bytes = max_bytes
        self.cmp_type = cmp_type
        self.cmp_level = cmp_level
        self.suffixes = suffixes

    def _doCompress(self, target):
        if self.cmp_type is 'gzip':
            f_in = open(target, 'r')
            f_out = gzip.open(target + '.tmp', 'w', compresslevel=self.cmp_level)
            f_out.writelines(f_in)
            f_out.close()
            f_in.close()
            os.remove(target)
            os.rename(target + '.tmp', target)
        elif self.cmp_type is 'bzip2':
            f_in = open(target, 'r')
            f_out = bz2.BZ2File(target + '.tmp', 'w', compresslevel=self.cmp_level)
            f_out.writelines(f_in)
            f_out.close()
            f_in.close()
            os.remove(target)
            os.rename(target + '.tmp', target)
        else:
            raise Exception('Compression type not supported')

    def doRollover(self):
        self.stream.close()
        if self.backup_count > 0:
            for i in range(self.backup_count - 1, 0, -1):
                sfn = "%s.%d.%s" % (self.baseFilename, i, self.suffixes)
                dfn = "%s.%d.%s" % (self.baseFilename, i + 1, self.suffixes)
                if os.path.exists(sfn):
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
            dfn = self.baseFilename + ".1." + self.suffixes
            if os.path.exists(dfn):
                os.remove(dfn)
            os.rename(self.baseFilename, dfn)
            self._doCompress(dfn)
        if self.encoding:
            self.stream = codecs.open(self.baseFilename, 'w', self.encoding)
        else:
            self.stream = open(self.baseFilename, 'w')

    def shouldRollover(self, record):
        if self.max_bytes > 0:
            msg = "%s\n" % self.format(record)
            self.stream.seek(0, 2)  #due to non-posix-compliant Windows feature
            if self.stream.tell() + len(msg) >= self.max_bytes:
                return 1
        return 0


from psycopg2.pool import ThreadedConnectionPool
import psycopg2

def manage_pgconn(user, password, dbname, host='localhost', port='5432'):
    """ Manage the postgresql database connection using
    information stored on conf_file """
    def __nested__(func):
        db_opts = { 'user' : user, 'password' : password, 'host' : host, 'port' : port, 'dbname' : dbname }
        return PgConnProxy(db_opts, func)

    return __nested__

def manage_pgconn_conf(conf_file, section="database"):
    """ Manage the postgresql database connection using
    information stored on conf_file """
    def __nested__(func):
        from ConfigParser import RawConfigParser
        conf = RawConfigParser()
        conf.read(conf_file)
        items = dict(conf.items(section))
        return PgConnProxy(items, func)

    return __nested__


class PgConnProxy(object):
    """
    A proxy class to allow compatibility between
    PgConnManager's Factory system and decorators.
    """

    def __init__(self, db_opts, func):
        self.__params__ = db_opts
        self.__func__ = func
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__
        self.__module__ = func.__module__
        self.__dict__.update(func.__dict__)

    def __call__(self, *args, **kw):
        manager = PgConnManager(self.__params__)
        return manager.decorate(self.__func__, *args, **kw)


class PgConnManager(object):
    """
    Manage postgresql database connections.
    """

    # dict to keep track of PgConnManager instances
    _instances = {}

    class DatabaseError(psycopg2.Error):
        """ Raised when database connection error occurs. """
        pass

    def __new__(self, *kargs, **kwargs):
        db_opts = kargs[0]

        # We can either accept 'database' or 'dbname' as an input
        if db_opts.has_key('database') and not db_opts.has_key('dbname'):
            db_opts['dbname'] = db_opts['database']

        # This is ugly but since dict types cannot be used
        # as keys in another dict, we need to transform it.
        # This transformation was chosen as it is human
        # readable, it could be changed to a more optimised one.
        db_str = "host=%(host)s port=%(port)s user=%(user)s password=%(password)s dbname=%(dbname)s" % db_opts

        if not self._instances.has_key(db_str):
            self._instances[db_str] = super(PgConnManager, self).__new__(self, *kargs, **kwargs)
            self._instances[db_str].lock = threading.Lock()
        return self._instances[db_str]

    def __init__(self, db_opts):
        self.__params__ = db_opts
        if not hasattr(self, '__conn_pool__'):
            self.__conn_pool__ = None

    def decorate(self, func, *args, **kw):
        try:
            ctx_list = self.connect()
            try:
                ret = func(self, ctx_list, *args, **kw)

                # Connexion(s) wasn't released by user, so we have to release it/them
                for ctx in ctx_list:
                    if ctx['conn'] is not None:
                        self.release(ctx)

                return ret
            except psycopg2.Error, _error:
                for ctx in ctx_list:
                    ctx['cursor'] = None
                    if ctx['conn']:
                        self.__conn_pool__.putconn(ctx['conn'], close=True)
                    ctx['conn'] = None
                raise
            except Exception:
                for ctx in ctx_list:
                    self.rollback(ctx)
                    self.release(ctx)
                raise
        except psycopg2.Error, _error:
            # We do not want our users to have to 'import psycopg2' to
            # handle the module's underlying database errors
            _, value, traceback = sys.exc_info()
            raise self.DatabaseError, value, traceback

    def _new_ctx(self):
        """ Create a new context object. """
        ret = { 'conn' : None, 'cursor' : None }
        ret['conn'] = self.__conn_pool__.getconn()
        return ret

    def connect(self, ctx_list = None):
        """ Connect to database. """
        try:
            self.lock.acquire_lock()
            try:
                if not self.__conn_pool__:
                    connector = "host=%(host)s port=%(port)s user=%(user)s password=%(password)s dbname=%(dbname)s" % self.__params__
                    self.__conn_pool__ = ThreadedConnectionPool(1, 20, connector)
            finally:
                self.lock.release_lock()
            if not ctx_list:
                ctx_list = []
            ctx_list.append(self._new_ctx())
            return ctx_list

        except psycopg2.Error, _error:
            # We do not want our users to have to 'import psycopg2' to
            # handle the module's underlying database errors
            _, value, traceback = sys.exc_info()
            raise self.DatabaseError, value, traceback

    def execute(self, ctx, query, options=None):
        """ Execute an SQL query. """
        try:
            if not ctx['conn']:
                ctx['conn'] = self.__conn_pool__.getconn()
            if not ctx['cursor']:
                ctx['cursor'] = ctx['conn'].cursor()
            if options:
                ctx['cursor'].execute(query, options)
            else:
                ctx['cursor'].execute(query)
        except psycopg2.Error, _error:
            ctx['cursor'] = None
            if ctx['conn']:
                self.__conn_pool__.putconn(ctx['conn'], close=True)
            ctx['conn'] = None
            # We do not want our users to have to 'import psycopg2' to
            # handle the module's underlying database errors
            _, value, traceback = sys.exc_info()
            raise self.DatabaseError, value, traceback

    def commit(self, ctx):
        """ Commit changes to dabatase. """
        try:
            ctx['conn'].commit()
        except psycopg2.Error, _error:
            self.rollback()
            ctx['cursor'] = None
            if ctx['conn']:
                self.__conn_pool__.putconn(ctx['conn'], close=True)
            ctx['conn'] = None
            # We do not want our users to have to 'import psycopg2' to
            # handle the module's underlying database errors
            _, value, traceback = sys.exc_info()
            raise self.DatabaseError, value, traceback

    def rollback(self, ctx):
        """ Rollback changes to database. """
        if not ctx['conn'].closed:
            ctx['conn'].rollback()

    def release(self, ctx):
        """ Release database connection. """
        ctx['cursor'] = None
        if ctx['conn']:
            self.__conn_pool__.putconn(ctx['conn'], close=False)
        ctx['conn'] = None

    def release_all(self, ctx_list):
        """ Release all database connections from a context list. """
        for ctx in ctx_list:
            self.release(ctx)
        ctx_list = None

    def fetchall(self, ctx):
        """ Return all rows of current request. """
        return ctx['cursor'].fetchall()

    def fetchone(self, ctx):
        """ Return one row of current request. """
        return ctx['cursor'].fetchone()

def flatten_dict(dictionary, sep = '/'):
    """
    Flatten a Python dictionary, in an iterative way (no stack
    overflow)

    Flattenning a dictionary can be compared to the depth-first
    traversal of a B-tree. We can iterate through the tree's branches
    by keeping a stack (FILO) of the nodes we're traversing.

    @param dictionary The dictionary to flatten
    @param sep A string that will be used to join the keys
    @return The flattened dictionary
    """

    my_stack = dictionary.items()
    result = {}

    while my_stack:
        key, value = my_stack.pop()
        if isinstance(value, dict):
            my_stack.extend([(key + sep + inner_key, inner_value) for inner_key, inner_value in value.iteritems()])
        else:
            result[key] = value

    return result

def flatten_list(my_list):
    """
    Flatten a Python list, in an iterative way (no stack
    overflow)

    Flattenning a list can be compared to the depth-first traversal of
    a B-tree. We can iterate through the tree's branches by keeping a
    stack (FILO) of the nodes we're traversing.

    Note: I used collections.deque here in order to avoid using
    multiple calls to list() (to avoid in-place modification of the
    list) and reverse() (to preserve the order in the stack). The only
    beef I have with deque is its input-reversing extendleft() method,
    which forces me to call reversed() on the inner lists.

    Note 2: Currently, we completely collapse empty lists, i.e. they
    will never be part of the returned list.

    @param my_list The list to flatten
    @return The flattened list
    """

    # We use collections.deque for fast pop(0) / insert(0, v)
    from collections import deque
    my_stack = deque(my_list)
    result = []

    while my_stack:
        elt = my_stack.popleft()
        if isinstance(elt, list):
            my_stack.extendleft(reversed(elt))
        else:
            result.append(elt)

    return result
