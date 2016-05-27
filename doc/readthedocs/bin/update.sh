#!/bin/bash

make clean gettext

LANGUAGES=""
for var in "$@"
do
    LANGUAGES="$LANGUAGES -l $var "
done

sphinx-intl update -p _build/locale $LANGUAGES
