<?xml version="1.0" encoding="UTF-8"?>
<sch:schema
    xmlns:sch="http://purl.oclc.org/dsdl/schematron"
    xmlns:ler="http://data.gov.dk/schemas/LER/2/gml"
    xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

  <sch:ns prefix="ler" uri="http://data.gov.dk/schemas/LER/2/gml"/>
  <sch:ns prefix="gml" uri="http://www.opengis.net/gml/3.2"/>
  <sch:ns prefix="xsi" uri="http://www.w3.org/2001/XMLSchema-instance"/>

  <sch:pattern id="Elledning">

    <sch:rule context="ler:Elledning">

      <sch:let name="afterCutoff"
               value="number(translate(substring(ler:etableringstidspunkt, 1, 10), '-', '')) &gt; 20230701"/>

      <!-- NB: simpel XPath 1.0-tilnærmelse: finder -99 som token i geometrien -->
      <sch:let name="hasUnknownZ"
               value=".//ler:geometri//*[contains(concat(' ', normalize-space(.), ' '), ' -99 ')]"/>

      <sch:assert id="spændingsniveauMåleenhedsrestriktion"
                  test="not(ler:spaendingsniveau[not(@uom = 'kV')])">
        Måleenheden for spændingsniveauet skal være kV.
      </sch:assert>

      <sch:assert id="udvendigDiameterBetingelse"
                  test="not($afterCutoff) or ler:udvendigDiameter">
        Den udvendige diameter skal være angivet hvis etableringstidspunktet er efter skæringsdatoen.
      </sch:assert>

      <sch:assert id="vejledendeDybdeBetingelse"
                  test="not($afterCutoff and $hasUnknownZ) or ler:vejledendeDybde">
        Den vejledende dybde skal være angivet hvis etableringstidspunktet er efter skæringsdatoen
        og de vertikale koordinater i geometrien er ukendt-værdien -99.
      </sch:assert>

      <sch:assert id="vejledendeDybdeVoidrestriktion"
                  test="
                    not(
                      $afterCutoff
                      and ler:ejerskabsforhold = 'ejet af udleverende ledningsejer'
                      and not(ler:driftsstatus = 'under etablering')
                      and $hasUnknownZ
                      and ler:vejledendeDybde/@xsi:nil = 'true'
                    )
                  ">
        Den vejledende dybde må ikke være void hvis betingelserne er opfyldt.
      </sch:assert>

    </sch:rule>

  </sch:pattern>

</sch:schema>