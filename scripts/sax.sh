#!/usr/bin/env bash

# E.g.:
# $ sax.sh test.xml main.sch

# Helper script, used while developing. 
# Helps compare saxon/schxslt versus pyschematron behavior.

set -euo pipefail

export SCH_TO_XSL=~/a/schxslt/core/target/xslt-only/2.0/compile-for-svrl.xsl

if [ $# -ne 2 ]; then
    echo "Usage: $0 file.xml file.sch"
    exit 1
fi

XML="$1"
SCH="$2"

saxon \
  -xsl:"$SCH_TO_XSL" \
  -s:"$SCH" \
  -o:main.xsl

saxon \
  -xsl:main.xsl \
  -s:"$XML" \
  -o:report.svrl
