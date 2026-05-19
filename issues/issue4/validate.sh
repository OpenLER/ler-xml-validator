#!/usr/bin/env bash

# Wrapper around pyschematron
# Runs validation and then prints summary of svrl report

set -euo pipefail

SVRL=".tmp.svrl"

pyschematron --svrl-out "$SVRL" "$@"

python3 - <<'PY'
from lxml import etree

NS = {"svrl": "http://purl.oclc.org/dsdl/svrl"}

tree = etree.parse(".tmp.svrl")

for fa in tree.xpath("//svrl:failed-assert", namespaces=NS):
    print(f'failed-assertion: id={fa.get("id", "")}')
PY
