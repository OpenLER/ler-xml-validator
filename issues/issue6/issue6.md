# If svrl contains succesful-report then 

### To reproduce

Create `test.xml`:

```xml
<foo/>
```

Create `e1.sch`:

```xml
<schema
    xmlns="http://purl.oclc.org/dsdl/schematron"
    queryBinding="xslt2">
<pattern>
  <rule context="/*">

    <assert id="dummy" test="true()">always true</assert>

  </rule>
</pattern>
</schema>
```

Create `e2.sch`, same as e1.sch but with report:

```xml
<schema
    xmlns="http://purl.oclc.org/dsdl/schematron"
    queryBinding="xslt2">
<pattern>
  <rule context="/*">

    <report test="true()">
      hello world
    </report>

    <assert id="dummy" test="true()">always true</assert>

  </rule>
</pattern>
</schema>
```

Run them:

```
$ pyschematron test.xml e1.sch --svrl-out report1.svrl
/home/thlw/a/lerxml/issue6/test.xml VALID
$ pyschematron test.xml e2.sch --svrl-out report2.svrl
/home/thlw/a/lerxml/issue6/test.xml INVALID

We expect them both to be VALID, but e2.sch gives INVALID,
probably because the report2.svrl contains a
successful-report element.

```
$ diff report1.svrl report2.svrl
9c9
<     <dct:created>2026-05-19T21:31:31.643319+02:00</dct:created>
---
>     <dct:created>2026-05-19T21:31:35.649253+02:00</dct:created>
17c17
<         <dct:created>2026-05-19T21:31:31.643319+02:00</dct:created>
---
>         <dct:created>2026-05-19T21:31:35.649253+02:00</dct:created>
22a23,25
>   <svrl:successful-report location="/Q{}foo[1]" test="true()">
>     <svrl:text>hello world</svrl:text>
>   </svrl:successful-report>
```
