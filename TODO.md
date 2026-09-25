# TODO

## G3: XML-kommentarer

G3 ("XML kommentarer ikke tilladt") er beskrevet under "Andre krav" i
LER-bogen, men er ikke implementeret. Test først mod LERs extest-API,
om kommentarer faktisk afvises. Implementer det derefter som et lille modul
på linje med `xlink.py`.

## srsDimension

Der var tidligere tests (`mut/andre_krav/srsDimension.yml`, slettet sammen
med `mut.py`) for koderne `XYZ1` (manglende `srsDimension`) og `XYZ2`
(`srsDimension` forskellig fra 3). Kravet blev håndhævet af Schematron og
forsvandt, da Schematron blev fjernet. Afklar, om det er et reelt LER-krav,
og implementer det i givet fald i `geometri.py` eller XTA med en btest.
