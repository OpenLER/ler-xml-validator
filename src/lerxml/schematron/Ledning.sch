<?xml version="1.0" encoding="UTF-8"?>
<sch:schema
    xmlns:sch="http://purl.oclc.org/dsdl/schematron"
    xmlns:ler="http://data.gov.dk/schemas/LER/2/gml"
    xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

  <sch:ns prefix="ler" uri="http://data.gov.dk/schemas/LER/2/gml"/>
  <sch:ns prefix="gml" uri="http://www.opengis.net/gml/3.2"/>
  <sch:ns prefix="xsi" uri="http://www.w3.org/2001/XMLSchema-instance"/>

  <sch:pattern id="Ledning">

    <sch:rule context="ler:Ledning">

      <sch:let name="afterCutoff"
        value="number(translate(substring(ler:etableringstidspunkt, 1, 10), '-', '')) &gt; 20230701"/>

      <sch:let name="ownedByDeliveringOwner"
        value="ler:ejerskabsforhold = 'ejet af udleverende ledningsejer' or not(ler:ejerskabsforhold)"/>

      <sch:let name="hasGeometry"
        value="ler:geometri/*"/>

      <sch:let name="containedInTrace"
        value="ancestor::ler:Ledningstrace or ancestor::*[ler:indeholdtLedning]"/>

      <sch:let name="containedInOtherLedning"
        value="ler:liggerILedning = 'true'"/>

      <sch:assert id="driftsstatusVoidrestriktion"
        test="not($afterCutoff) or not(ler:driftsstatus/@xsi:nil = 'true')">
        Driftsstatussen må ikke være void hvis etableringstidspunktet er efter skæringsdatoen.
      </sch:assert>

      <sch:assert id="fareklasseVoidrestriktion"
        test="not($afterCutoff) or not(ler:fareklasse/@xsi:nil = 'true')">
        Fareklassen må ikke være void hvis etableringstidspunktet er efter skæringsdatoen.
      </sch:assert>

      <sch:assert id="geometriBetingelse"
        test="$containedInTrace or $containedInOtherLedning or ler:geometri">
        Geometrien skal være angivet hvis ledningen ikke er indeholdt i et ledningstracé
        og ikke er indeholdt i en anden ledning.
      </sch:assert>

      <sch:assert id="geometriDatatypeRestriktion"
        test="
          not($hasGeometry)
          or ler:geometri/gml:LineString
          or ler:geometri/gml:Curve[
            gml:segments/gml:LineStringSegment
            and not(gml:segments/*[not(self::gml:LineStringSegment)])
          ]
        ">
        Geometrien skal anvende lineær interpolation.
      </sch:assert>

      <sch:assert id="nøjagtighedsklasseBetingelse"
        test="($hasGeometry and ler:noejagtighedsklasse) or (not($hasGeometry) and not(ler:noejagtighedsklasse))">
        Nøjagtighedsklassen for den horisontale placering skal være angivet hvis geometrien er angivet,
        og må ikke være angivet hvis geometrien ikke er angivet.
      </sch:assert>

      <sch:assert id="nøjagtighedsklasseVertikalBetingelse"
        test="($hasGeometry and ler:noejagtighedsklasseVertikal) or (not($hasGeometry) and not(ler:noejagtighedsklasseVertikal))">
        Nøjagtighedsklassen for den vertikale placering skal være angivet hvis geometrien er angivet,
        og må ikke være angivet hvis geometrien ikke er angivet.
      </sch:assert>

      <sch:assert id="nøjagtighedsklasseVoidrestriktion"
        test="not($afterCutoff and $ownedByDeliveringOwner) or not(ler:noejagtighedsklasse/@xsi:nil = 'true')">
        Nøjagtighedsklassen for den horisontale placering må ikke være void.
      </sch:assert>

      <sch:assert id="nøjagtighedsklasseVertikalVoidrestriktion"
        test="not($afterCutoff and $ownedByDeliveringOwner) or not(ler:noejagtighedsklasseVertikal/@xsi:nil = 'true')">
        Nøjagtighedsklassen for den vertikale placering må ikke være void.
      </sch:assert>

      <sch:assert id="udvendigDiameterMåleenhedsrestriktion"
        test="not(ler:udvendigDiameter) or ler:udvendigDiameter/@uom = 'mm'">
        Måleenheden for den udvendige diameter skal være mm.
      </sch:assert>

      <sch:assert id="udvendigDiameterVoidrestriktion"
        test="
          not(
            $afterCutoff
            and $ownedByDeliveringOwner
            and not(ler:driftsstatus = 'under etablering')
          )
          or not(ler:udvendigDiameter/@xsi:nil = 'true')
        ">
        Den udvendige diameter må ikke være void hvis betingelserne er opfyldt.
      </sch:assert>

    </sch:rule>

  </sch:pattern>

</sch:schema>
