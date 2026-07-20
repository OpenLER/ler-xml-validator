<pattern
    xmlns="http://purl.oclc.org/dsdl/schematron"
    id="elledning-rules">

  <rule context="ler:Elledning">

    <let name="zValues"
         value="
           for $pl in ler:geometri//gml:posList
           return tokenize(normalize-space($pl), '\s+')[position() mod 3 = 0]
         "/>

    <let name="verticalUnknown"
        value="exists($zValues) and (every $z in $zValues satisfies $z = '-99')"/>

    <extends rule="ledning-base"/>

    <assert id='spændingsniveauMåleenhedsrestriktion' test="not(ler:spaendingsniveau) or ler:spaendingsniveau/@uom = 'kV'">
      Måleenheden for spændingsniveauet skal være kilovolt.
      Kilovolt skal angives med symbolet kV [UCUM].
    </assert>

    <assert id='udvendigDiameterBetingelse' test="
      not($afterCutoff)
      or
      (
        ler:udvendigDiameter
        and not(ler:udvendigDiameter/@xsi:nil = 'true')
        and normalize-space(ler:udvendigDiameter) != ''
      )
    ">
      udvendigDiameterBetingelse:
      Den udvendige diameter skal være angivet hvis etableringstidspunktet er efter skæringsdatoen.
    </assert>

    <assert id='vejledendeDybdeBetingelse' test="
      not($afterCutoff and $verticalUnknown)
      or
      (
        ler:vejledendeDybde
        and not(ler:vejledendeDybde/@xsi:nil = 'true')
        and normalize-space(ler:vejledendeDybde) != ''
      )
    ">
      vejledendeDybdeBetingelse:
      Den vejledende dybde skal være angivet hvis etableringstidspunktet er efter skæringsdatoen
      og de vertikale koordinater i geometrien er ukendt-værdien -99.
    </assert>

    <assert id='vejledendeDybdeVoidrestriktion' test="
      not(
        $afterCutoff
        and (not(ler:ejerskabsforhold) or normalize-space(ler:ejerskabsforhold) = 'ejet af udleverende ledningsejer')
        and normalize-space(ler:driftsstatus) != 'under etablering'
        and $verticalUnknown
      )
      or
      not(ler:vejledendeDybde/@xsi:nil = 'true')
    ">
      vejledendeDybdeVoidrestriktion:
      Den vejledende dybde må ikke være void/nil hvis etableringstidspunktet er efter skæringsdatoen,
      ejerskabsforholdet er ejet af udleverende ledningsejer,
      driftsstatussen ikke er under etablering,
      og de vertikale koordinater i geometrien er ukendt-værdien -99.
    </assert>

  </rule>

</pattern>
