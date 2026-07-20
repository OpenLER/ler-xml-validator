<pattern
    xmlns="http://purl.oclc.org/dsdl/schematron"
    id="gml-srsdimension-3-explicit">

  <!-- Alle eksplicit angivne srsDimension-attributter skal være 3 -->
  <rule context="gml:*[@srsDimension]">
    <assert id="XYZ2"
            test="@srsDimension = '3'">
      GML-elementet <name/> har srsDimension="<value-of select="@srsDimension"/>",
      men værdien skal være "3".
    </assert>
  </rule>

</pattern>
