<pattern
    xmlns="http://purl.oclc.org/dsdl/schematron"
    id="gml-srsdimension-3-pos">

  <!-- pos/posList skal have en srsDimension direkte eller arvet -->
  <rule context="gml:pos | gml:posList">

    <assert id="XYZ1"
            test="ancestor-or-self::*[@srsDimension]">
      GML-positionen mangler srsDimension direkte eller på nærmeste overordnede geometri-element.
    </assert>

  </rule>

</pattern>
