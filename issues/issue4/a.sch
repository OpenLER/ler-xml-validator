<pattern
    xmlns="http://purl.oclc.org/dsdl/schematron"
    queryBinding="xslt2">
  <rule context="/*">
    <assert id='rule-a' test="false()">should always fail</assert>
  </rule>
</pattern>
