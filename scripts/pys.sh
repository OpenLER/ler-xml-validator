#!/usr/bin/env bash
set -euo pipefail

XML="$1"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

SCH="$ROOT/src/lerxml/schematron/2.2_ler.sch"
RESOLVE_INCLUDES="$ROOT/vendor/schematron-skeleton/iso_dsdl_include.xsl"

OUTDIR="$ROOT/build"
RESOLVED="$OUTDIR/2.2_ler_resolved.sch"
SVRL=".tmp.svrl"

SCH_RNC=/home/thlw/a/schema/schematron.rnc
SVRL_RNC=/home/thlw/a/schema/svrl.rnc

SCH_SCH=/home/thlw/a/schema/schematron.sch
SVRL_SCH=/home/thlw/a/schema/svrl.sch

LER_XSD=$ROOT/src/lerxml/xsd/2.2_ler.xsd


## STEP 0:
## Pre-flight checks

mkdir -p "$OUTDIR"
[ -f "$XML" ] || { echo "XML not found: $XML" >&2; exit 2; }
[ -f "$SCH" ] || { echo "SCH not found: $SCH" >&2; exit 2; }


## STEP 1:
## Resolve sch:include and write resolved schematron to $RESOLVED

xsltproc \
  --output "$RESOLVED" \
  "$RESOLVE_INCLUDES" \
  "$SCH"

## STEP 2:
## Validate $RESOLVED against the Relax NG schema (($SCH_RNC))

jing -c "$SCH_RNC" "$RESOLVED"


## STEP 3:
## Validate $RESOLVED against the schematron ($SCH_SCH)

schxslt \
  -d "$RESOLVED" \
  -s "$SCH_SCH" \
  -o ".validation_of_sch.sch" #\
  > /dev/null


## STEP 4:
## Validate $XML against 2.2_ler.xsd

echo "[Validating XML against XSD using jing]"
jing "$LER_XSD" "$XML"
 
# echo "[Validating XML against XSD using Python's xmlschema]"
# xmlschema-validate -v --schema "$LER_XSD" "$XML"


## STEP 5:
## Run pyschematron cli

echo "[Validating XML against sch using pyschematron]"
pyschematron "$XML" "$RESOLVED" --svrl-out "$SVRL"


## STEP 6:
## Print summary of SVRL

s2y "$SVRL"
