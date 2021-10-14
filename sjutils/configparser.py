# -*- coding: utf-8 -*-

import ConfigParser


class OrderedRawConfigParser(ConfigParser.RawConfigParser):
    """RawConfigParser subclass, with an ordered write() method."""

    def write(self, fp):
        """Write an .ini-format representation of the configuration
        state. Sections are written sorted."""
        if self._defaults:
            fp.write("[%s]\n" % ConfigParser.DEFAULTSECT)
            for (key, value) in self._defaults.items():
                fp.write("%s = %s\n" % (key, str(value).replace("\n", "\n\t")))
            fp.write("\n")
        tmp_sections = self._sections.keys()
        tmp_sections.sort()
        for section in tmp_sections:
            fp.write("[%s]\n" % section)
            tmp_keys = self._sections[section].keys()
            tmp_keys.sort()
            for key in tmp_keys:
                if key != "__name__":
                    fp.write(
                        "%s = %s\n"
                        % (key, str(self._sections[section][key]).replace("\n", "\n\t"))
                    )
            fp.write("\n")


class OrderedConfigParser(ConfigParser.ConfigParser, OrderedRawConfigParser):
    """A ConfigParser subclass, with an ordered write() method."""

    def write(self, fp):
        OrderedRawConfigParser.write(self, fp)


class OrderedSafeConfigParser(ConfigParser.SafeConfigParser, OrderedConfigParser):
    """A SafeConfigParser subclass, with an ordered write() method."""

    def write(self, fp):
        OrderedRawConfigParser.write(self, fp)
