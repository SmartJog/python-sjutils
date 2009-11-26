nobase_locales_DATA = \
	en/LC_MESSAGES/python-sjutils.mo \
	fr/LC_MESSAGES/python-sjutils.mo

SUFFIXES: .po

.po.mo:
	-@localebuildir=`echo $@ | sed 's:\(.*/\).*:\1:'` \
	  && test ! -d "$$localebuildir" && $(MKDIR_P) $$localebuildir
	$(MSGFMT) --check-format -o $@ $<

EXTRA_DIST = en fr
CLEANFILES = $(nobase_locales_DATA)
