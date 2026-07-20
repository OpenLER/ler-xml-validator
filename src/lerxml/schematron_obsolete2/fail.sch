<pattern xmlns="http://purl.oclc.org/dsdl/schematron"
         id="always-fail">

  <rule context="/">
    <assert test="false()">
      FAIL
    </assert>
  </rule>

</pattern>
