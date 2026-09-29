# 904 - Fejlet XSD stopper al videre tjek

Featurekatalogets restriktioner (xta) springes allerede over ved XSD-fejl,
fordi deres udtryk forudsætter XSD'ens struktur.

Andre krav (G1, G3 …) køres derimod altid, også ved XSD-fejl.
Det er ikke besluttet nogen steder, det er bare blevet sådan.

## Fordele ved at køre andre krav på trods af XSD-fejl

- Rapporten bliver mere komplet: man ser fx G4 sammen med XSD-fejlene,
  i stedet for først i næste runde.

## Imod

- Rapporten bliver alligevel aldrig komplet, xta mangler jo. Og G4 er
  ikke vigtigere at se med det samme end en vilkårlig xta-regel.
- Hvert krav skal have defensiv kode for dokumenter, XSD'en ville have
  afvist (posList med ikke-tal, srsDimension der ikke er et heltal …).
- Det er svært at forklare/dokumentere, at nogle fejl vises på trods af XSD-fejl,
  mens andre ikke gør.

## Nogle tjek bør måske netop køre før XSD

G8 tjekker, at dokumentets `schemaVersion` passer med den version, man
validerer efter.

Har man valgt en forkert version (fx forkert angivet i CLI'en), så vil det ofte betyde, at XSD fejler,
XSD. Hvis tjekket stopper ved XSD,
så får brugeren aldrig vist G8 (som er forklaringen/hint)

Argumenterne imod ovenfor gælder heller ikke for G8: den læser kun én
attribut på rodelementet og kræver ingen defensiv kode.

## Mulig struktur

- pre_check (vist nok kun G8)
- XSD
- XTA
- andre_krav

## Evt omdøbning af G8

Måske skulle G8 omdøbes til P1 (P for precheck).

Jeg har i øvrigt også overvejet at omdøbe de andre G til A, for "andre check".
Og i samme forbindelse tildele nye tal, så tallene har en struktur.

## Foreløbig beslutning

Jeg hælder meget til at vedtage ovenstående struktur. Jeg er mere i tvivl omdøbning.
Men jeg udsætter den endelige beslutning, fordi jeg alligevel ikke har tid til
at arbejde mere på det lige nu.
