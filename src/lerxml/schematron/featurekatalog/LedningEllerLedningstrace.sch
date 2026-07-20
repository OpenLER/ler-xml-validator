<pattern
    xmlns="http://purl.oclc.org/dsdl/schematron"
    id="ledning-eller-ledningstrace-rules">

  <rule abstract="true" id="ledning-eller-ledningstrace-base">

    <extends rule="feature-base"/>

    <assert id='vejledendeDybdeMåleenhedsrestriktion' test="not(ler:vejledendeDybde) or ler:vejledendeDybde/@uom = 'mm'">
      Måleenheden for den vejledende dybde skal være millimeter.
      Millimeter skal angives med symbolet mm [UCUM].
    </assert>

  </rule>

</pattern>
