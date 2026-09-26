# ler-xml-validator

Tjekker, om en XML-fil vil blive accepteret af LER, før den sendes.
Python-bibliotek og CLI (`lerxml`). Understøtter LER 2.0.0, 2.0.1, 2.1.0 og 2.2.0.

## Brug

```bash
pip install -e .
```

De to eksempelfiler er ens, bortset fra etableringstidspunktet (2022 og 2024), og
begge har `noejagtighedsklasse` sat til nil:

```console
$ lerxml validate --version 2.1.0 example_xml/elledning_2022.xml
Gyldig efter LER 2.1.0

$ lerxml validate --version 2.1.0 example_xml/elledning_2024.xml
[ERR] nøjagtighedsklasseVoidrestriktion at /ler:Elledning line 6
Ugyldig efter LER 2.1.0: 1 fejl
```

Hver violation skrives på én linje med `[ERR]` (fejl), `[WRN]` (advarsel) eller `[INF]` (oplysning),
fejlkode, evt. en kort besked og placering. Sidste linje er en opsummering. Exit code er
0, hvis filen er gyldig, og 1, hvis der er fejl. Kommandoerne `xsd`, `xta` og
`geometri` kører kun ét af tjekkene.

Resultatet afhænger af, hvilken LER-version der valideres efter:

| | 2.0.0 | 2.0.1 | 2.1.0 | 2.2.0 |
|---|---|---|---|---|
| `elledning_2022.xml` | gyldig | gyldig | gyldig | `nøjagtighedsklasseVertikalBetingelse` |
| `elledning_2024.xml` | `nøjagtighedsklasseVoidrestriktion` | `nøjagtighedsklasseVoidrestriktion` | `nøjagtighedsklasseVoidrestriktion` | `nøjagtighedsklasseVertikalBetingelse`, `nøjagtighedsklasseVoidrestriktion` |

Nøjagtighedsklassen må ikke være nil, hvis etableringstidspunktet ligger efter
skæringsdatoen (2023-07-01). I 2.2.0 kom `noejagtighedsklasseVertikal` til, og
den mangler i begge filer.

`gfsvar.xml` er et graveforespørgselssvar med tre ledninger og fejl af forskellig
slags: XSD, restriktioner fra featurekataloget og geometri. Den indeholder også en
kommentar, som giver oplysningen `G3`.

```console
$ lerxml validate --version 2.2.0 example_xml/gfsvar.xml
[ERR] XSD: value must be one of ['afløb', 'el', 'fjernvarme/fjernkøling', 'gas', 'olie', 'telekommunikation', 'vand'] at /ler:Graveforespoergselssvar/ler:ledningMember[3]/ler:Foeringsroer/ler:forsyningsart line 91
[ERR] nøjagtighedsklasseVoidrestriktion at /ler:Graveforespoergselssvar/ler:ledningMember[1]/ler:Elledning line 14
[ERR] vejledendeDybdeMåleenhedsrestriktion at /ler:Graveforespoergselssvar/ler:ledningMember[2]/ler:Vandledning line 40
[ERR] GEOM1: Geometrien krydser/rører sig selv at /ler:Graveforespoergselssvar/ler:ledningMember[2]/ler:Vandledning/ler:geometri/gml:LineString/gml:posList line 52
[INF] G3: dokumentet indeholder 1 XML-kommentar (LER har tidligere haft problemer med kommentarer) at /ler:Graveforespoergselssvar/comment() line 12
Ugyldig efter LER 2.2.0: 4 fejl
```

Fra Python:

```python
from lxml import etree
import lerxml

report = lerxml.validate(etree.parse("fil.xml"), "2.2.0")
report.valid       # True/False
report.violations  # liste af Violation(code, message, xpath, line, ...)
```

Versionen skal altid angives. Hvis dokumentets `schemaVersion` ikke passer
med den angivne version, gives advarslen `W1`. Den kommer med i rapporten som
en `Violation` med `severity="warning"`, men gør ikke filen ugyldig, og CLI'en
giver stadig exit code 0. Kun `Graveforespoergselssvar` har `schemaVersion`.

## Hvad bliver tjekket?

| Modul | Tjekker | Fejlkoder |
|---|---|---|
| `xsd.py` | XML Schema for den valgte version | `XSD`, `W1` |
| `xta.py` | Restriktionerne fra featurekataloget, udtrykt i XTA (`src/lerxml/xta/<version>/`) | Restriktionens navn |
| `geometri.py` | Geometrikrav, som ikke let kan udtrykkes i XSD eller XTA | `GEOM1`–`GEOM3` |
| `xlink.py` | At `xmlns:xlink` er deklareret | `G4` (se "Andre krav" i LER-bogen) |
| `kommentarer.py` | Om dokumentet indeholder XML-kommentarer | `G3` (oplysning) |

