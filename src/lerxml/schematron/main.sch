<?xml version="1.0" encoding="UTF-8"?>

<schema
    xmlns="http://purl.oclc.org/dsdl/schematron"
    xmlns:sch="http://purl.oclc.org/dsdl/schematron"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    queryBinding="xslt2">

  <title>LER Schematron validation</title>

  <!-- Prefixes used in rule contexts/tests -->
  <ns prefix="ler" uri="http://data.gov.dk/schemas/LER/2/gml"/>
  <ns prefix="gml" uri="http://www.opengis.net/gml/3.2"/>

  <!-- Common abstract rules / shared helpers -->
  <include href="common.sch"/>

  <!-- General rules -->
  <include href="etableringstidspunkt.sch"/>
  <include href="xyz.sch"/>

  <!-- Feature-specific rules, from feature catalog -->
  <include href="Elledning.sch"/>

</schema>
