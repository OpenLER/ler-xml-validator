It seems that `pyschematron` does not handle comments outside the root `<schema>` element correctly.

Furthermore, instead of reporting an error, it appears to silently continue with no active rules, causing validation to always return `VALID`.

I have noticed this silent failing in other situations too, with faulty schematron xml as far as I remember. Is that intentional?

### How to reproduce:

Create `e1.sch` which fail on every xml document:

```xml
<schema
    xmlns="http://purl.oclc.org/dsdl/schematron"
    queryBinding="xslt2">
  <!-- comment inside root element -->
  <pattern>
    <rule context="/*">
      <assert test="false()">should always fail</assert>
    </rule>
  </pattern>
</schema>
```

Create `e2.sch`, same as e1.sch, but comment added outside root element:

```xml
<schema
    xmlns="http://purl.oclc.org/dsdl/schematron"
    queryBinding="xslt2">
  <!-- comment inside root element -->
  <pattern>
    <rule context="/*">
      <assert test="false()">should always fail</assert>
    </rule>
  </pattern>
</schema>
<!-- comment outside root element -->
```

Create `test.xml`:

```xml
<foo/>
```

Run pyschematron cli for e1.sch, expected: INVALID:

```shell
$ pyschematron test.xml e1.sch --svrl-out report1.svrl 
/home/thlw/a/lerxml/issue3/test.xml INVALID
```

Run pyschematron cli for e2.sch, expected: INVALID:

```shell
$ pyschematron test.xml e2.sch --svrl-out report2.svrl
/home/thlw/a/lerxml/issue3/test.xml VALID
```

See gist for svrl files:

https://gist.github.com/velle/b84c14af6bde7216d39049c509fc9878