<pattern
    xmlns="http://purl.oclc.org/dsdl/schematron"
    id="ledning-rules">

  <rule abstract="true" id="ledning-base">

    <extends rule="ledning-eller-ledningstrace-base"/>

    <let name="ownRef" value="concat('#', @gml:id)"/>

    <assert id='driftsstatusVoidrestriktion' test="not($afterCutoff) or not(ler:driftsstatus/@xsi:nil = 'true')">
      driftsstatusVoidrestriktion:
      Driftsstatussen må ikke være void hvis etableringstidspunktet er efter skæringsdatoen.
    </assert>

    <assert id='fareklasseVoidrestriktion' test="not($afterCutoff) or not(ler:fareklasse/@xsi:nil = 'true')">
      fareklasseVoidrestriktion:
      Fareklassen må ikke være void hvis etableringstidspunktet er efter skæringsdatoen.
    </assert>

    <!--
      NOTE: not fully verified — relies on document-wide xlink:href reverse
      lookups (a ledning references the ledninger/ledningstraceer it contains,
      not the other way around). Please review.
    -->
    <assert id='geometriBetingelse' test="
      exists(//ler:Ledningstrace/ler:indeholdtLedning[@xlink:href = $ownRef])
      or exists(//ler:Ledning/ler:indeholdtLedning[@xlink:href = $ownRef])
      or (ler:geometri and not(ler:geometri/@xsi:nil = 'true'))
    ">
      geometriBetingelse:
      Geometrien skal være angivet hvis ledningen ikke er indeholdt i et ledningstracé
      og ikke er indeholdt i en anden ledning.
    </assert>

    <!--
      NOTE: not fully verified — assumes gml:Curve's segments are directly
      gml:LineStringSegment elements. Please review against real GML samples.
    -->
    <assert id='geometriDatatyperestriktion' test="
      not(ler:geometri)
      or ler:geometri/gml:LineString
      or (ler:geometri/gml:Curve and not(ler:geometri/gml:Curve/gml:segments/*[not(local-name() = 'LineStringSegment')]))
    ">
      geometriDatatyperestriktion:
      Geometrien skal anvende lineær interpolation: gml:LineString,
      eller gml:Curve med segmenter udelukkende af typen gml:LineStringSegment.
    </assert>

    <assert id='nøjagtighedsklasseBetingelse' test="
      (ler:geometri and ler:noejagtighedsklasse)
      or (not(ler:geometri) and not(ler:noejagtighedsklasse))
    ">
      nøjagtighedsklasseBetingelse:
      Nøjagtighedsklassen for den horisontale placering skal være angivet hvis geometrien er angivet,
      og må ikke være angivet hvis geometrien ikke er angivet.
    </assert>

    <assert id='nøjagtighedsklasseVertikalBetingelse' test="
      (ler:geometri and ler:noejagtighedsklasseVertikal)
      or (not(ler:geometri) and not(ler:noejagtighedsklasseVertikal))
    ">
      nøjagtighedsklasseVertikalBetingelse:
      Nøjagtighedsklassen for den vertikale placering skal være angivet hvis geometrien er angivet,
      og må ikke være angivet hvis geometrien ikke er angivet.
    </assert>

    <assert id='nøjagtighedsklasseVertikalVoidrestriktion' test="
      not(
        $afterCutoff
        and (not(ler:ejerskabsforhold) or normalize-space(ler:ejerskabsforhold) = 'ejet af udleverende ledningsejer')
      )
      or not(ler:noejagtighedsklasseVertikal/@xsi:nil = 'true')
    ">
      nøjagtighedsklasseVertikalVoidrestriktion:
      Nøjagtighedsklassen for den vertikale placering må ikke være void hvis etableringstidspunktet
      er efter skæringsdatoen og ejerskabsforholdet er ejet af udleverende ledningsejer.
    </assert>

    <assert id='nøjagtighedsklasseVoidrestriktion' test="
      not(
        $afterCutoff
        and (not(ler:ejerskabsforhold) or normalize-space(ler:ejerskabsforhold) = 'ejet af udleverende ledningsejer')
      )
      or not(ler:noejagtighedsklasse/@xsi:nil = 'true')
    ">
      nøjagtighedsklasseVoidrestriktion:
      Nøjagtighedsklassen for den horisontale placering må ikke være void hvis etableringstidspunktet
      er efter skæringsdatoen og ejerskabsforholdet er ejet af udleverende ledningsejer.
    </assert>

    <assert id='udvendigDiameterMåleenhedsrestriktion' test="not(ler:udvendigDiameter) or ler:udvendigDiameter/@uom = 'mm'">
      udvendigDiameterMåleenhedsrestriktion:
      Måleenheden for den udvendige diameter skal være millimeter.
      Millimeter skal angives med symbolet mm [UCUM].
    </assert>

    <assert id='udvendigDiameterVoidrestriktion' test="
      not(
        $afterCutoff
        and (not(ler:ejerskabsforhold) or normalize-space(ler:ejerskabsforhold) = 'ejet af udleverende ledningsejer')
        and normalize-space(ler:driftsstatus) != 'under etablering'
      )
      or not(ler:udvendigDiameter/@xsi:nil = 'true')
    ">
      udvendigDiameterVoidrestriktion:
      Den udvendige diameter må ikke være void hvis etableringstidspunktet er efter skæringsdatoen,
      ejerskabsforholdet er ejet af udleverende ledningsejer,
      og driftsstatussen ikke er under etablering.
    </assert>

  </rule>

</pattern>
