<sch:schema
    queryBinding="xslt2"
    xmlns:sch="http://purl.oclc.org/dsdl/schematron"
    xmlns:ler="http://data.gov.dk/schemas/LER/2/gml"
    xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:xs="http://www.w3.org/2001/XMLSchema">

  <sch:ns prefix="ler" uri="http://data.gov.dk/schemas/LER/2/gml"/>
  <sch:ns prefix="gml" uri="http://www.opengis.net/gml/3.2"/>
  <sch:ns prefix="xsi" uri="http://www.w3.org/2001/XMLSchema-instance"/>
  <sch:ns prefix="xs" uri="http://www.w3.org/2001/XMLSchema"/>

  <sch:pattern id="Elledning">

    <sch:rule context="ler:Elledning">

      <sch:let name="etableringsdato"
              value="
                if (substring(string(ler:etableringstidspunkt), 1, 10) castable as xs:date)
                then xs:date(substring(string(ler:etableringstidspunkt), 1, 10))
                else xs:date('0001-01-01')
              "/>

      <sch:let name="afterCutoff"
              value="$etableringsdato gt xs:date('2023-07-01')"/>


      <sch:let name="is2D"
              value="exists(.//ler:geometri//*[@srsDimension = '2'])"/>

      <sch:let name="hasMinus99"
                value="
                  some $n in tokenize(
                    normalize-space(string-join(.//ler:geometri//*[self::gml:pos or self::gml:posList]/text(), ' ')),
                    '\s+'
                  )
                  satisfies $n = '-99'
                "/>

      <sch:let name="hasUnknownZ"
              value="$is2D or $hasMinus99"/>

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