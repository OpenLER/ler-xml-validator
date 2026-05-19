<schema
    xmlns="http://purl.oclc.org/dsdl/schematron"
    queryBinding="xslt2">
<pattern>
  <rule context="/*">
    <assert id="dummy" test="true()">always true</assert>
  </rule>
</pattern>
</schema>
