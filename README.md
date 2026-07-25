# ler-xml-validator

Et python library og cli værktøj til at validere den LER XML (LER 2.2).

Der foregår flere former for validering, i følgende rækkefølge:

* lerxml parser XML, kaster evt fejl, hvis det ikke er wellformed
* læser LER formatet fra schemaVersion (kan evt overrides, her antager vi '2.2.0')
* kører et antal moduler, der hver gennemfører validering
  * xsd.py, kører XSD evaluering med XSD filerne fra `xsd/2.2.0/`, evt fejl returneres med koden E1
  * xta.py, kører validering af et custom XTA format, hvor man udtrykker assertions for hver enkelt XSD type.
    Den leder rekursivt efter xta filer i mappen xta/2.2.0 og evaluerer dem alle. Hver assertion har sin egen kode, og message. XTA filerne
    er organiseret i to mapper:
    * `restr`, alle de officielle *restriktioner* som defineret i de officielle featurekatalog docx filer
    * `andre_krav`, andre krav, herunder også krav, som jeg tror ikke officielt er dokumenteret, men som jeg har konstateret (fx. er xml-kommentarer ikke tilladt) 
  * geometri.py, krav til geometri, som ikke let kunne udtrykkes i xsd eller xta

## Coverage

Der er publiceret fire forskellige udgaver af LER-specifikationen. Hver af disse *publikationer*
består af et antal XSD filer og en docx fil kaldt featurekatalog med *restriktioner*.

Jeg har implementeret samtlige 301 restriktioner (dog er mange af dem identiske, og der er kun 76 unikke restriktioner).

Jeg har dog kun testet et lille antal, for v. 2.2.0, primært omkr Elledning og Føringsrør.

```
2.0.0               68
2.0.1               75
2.1.0               77
2.2.0               81
----------------------
                   301
```

## Hvorfor XTA?

XML Schema er beregnet til at validere den grundlæggende struktur. Schematron er designet
til at udtrykke den form for assertions, der ligger ud over XML Schema. Jeg forsøgte først
at implementere alle kravene (både de officielle restriktioner og andre krav) som Schematron,
men endte med at give op.

Det var meget tungt/omstændigt at skrive, men det største problem var, at det var svært at
skrive, så det havde en pæn/overskuelig struktur.

Til sidst indførte jeg mit eget format, XTA, for *XML Schema Type-based assertions*, hvor
man angiver assertions for hver XML Schema type.

Formatet er yml, og meget simpelt at gennemskue/overskue.

Største/eneste ulempe ved at have droppet Schematron er, at hvis det var lykkedes at skrive
reglerne i Schematron, så kunne disse også evalueres i andre miljøer; altså det ville
ikke være nødvendigt at installere noget Python-bibliotek, som i princippet kunne indeholde
sikkerhedsproblemer eller bugs / problemer med vedligehold.

## Automatiserede tests

Jeg har kun skrevet tests til et fåtal af koderne. Jeg har struktuereret det således,
at testmiljøet kun benytter et lille antal xml-filer. Hvor hver test laves der
én eller flere manipulationer på denne XML, og så tjekkes, om man får de forventede koder.

Disse manipulationer udtrykkes i XQuery Update Facility (XQUF), som dog desværre kun
findes i én open source implementation, basex. BaseX er lavet i Java, og er tungt at
starte op. Løsningen blev at man starter en lokal basex server, som løbende udfører
XQUF arbejdet.

### Opsætning af basex-server (engangs + daglig)

Engangs-opsætning af en lav-privilegie-bruger (kræver ikke en kørende server):
```
basex -c "CREATE USER lerxml lerxml"
basex -c "GRANT CREATE TO lerxml"
```
`CREATE` er den laveste rettighed der tillader `doc()` og XQuery Update-udtryk mod vilkårlige filer — `ADMIN` er ikke nødvendigt.

Hver gang du sætter dig til at arbejde, start serveren og lad den køre:
```
basexserver -p1984
```
Og når du er færdig:
```
basexserver stop
```

### btest filer

Jeg har indført et yml format, som beskriver hvilken xml fil, der skal loades,
hvordan dette dokument skal manipuleres, og hvilke validerings koder,
det bør give. Det er en rekursiv struktur, og derfor er printout også formet
som et træ.

### Kør btest.py

For at køre tests, bare kør `python btest.py`.

## Q & A

### Hvor kommer alle restriktionerne fra?

LER.dk har for hver udgave (altså 2.0.0, 2.0.1, etc.) udgivet en ny docx-fil,
der indeholder alle disse restriktioner (og en masse andet). Filen er tydeligvis
maskingenereret, ud fra en eller anden masterfil. Et oplagt bud er en XMI-fil.
Jeg har skrevet til LER og spurgt efter en sådan fil, men fik blot svar om,
at de ikke havde en sådan fil, og henviste til XSD.

Derfor har jeg bygget et værktøj, der kunne extracte data fra docx-filerne.
Dette værktøj er en del af mit featurekatalog repo ([link](https://github.com/OpenLER/featurekatalog)).

Restriktionerne kan kan findes i yaml-filer i mappen constraints ([link](https://github.com/OpenLER/featurekatalog/tree/main/constraints)).

Den statiske hjemmeside viser også forskellige informationer omkr strukturen;
denne information kommer fra XSD-filerne.
