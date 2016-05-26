#!/bin/bash

# Clean _build dir
[ -d "_build" ] && rm -r _build

make gettext

LANGUAGES=""
for var in "$@"
do
    LANGUAGES="$LANGUAGES -l $var "
done

sphinx-intl update -p _build/locale $LANGUAGES
