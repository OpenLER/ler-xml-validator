# silently ignores invalid Schematron

## How to reproduce

### Create files

Create `test.xml`:

```xml
<foo/>
```

Create `a.sch`, a fragment that can be included.

```xml
<pattern
    xmlns="http://purl.oclc.org/dsdl/schematron"
    queryBinding="xslt2">
  <rule context="/*">
    <assert id='rule-a' test="false()">should always fail</assert>
  </rule>
</pattern>
```

Create `b.sch`, like `a.sch` but wrapped in schema.

```xml
<schema
    xmlns="http://purl.oclc.org/dsdl/schematron"
    queryBinding="xslt2">
  <pattern>
    <rule context="/*">
      <assert id='rule-b' test="false()">should always fail</assert>
    </rule>
  </pattern>
</schema>
```

Create `main.sch`:

```xml
<schema xmlns="http://purl.oclc.org/dsdl/schematron" queryBinding="xslt2">
  <include href="a.sch"/>
  <include href="b.sch"/>
</schema>
```

Create `validate.sh`, wrapper around pyschematron:

```
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
```

### Silent fail if using a.sch directly

Expected behavior: print error that this is not a valid schematron schema.

```shell
$ ./validate.sh test.xml a.sch
/home/thlw/a/lerxml/issue4/test.xml VALID
```

### Silent fail if including schema instead of fragment

If the including sch file includes a schematron file which is not
the kind of fragment it expects, then it silently ignores that include. 

However, it does still include and apply the assertions etc. of other
included files.

Expected result: both rule-a and rule-b.

```shell
$ ./validate.sh test.xml main.sch
/home/thlw/a/lerxml/issue4/test.xml INVALID
failed-assertion: id=rule-a
```
