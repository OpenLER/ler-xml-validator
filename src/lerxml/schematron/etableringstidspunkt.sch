<?xml version="1.0" encoding="UTF-8"?>

<pattern
    xmlns="http://purl.oclc.org/dsdl/schematron"
    xmlns:ler="http://data.gov.dk/schemas/LER/2/gml"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    id="etableringstidspunkt-rules">

  <rule context="ler:etableringstidspunkt">

    <let name="v"
         value="normalize-space(.)"/>

    <let name="hasIndeterminate"
         value="exists(@indeterminatePosition)"/>

    <let name="isYear"
        value="matches($v, '^[0-9]{4}$')"/>

    <let name="isYearMonth"
        value="matches($v, '^[0-9]{4}-[0-9]{2}$')"/>

    <let name="isDate"
        value="matches($v, '^[0-9]{4}-[0-9]{2}-[0-9]{2}$')"/>

    <!-- ========================================================== -->
    <!-- Basic format                                                -->
    <!-- ========================================================== -->

    <assert id="LER-ETAB-001"
            test="$isYear or $isYearMonth or $isDate">
      etableringstidspunkt skal angives som YYYY, YYYY-MM eller YYYY-MM-DD.
    </assert>


    <!-- ========================================================== -->
    <!-- indeterminatePosition restrictions                          -->
    <!-- ========================================================== -->

    <assert id="LER-ETAB-002"
            test="not(@indeterminatePosition)
                  or @indeterminatePosition = 'before'">
      indeterminatePosition må kun have værdien "before".
    </assert>


    <!-- ========================================================== -->
    <!-- calendarEraName not allowed                                 -->
    <!-- ========================================================== -->

    <assert id="LER-ETAB-003"
            test="not(@calendarEraName)">
      calendarEraName må ikke anvendes.
    </assert>


    <!-- ========================================================== -->
    <!-- frame restrictions                                          -->
    <!-- ========================================================== -->

    <assert id="LER-ETAB-004"
            test="not(@frame)
                  or @frame = '#ISO-8601'">
      frame må kun have værdien "#ISO-8601".
    </assert>


    <!-- ========================================================== -->
    <!-- YYYY rules                                                  -->
    <!-- ========================================================== -->

    <!-- 2023 requires indeterminatePosition="before" -->

    <assert id="LER-ETAB-005"
            test="not($isYear and $v = '2023')
                  or @indeterminatePosition = 'before'">
      Årstallet 2023 skal anvende indeterminatePosition="before".
    </assert>


    <!-- 2024+ must not use indeterminatePosition -->

    <assert id="LER-ETAB-006"
            test="not($isYear and number($v) ge 2024)
                  or not($hasIndeterminate)">
      Årstal 2024 eller senere må ikke anvende indeterminatePosition.
    </assert>


    <!-- ========================================================== -->
    <!-- YYYY-MM rules                                               -->
    <!-- ========================================================== -->

    <!-- 2023-08+ must not use indeterminatePosition -->

    <assert id="LER-ETAB-007"
            test="not($isYearMonth and $v ge '2023-08')
                  or not($hasIndeterminate)">
      YYYY-MM værdier fra og med 2023-08 må ikke anvende indeterminatePosition.
    </assert>


    <!-- ========================================================== -->
    <!-- YYYY-MM-DD rules                                            -->
    <!-- ========================================================== -->

    <!-- 2023-07-02+ must not use indeterminatePosition -->

    <assert id="LER-ETAB-008"
            test="if ($isDate)
                  then xs:date($v) lt xs:date('2023-07-02')
                      or not($hasIndeterminate)
                  else true()">
      YYYY-MM-DD værdier fra og med 2023-07-02 må ikke anvende indeterminatePosition.
    </assert>

  </rule>

</pattern>
