# #!/usr/bin/env bash

# If it prints no errors, and if output is written to $OUTPUT,
# then the 2.2_ler.sch was succesfully resolved and validated
# according to relax ng schema.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

INPUT="$ROOT/src/lerxml/schematron/2.2_ler.sch"
XSLT="$ROOT/vendor/schematron-skeleton/iso_dsdl_include.xsl"
OUTDIR="$ROOT/build/schematron"
OUTPUT="$OUTDIR/2.2_ler_resolved.sch"

mkdir -p "$OUTDIR"

xsltproc \
  --output "$OUTPUT" \
  "$XSLT" \
  "$INPUT"

echo "Wrote $OUTPUT"
