#!/usr/bin/env bash

# E.g.:
# $ sax.sh test.xml main.sch

# Helper script, used while developing. 
# Helps compare saxon/schxslt versus pyschematron behavior.

set -euo pipefail

#export SCH_TO_XSL=~/a/schxslt/core/target/xslt-only/2.0/compile-for-svrl.xsl
export PIPELINE=~/a/schxslt/core/target/xslt-only/2.0/pipeline-for-svrl.xsl

if [ $# -ne 2 ]; then
    echo "Usage: $0 file.xml file.sch"
    exit 1
fi

XML="$1"
SCH="$2"

schxslt \
  -d "$XML" \
  -s "$SCH" \
  -o out.svrl

xmlstarlet sel \
  -N svrl="http://purl.oclc.org/dsdl/svrl" \
  -t -m "//svrl:failed-assert" \
  -o "FAIL " \
  -v "@id" \
  -o " " \
  -v "@location" \
  -o "  " \
  -v "normalize-space(svrl:text)" -n \
  out.svrl
