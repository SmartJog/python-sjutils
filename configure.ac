AC_PREREQ(2.61)

AC_INIT([python-sjutils],[1.15.0])

AM_INIT_AUTOMAKE([foreign])

AM_PATH_PYTHON
AC_PATH_PROG(MSGFMT, msgfmt)

AC_SUBST([sjutilssysconfdir], [\$\(sysconfdir\)/sjutils])
AC_SUBST([sjutilsexecdir], [\$\(pyexecdir\)/sjutils])
AC_SUBST([localesdir], [\$\(datadir\)/sjutils])



AC_CONFIG_FILES([
	Makefile
	sjutils/Makefile
	tests/Makefile
	locale/Makefile
	locale/en/LC_MESSAGES/python-sjutils.po
	locale/fr/LC_MESSAGES/python-sjutils.po
])

AC_OUTPUT
