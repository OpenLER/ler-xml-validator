# ler-xml-validator

Et python library og cli værktøj til at validere den LER XML (LER 2.2).

Der foregår tre former for validering, i følgende rækkefølge:

* XML well formedness
* XML Schema validering ift officielle XSD filer
* Schematron validering, mod .sch filer, som jeg har skrevet til at verificere andre officielle krav, primært fra featurekatalog docx.

## Repo struktur

Selve værktøjet ligger i src/lerxml. Denne Python-kode er relativt simpel. Det har været et større arbejde at skrive selve Schematron, især fordi jeg undervejs har forsøgt at holde det meget pænt og undgå alt for meget duplicate sch kode.

Jeg bruger 

Den mest tidskrævende del har været at skrive de automatiserede tests. Bl.a.
fordi jeg valgte at bruge XQuery Update Facility via xBase.


## Scripts

| Script | Type | Formål | Køres via | Bemærkninger |
|---|---|---|---|---|
| `scripts/build_schematron.py` | Python | Samler `sch:pattern`-fragmenter fra `src/lerxml/schematron/*.sch` til én samlet `2.2_ler.sch` | Manuelt: `python scripts/build_schematron.py` | Kræver at hver input-fil er en gyldig `sch:schema` med `queryBinding="xslt2"`. Fejler pt., da `Elledning.sch` mangler schema-wrapper. |
| `scripts/export_xsd.py` | Python | Henter LER XSD-filerne fra ler.dk og gemmer dem lokalt i `src/lerxml/xsd/` | Manuelt, kun når XSD'erne skal opdateres | Bruger `xmlschema`-biblioteket. |
| `scripts/update_vendor.py` | Python | Henter/opdaterer vendored tredjepartskode i `vendor/` iht. `vendor/vendor.toml` (schematron-schema, schematron-skeleton) | Manuelt | Kræver netværksadgang til GitHub. |
| `scripts/pys.sh` | Bash | Fuld manuel valideringspipeline: resolver `sch:include`, validerer mod RNC/schematron.sch (jing/schxslt), validerer XML mod XSD (jing), validerer mod sch (pyschematron CLI), printer SVRL-opsummering | Manuelt, dev-only | Hardkodede personlige stier (`/home/thlw/a/schema/...`). Kræver `xsltproc`, `jing`, `schxslt`, `pyschematron` CLI og `s2y` installeret lokalt. |
| `run_mutation_tests.py` (repo-rod) | Python | Kører mutation-tests: for hver mutation i `tests/data/*.yml` genererer den XML'en on-the-fly ved at sende XQuery Update Facility-udtrykket til en kørende `basex`-server, og validerer resultatet mod forventede XSD-/Schematron-fejlkoder | Automatisk via `nox -s mutations`/`nox -s report`, eller manuelt `python run_mutation_tests.py [--strict\|--report]` | Kræver en kørende `basexserver -p1984` (startes manuelt, kør én gang og lad den køre mens du arbejder — se nedenfor) samt en lokal `lerxml`-bruger med `CREATE`-rettighed (engangs-opsætning). Bruger `vendor/basexclient/BaseXClient.py` (BaseX's officielle Python-klient) til selve forbindelsen. Ligger bevidst i repo-roden, ikke i `scripts/`, da det er projektets primære test-entrypoint. |

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

## Nox sessions

De fleste opgaver er almindelige scripts (se tabellen ovenfor). Nox bruges kun til de to opgaver, der reelt har brug for et isoleret Python-miljø for at installere og køre `lerxml`-pakken:

| Session | Formål |
|---|---|
| `nox -s mutations` | Kører `run_mutation_tests.py` i subset-mode (default) — fejler hvis forventede fejlkoder mangler. |
| `nox -s report` | Samme som `mutations`, men kører i `--report`-mode: printer en fuld tabel og fejler aldrig. |

