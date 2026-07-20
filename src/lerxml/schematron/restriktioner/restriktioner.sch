<?xml version="1.0" encoding="UTF-8"?>

<schema
    xmlns="http://purl.oclc.org/dsdl/schematron"
    xmlns:sch="http://purl.oclc.org/dsdl/schematron"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    queryBinding="xslt2">

  <title>LER Schematron validation — restriktioner fra featurekatalogets docx</title>

  <!-- Prefixes used in rule contexts/tests -->
  <ns prefix="ler" uri="http://data.gov.dk/schemas/LER/2/gml"/>
  <ns prefix="gml" uri="http://www.opengis.net/gml/3.2"/>
  <ns prefix="xsi" uri="http://www.w3.org/2001/XMLSchema-instance"/>
  <ns prefix="xlink" uri="http://www.w3.org/1999/xlink"/>

  <include href="feature_base.sch"/>
  <include href="LedningEllerLedningstrace.sch"/>
  <include href="Ledning.sch"/>
  <include href="Elledning.sch"/>
</schema>
