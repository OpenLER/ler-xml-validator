<schema
    xmlns="http://purl.oclc.org/dsdl/schematron"
    queryBinding="xslt2">
<pattern>
  <rule context="/*">

    <report test="false()">
      hello world
    </report>

    <assert id="dummy" test="true()">always true</assert>

  </rule>
</pattern>
</schema>
