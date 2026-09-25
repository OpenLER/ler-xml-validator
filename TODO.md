# TODO

## README: indledningen passer ikke med koden

Linje 3–17 i README.md beskriver en ældre version af validatoren:

| README siger | Koden gør |
|---|---|
| "(LER 2.2)" | Understøtter 2.0.0, 2.0.1, 2.1.0 og 2.2.0 (`xsd.VERSIONS`) |
| Læser versionen fra `schemaVersion`, ellers antages 2.2.0 | Versionen skal angives (`--version`/`-V`). `schemaVersion` bruges kun til en advarsel ved uoverensstemmelse |
| XTA-filerne ligger i to mapper, `restr` og `andre_krav` | Én fil pr. version: `src/lerxml/xta/<version>/<v>_restriktioner.yml` |
| XML-kommentarer bliver tjekket | Intet tjek for kommentarer fundet i koden |

README'en mangler også et afsnit om brug (CLI og Python).

Forslag til ny indledning: afsnittene "Brug" (CLI + `lerxml.validate(...)`) og
"Hvad bliver tjekket?" (tabel: `xsd.py` E1, `xta.py` restriktionens navn,
`geometri.py` GEOM1/GEOM2, `xlink.py` G4).

Afklar først:

1. Mangler tjekket for XML-kommentarer, eller ligger det et andet sted?
2. Virker `lerxml validate --version 2.2.0 example_xml/elledning_2024.xml`?
3. Kommentaren i `src/lerxml/xsd.py` siger, at XTA-reglerne "only written
   against 2.2.0's schema so far". Virker XTA for de ældre versioner?
