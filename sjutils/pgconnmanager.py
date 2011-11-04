# -*- coding: utf-8 -*-

import sys
import logging
import threading

import psycopg2
import psycopg2.extras
from psycopg2.pool import ThreadedConnectionPool


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

        if 'logger' in kwargs:
            logger = kwargs.pop('logger')
        else:
            logger = logging.getLogger('sjutils.pgconnmanager')

        # We can either accept 'database' or 'dbname' as an input
        if db_opts.has_key('database') and not db_opts.has_key('dbname'):
            db_opts['dbname'] = db_opts['database']

        # This is ugly but since dict types cannot be used
        # as keys in another dict, we need to transform it.
        # This transformation was chosen as it is human
        # readable, it could be changed to a more optimised one.
        db_str = "host=%(host)s port=%(port)s user=%(user)s password=%(password)s dbname=%(dbname)s" % db_opts

        if not self._instances.has_key(db_str):
            self._instances[db_str] = super(PgConnManager, self).__new__(self)
            self._instances[db_str].lock = threading.Lock()
            self._instances[db_str].log = logger

        return self._instances[db_str]

    def __init__(self, db_opts):
        self.__params__ = db_opts
        if not hasattr(self, '__conn_pool__'):
            self.__conn_pool__ = None

    def decorate(self, func, *args, **kw):
        try:
            ctx_list = self.connect()
            try:
                try:
                    ret = func(self, ctx_list, *args, **kw)
                except psycopg2.OperationalError, _error:
                    # We got a database disconnection not catched by user, wiping all connection because
                    # psycopg2 does not fill correctly the database connection 'closed' attribute in case of disconnection
                    self.release_all(ctx_list, close=True)
                    raise

                # Connexion(s) wasn't released by user, so we have to release it/them
                self.release_all(ctx_list, rollback=True)

                return ret
            except psycopg2.Error, _error:
                self.release_all(ctx_list, rollback=True)
                raise
            except Exception:
                self.release_all(ctx_list, rollback=True)
                raise
        except psycopg2.Error, _error:
            # We do not want our users to have to 'import psycopg2' to
            # handle the module's underlying database errors
            _, value, traceback = sys.exc_info()
            raise self.DatabaseError, value, traceback

    def _new_ctx(self, mark = None):
        """ Create a new context object. """
        if not mark:
            mark = 'none'
        ret = { 'conn' : None, 'cursor' : None, 'mark': mark }
        ret['conn'] = self.__conn_pool__.getconn()
        self.log.debug('ctx:(' + mark + ', ' + str(id(ret)) + ') Creating context to database: %(dbname)s as %(user)s' % self.__params__)
        return ret

    def connect(self, ctx_list = None, mark = None):
        """ Connect to database. """
        self.log.debug('Connecting to database: %(dbname)s as %(user)s' % self.__params__)
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
            ctx_list.append(self._new_ctx(mark))
            self.log.debug('ctx:(%(mark)s, %(ctxid)s) Connected to database: %(dbname)s as %(user)s' % {
                'mark': ctx_list[-1]['mark'],
                'ctxid': str(id(ctx_list[-1])),
                'dbname': self.__params__['dbname'],
                'user': self.__params__['user'],
            })
            return ctx_list

        except psycopg2.Error, _error:
            # We do not want our users to have to 'import psycopg2' to
            # handle the module's underlying database errors
            _, value, traceback = sys.exc_info()
            raise self.DatabaseError, value, traceback

    def execute(self, ctx, query, options=None):
        """ Execute an SQL query. """
        self.log.debug('ctx:(%(mark)s, %(ctxid)s) Executing query on database: %(dbname)s as %(user)s' % {
            'mark': ctx['mark'],
            'ctxid': str(id(ctx)),
            'dbname': self.__params__['dbname'],
            'user': self.__params__['user'],
        })
        try:
            if not ctx['conn']:
                ctx['conn'] = self.__conn_pool__.getconn()
            if not ctx['cursor']:
                ctx['cursor'] = ctx['conn'].cursor(cursor_factory=psycopg2.extras.DictCursor)
            try:
                if options:
                    ctx['cursor'].execute(query, options)
                else:
                    ctx['cursor'].execute(query)
            except psycopg2.OperationalError, _error:
                # We got a database disconnection, wiping connection
                self.release(ctx, close=True)
                raise
        except psycopg2.Error, _error:
            # We do not want our users to have to 'import psycopg2' to
            # handle the module's underlying database errors
            _, value, traceback = sys.exc_info()
            raise self.DatabaseError, value, traceback

    def commit(self, ctx):
        """ Commit changes to dabatase. """
        self.log.debug('ctx:(%(mark)s, %(ctxid)s) Commiting changes on database: %(dbname)s as %(user)s' % {
            'mark': ctx['mark'],
            'ctxid': str(id(ctx)),
            'dbname': self.__params__['dbname'],
            'user': self.__params__['user'],
        })
        try:
            try:
                ctx['conn'].commit()
            except psycopg2.OperationalError, _error:
                # We got a database disconnection, wiping connection
                self.release(ctx, close=True)
                raise
        except psycopg2.Error, _error:
            # We do not want our users to have to 'import psycopg2' to
            # handle the module's underlying database errors
            _, value, traceback = sys.exc_info()
            raise self.DatabaseError, value, traceback

    def rollback(self, ctx):
        """ Rollback changes to database. """
        self.log.debug('ctx:(%(mark)s, %(ctxid)s) Reverting changes on database: %(dbname)s as %(user)s' % {
            'mark': ctx['mark'],
            'ctxid': str(id(ctx)),
            'dbname': self.__params__['dbname'],
            'user': self.__params__['user'],
        })
        # FIXME: ctx['conn'] is None if execute failed, see bug #3085
        if ctx['conn'] and not ctx['conn'].closed:
            ctx['conn'].rollback()

    def release(self, ctx, rollback=False, close=False):
        """ Release database connection. """
        self.log.debug('ctx:(%(mark)s, %(ctxid)s) Releasing connection on database: %(dbname)s as %(user)s' % {
            'mark': ctx['mark'],
            'ctxid': str(id(ctx)),
            'dbname': self.__params__['dbname'],
            'user': self.__params__['user'],
        })

        if rollback:
            self.rollback(ctx)

        ctx['cursor'] = None
        if ctx['conn']:
            self.log.debug('ctx:(%(mark)s, %(ctxid)s) Disposing connection on database: %(dbname)s as %(user)s' % {
                'mark': ctx['mark'],
                'ctxid': str(id(ctx)),
                'dbname': self.__params__['dbname'],
                'user': self.__params__['user'],
            })
            closeit =  close or (ctx['conn'].closed > 0)
            self.__conn_pool__.putconn(ctx['conn'], close=closeit)
        ctx['conn'] = None

    def release_all(self, ctx_list, rollback=False, close=False):
        """ Release all database connections from a context list. """
        self.log.debug('Releasing ALL connections on database: %(dbname)s as %(user)s' % self.__params__)

        for ctx in ctx_list:
            self.release(ctx, rollback=rollback, close=close)
        ctx_list = None

    def fetchall(self, ctx):
        """ Return all rows of current request. """
        self.log.debug('ctx:(%(mark)s, %(ctxid)s) fetchall on database: %(dbname)s as %(user)s' % {
            'mark': ctx['mark'],
            'ctxid': str(id(ctx)),
            'dbname': self.__params__['dbname'],
            'user': self.__params__['user'],
        })
        return ctx['cursor'].fetchall()

    def fetchmany(self, ctx, arraysize=1000):
        """ Return @arraysize rows of current request. """
        self.log.debug('ctx:(%(mark)s, %(ctxid)s) fetchmany on database: %(dbname)s as %(user)s' % {
            'mark': ctx['mark'],
            'ctxid': str(id(ctx)),
            'dbname': self.__params__['dbname'],
            'user': self.__params__['user'],
        })
        return ctx['cursor'].fetchmany(arraysize)

    def fetchgenerator(self, ctx):
        """ A basic generator to iterate through the current request's
        result rows. """
        self.log.debug('ctx:(%(mark)s, %(ctxid)s) fetchgenerator on database: %(dbname)s as %(user)s' % {
            'mark': ctx['mark'],
            'ctxid': str(id(ctx)),
            'dbname': self.__params__['dbname'],
            'user': self.__params__['user'],
        })
        while True:
            results = self.fetchmany(ctx)
            if not results:
                raise StopIteration
            for result in results:
                yield result

    def get_rowcount(self, ctx):
        """Get the cursor's rowcount attribute of the given context @ctx."""
        return ctx['cursor'].rowcount

    def fetchone(self, ctx):
        """ Return one row of current request. """
        self.log.debug('ctx:(%(mark)s, %(ctxid)s) fetchone on database: %(dbname)s as %(user)s' % {
            'mark': ctx['mark'],
            'ctxid': str(id(ctx)),
            'dbname': self.__params__['dbname'],
            'user': self.__params__['user'],
        })
        return ctx['cursor'].fetchone()
