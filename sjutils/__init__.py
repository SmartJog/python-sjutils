# -*- coding: utf-8 -*-
# FIXME: clean this up as modules are ported to using submodules directly

from sjutils.defaultdict import DefaultDict

from sjutils.logger2 import Logger2

try:
    from logging import LoggerAdapter
except ImportError:
    from sjutils.loggeradapter import LoggerAdapter

from sjutils.pgconnmanager import (
    PgConnManager,
    PgConnProxy,
    manage_pgconn,
    manage_pgconn_conf,
)

import sjutils.threadpool

from sjutils.utils import (
    pretty_size,
    html_entity_fixer,
    html_escape,
    any,
    all,
    flatten_dict,
    flatten_list,
)
