<pattern xmlns="http://purl.oclc.org/dsdl/schematron"
         id="always-fail">
  <rule id='foo' context="/">
    <assert id='bar' test="not(//comment())">XML must not contain comments.</assert>
  </rule>
</pattern>
