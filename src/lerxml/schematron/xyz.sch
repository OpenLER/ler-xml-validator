<pattern
    xmlns="http://purl.oclc.org/dsdl/schematron"
    id="gml-srsdimension-3">

  <!-- pos/posList skal have en srsDimension direkte eller arvet -->
  <rule context="gml:pos | gml:posList">

    <assert id="XYZ1"
            test="ancestor-or-self::*[@srsDimension]">
      GML-positionen mangler srsDimension direkte eller på nærmeste overordnede geometri-element.
    </assert>

    <assert id="XYZ2"
            test="
              not(ancestor-or-self::*[@srsDimension])
              or
              ancestor-or-self::*[@srsDimension][1]/@srsDimension = '3'
            ">
      GML-positionen skal have srsDimension="3".
    </assert>

  </rule>

  <!-- Alle eksplicit angivne srsDimension-attributter skal være 3 -->
  <rule context="gml:*[@srsDimension]">
    <assert id="XYZ3"
            test="@srsDimension = '3'">
      GML-elementet <name/> har srsDimension="<value-of select="@srsDimension"/>",
      men værdien skal være "3".
    </assert>
  </rule>

</pattern>
