# Kendte begrænsninger i pyschematron

## `role`-attributten på `assert`/`report` viderekommer ikke til SVRL

ISO Schematron understøtter et `role`-attribut på `<assert>`/`<report>` (fx `role="warning"`), til at markere at en given regel er mindre alvorlig end en almindelig fejl.

`pyschematron` (version 1.1.16+issue16fix, den version brugt i dette projekt) viderefører **ikke** `role`-attributten til sit SVRL-output. Testet direkte:

```xml
<assert id="test1" role="warning" test="false()">a warning</assert>
```

giver dette i SVRL, uden nogen `role`-attribut:

```xml
<svrl:failed-assert id="test1" location="..." test="false()">
  <svrl:text>a warning</svrl:text>
</svrl:failed-assert>
```

**Konsekvens:** `lerxml/schematron.py` (som udelukkende læser `id`, `svrl:text` og `location` fra SVRL'en) kan ikke se `role`-attributten. En regel markeret `role="warning"` i `.sch`-kilden opfører sig derfor i praksis identisk med en almindelig fejl — der er ingen indbygget måde at differentiere alvorlighedsgrad på i dette projekts nuværende opsætning.

**Hvis dette bliver relevant senere:** for at bruge `role` reelt, skal man selv slå attributten op direkte i `.sch`-kilden (ikke i SVRL'en) og matche den på `id`, når resultaterne fra `validate()` behandles — `pyschematron` gør det ikke for en.
