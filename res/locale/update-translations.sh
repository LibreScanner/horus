#/bin/sh
xgettext --language=Python \
	--copyright-holder='bq' \
	--package-name=Horus \
	--package-version=0.2 \
	--msgid-bugs-address=jesus.arroyo@bq.com \
	--keyword=_ \
	--output=horus.pot \
	--from-code=UTF-8 \
	`find ../../src/horus -name "*.py"`

for LANG in `ls .`; do
	if [ -e $LANG/LC_MESSAGES/horus.po ]; then
		msgmerge -U $LANG/LC_MESSAGES/horus.po horus.pot
		msgfmt $LANG/LC_MESSAGES/horus.po --output-file $LANG/LC_MESSAGES/horus.mo
	fi
done
