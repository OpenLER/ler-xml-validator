<schema
    xmlns="http://purl.oclc.org/dsdl/schematron"
    queryBinding="xslt2">
  <pattern>
    <rule context="/*">
      <assert test="false()">should always fail</assert>
    </rule>
  </pattern>
</schema>
