<pattern
    xmlns="http://purl.oclc.org/dsdl/schematron"
    id="common-date-rules">

  <!--
    Shared abstract rule for features with etableringstidspunkt
  -->

  <rule abstract="true" id="feature-base">

    <!-- Raw text value -->
    <let name="etab"
         value="normalize-space(ler:etableringstidspunkt)"/>

    <!-- Format helpers -->
    <let name="isYear"
         value="matches($etab, '^\d{4}$')"/>

    <let name="isYearMonth"
         value="matches($etab, '^\d{4}-\d{2}$')"/>

    <let name="isDate"
         value="matches($etab, '^\d{4}-\d{2}-\d{2}$')"/>

    <!--
      True if etableringstidspunkt is after cutoff:
      2023-07-01
    -->

    <let name="afterCutoff"
         value="
           if ($isDate)
           then xs:date($etab) gt xs:date('2023-07-01')

           else if ($isYearMonth)
           then $etab gt '2023-07'

           else if ($isYear)
           then number($etab) gt 2023

           else false()
         "/>

  </rule>

</pattern>
