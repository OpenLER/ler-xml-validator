<schema
    xmlns="http://purl.oclc.org/dsdl/schematron"
    queryBinding="xslt2">
<pattern>
  <rule context="b">

    <let name="b_value" value="normalize-space(.)"/>


    <assert id="b1" test="$b_value = '1234'">b must be 1234</assert>
    <assert id="b2" test="normalize-space(.) castable as xs:integer">b must be integer</assert>


  </rule>
</pattern>
</schema>
