<pattern
    xmlns="http://purl.oclc.org/dsdl/schematron"
    id="no-xml-comments">

  <!-- LER-server afviser XML der indeholder kommentarer -->
  <rule context="comment()">
    <assert id="G3"
            test="false()">
      XML-kommentarer er ikke tilladt.
    </assert>
  </rule>

</pattern>
