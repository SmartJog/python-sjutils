AC_PREREQ(2.61)

AC_INIT([python-sjutils],[1.12.0~dev])

AM_INIT_AUTOMAKE([foreign])

AM_PATH_PYTHON
AC_PATH_PROG(MSGFMT, msgfmt)

AC_SUBST([sjutilssysconfdir], [\$\(sysconfdir\)/sjutils])
AC_SUBST([sjutilsexecdir], [\$\(pyexecdir\)/sjutils])


AC_CONFIG_FILES([
	Makefile
	sjutils/Makefile
])

AC_OUTPUT
