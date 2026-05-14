<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron"
        queryBinding="xslt2">

  <title>LER geometri skal være 3D</title>

  <ns prefix="gml" uri="http://www.opengis.net/gml/3.2"/>

  <pattern id="gml-srsdimension-3">

    <!-- Alle GML position lists / positions skal have srsDimension=3,
         enten direkte eller arvet fra nærmeste ancestor med srsDimension. -->
    <rule context="gml:pos | gml:posList">
      <assert test="(ancestor-or-self::*[@srsDimension][1]/@srsDimension) = '3'">
        GML-positionen skal have srsDimension="3" enten direkte eller på nærmeste overordnede geometri-element.
      </assert>
    </rule>

    <!-- Hvis et GML-element overhovedet angiver srsDimension, skal værdien være 3. -->
    <rule context="gml:*[@srsDimension]">
      <assert test="@srsDimension = '3'">
        GML-elementet <name/> har srsDimension="<value-of select="@srsDimension"/>", men værdien skal være "3".
      </assert>
    </rule>

  </pattern>
</schema>
