# -*- coding: utf-8 -*-

import os
import bz2
import gzip
import codecs

from logging.handlers import BaseRotatingHandler

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