G1–G4 er beskrevet under "Andre krav" i [LER-bogen](https://openler.github.io/lerbogen/). G3 siger, at
XML-kommentarer ikke er tilladt. LER har tidligere haft problemer med kommentarer, men det er
formentlig rettet, så lerxml melder det kun som en oplysning (`severity="info"`). Den gør ikke
filen ugyldig, men kan være relevant, hvis LER afviser dokumentet af uforklarlige grunde.

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

## Hvorfor en separat validator?

OpenLER har to projekter, der begge handler om gyldig LER-XML:

- **[lermodel](https://github.com/OpenLER/lermodel)** er LERs datamodel i Python.
  Den validerer data og bygger XML ud fra dem.
- **ler-xml-validator** (dette repo) validerer den færdige XML, uanset hvordan
  den er lavet.

Man kunne spørge, hvorfor valideringen ikke bare ligger i lermodel.

Det var svært og uoverskueligt at skrive lermodel korrekt. Så jeg skrev
først validatoren og brugte den til at skrive unit tests til lermodel.
Validatoren er altså facit, og lermodel bliver testet op imod den.

Jeg havde også oplevet, at LER-serveren afviste XML af grunde, der ikke var
dokumenteret som krav, og at fejlbeskederne var uhjælpsomme eller misvisende.
For eksempel accepterede LER-serveren tidligere (måske helt tilbage i 2023)
ikke XML-kommentarer, og fejlbeskeden sagde ikke hvorfor. Jeg tror, LER er
blevet meget bedre siden. Der var brug for en bedre test af XML med bedre
feedback, for at jeg kunne bygge en robust lermodel.

Fordi validatoren kun ser på den færdige XML, kan den også bruges af alle
andre, der sender XML til LER, uanset om de bruger lermodel eller ej.

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

Til gengæld er XTA så simpelt, at det burde være muligt for andre at skrive
deres egen XTA-validator rimeligt let. Med AI er det måske hurtigere end at
sætte en Schematron-validator korrekt op.

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
som et træ. `b` står for branches.

Restriktionstests ligger i `btest/restr/<featuretype>/<restriktion>.yml`. Restriktioner
på abstrakte typer (fx `Ledning`) testes gennem en konkret undertype (fx `Elledning`),
da LERs XSD kun nedarver fra abstrakte typer.

### Kør btest.py

For at køre tests, bare kør `python btest.py`.

## Q & A

### Hvor kommer alle restriktionerne fra?

LER har for hver udgave (2.0.0, 2.0.1 osv.) udgivet en docx-fil med alle
restriktionerne. Mit repo [lerbogen](https://github.com/OpenLER/lerbogen)
parser dem ud af docx-filerne (se [hvorfor docx og ikke en kildefil](https://github.com/OpenLER/lerbogen#hvorfor-parse-docx-og-ikke-en-kildefil))
og gemmer dem i [fkdump](https://github.com/OpenLER/lerbogen/tree/main/fkdump), én YAML-fil pr. featuretype pr. version.

### Hvor kommer XSD-filerne fra?

`src/lerxml/xsd/` er en kopi fra lerbogen: `versions/<version>/schemas/` bliver til
`xsd/<version>/`, og `schemas/http/` og `schemas/https/` (GML, xlink m.fl.) bliver til
`xsd/http/` og `xsd/https/`. Kommer der en ny LER-version, kopieres den derfra.

### Hvad gør build_xta.py?

Den bruges alene til at opdatere filer, der allerede er committed til repo. Så med mindre du udvikler/debugger på dette repo, så er der ingen grund til at køre den. 

Scriptet itererer over alle restriktionerne i `$LERBOGEN_DIR/fkdump/<version>/*.yml`
og laver de tilsvarende XTA-filer, f.eks. `src/lerxml/xta/2.2.0/2.2_restriktioner.yml`.

De genererede XTA-filer må ikke rettes i hånden. Det manuelle arbejde ligger i
de to input-filer:

* `xta/human_to_xpath.yml`: oversætter hver restriktionstekst til XPath
* `xta/variabler.yml`: hjælpevariabler pr. XSD-type, som udtrykkene bruger

Efter en ændring i dem køres `build_xta.py`, og både input og output committes.

Den kigger på restriktionens tekst (human text) og slår det op i human_to_xpath.yml. Rigtigt mange
restriktioner har præcist samme restriktionstekst, og med denne lookup løsning, så
har jeg kunnet nøjes med at skrive én XPath assertion for hvert af disse.
