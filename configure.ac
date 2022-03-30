AC_PREREQ(2.67)

AC_INIT([python-sjutils],[2.0.1~dev])

AM_INIT_AUTOMAKE([foreign])

AM_PATH_PYTHON([3])
AC_PATH_PROG(MSGFMT, msgfmt)

AC_SUBST([sjutilssysconfdir], [\$\(sysconfdir\)/sjutils])
AC_SUBST([sjutilsexecdir], [\$\(pyexecdir\)/sjutils])
AC_SUBST([localesdir], [\$\(datadir\)/sjutils])



AC_CONFIG_FILES([
	Makefile
	sjutils/Makefile
	tests/Makefile
	locale/Makefile
	locale/en/LC_MESSAGES/python3-sjutils.po
	locale/fr/LC_MESSAGES/python3-sjutils.po
])

AC_OUTPUT
