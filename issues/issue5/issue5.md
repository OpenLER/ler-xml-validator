# expressions in `let` bindings are evaluated in wrong context

## To reproduce

Create `test.xml`:

```xml
<a>
  before
  <b>1234</b>
  after
</a>
```

Create `e.sch`:

```xml
<schema
    xmlns="http://purl.oclc.org/dsdl/schematron"
    queryBinding="xslt2">
<pattern>
  <rule context="b">

    <let name="b_value" value="normalize-space(.)"/>


    <assert id="b1" test="$b_value = '1234'">b must be 1234</assert>
    <assert id="b2" test="normalize-space(.) castable as xs:integer">b must be integer</assert>

    <report id='report1' test="true()">
      value of $b_value: <value-of select="$b_value"/>
    </report>

    <report id='report2' test="true()">
      value of normalize-space(.): <value-of select="normalize-space(.)"/>
    </report>

  </rule>
</pattern>
</schema>
```

Run pyschematron:

```
$ pyschematron test.xml e.sch --svrl-out report.svrl
/home/thlw/a/lerxml/issue5/test.xml INVALID
```

I have picked only the interesting parts from the svrl below:

```xml
  <svrl:failed-assert id="b1" location="/Q{}a[1]/Q{}b[1]" test="$b_value = '1234'">
    <svrl:text>b must be 1234</svrl:text>
  </svrl:failed-assert>
  <svrl:successful-report location="/Q{}a[1]/Q{}b[1]" test="true()">
    <svrl:text>value of $b_value: before 1234 after</svrl:text>
  </svrl:successful-report>
```

The expected result is that b1 and b2 both pass, however b1 failed.

The b1 assertion uses $b_value, which is printed to svrl as a `report` element.

We expect the context node (`.`) to be the `<b>` element, so the result should
be `1234`. But the SVRL shows that it evaluates to `before 1234 after`.

So it seems that the expression in the `let` binding is evaluated in the wrong
context, apparently the parent/root element context instead of the rule context.
