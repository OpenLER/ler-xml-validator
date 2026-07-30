# 901: Rapport-format og API når lerxml bruges som dependency

## Status

Vedtaget (endnu ikke implementeret).

## Kontekst

lerxml skal snart bruges som dependency i clay
(se `https://github.com/OpenLER/clay/adr/913_lerxml-anvendelse.md`).

clay har brug for at kunne kalde lerxml og få en rapport, enten som json
eller som json-agtigt, der let kan serialiseres til json, og gemmes i en
jsonblob i databasen.

## Krav til rapporten

1. Hvilken LER-version, der blev valideret imod.
2. Metadata om lerxml (fx pakkens version eller commit)
3. En liste af violations. Hver violation skal minimum indeholde en kode og en besked, og
   bør derudover indeholde lokation (xpath) og linjenummer, når det er tilgængeligt.
4. Violations skal kunne være enten errors eller warnings. Kun errors produceres i dag, men
   modellen men vi vil have en model, som kan rumme warnings i fremtiden, uden breaking changes
5. Rapporten skal kunne serialiseres til et format, der passer direkte ind i clay's
   `jsonb`-kolonne, uden en omvej.

## Beslutning 1 - Rapporten er et Python-objekt; JSON er referenceformatet ved serialisering

lerxml's offentlige API returnerer et `Report`-objekt (dataclass)

`Report` har en `to_dict()`-metode, som bruges når rapporten skal ud af Python,
til clay's `jsonb`-kolonne, til en fil, eller til CLI-output.

CLI'et kan fortsat printe et menneskelæsbart format (som i dag), men det er en separat
formattering af `Report`, ikke rapportens kanoniske form.

## Beslutning 2 - `ValidationError` omdøbes til `Violation`, får et `severity`-felt

```python
severity: Literal["error", "warning"] = "error"
```

De eksisterende felter bevares uændrede. Alle nuværende producenter (`xsd.py`, `xta.py`,
`schematron.py`, `geometri.py`) sætter ikke `severity` eksplicit, de falder tilbage til
default `"error"`, hvilket er korrekt adfærd i dag, da ingen af dem endnu kan producere
warnings.

## Beslutning 3 - `Report`-dataclass

```python
@dataclass
class Report:
    ler_version: str
    lerxml_version: str
    violations: list[Violation]

    @property
    def valid(self) -> bool:
        return not any(v.severity == "error" for v in self.violations)

    def to_dict(self) -> dict:
        ...
```

`lerxml_version` udfyldes automatisk (`importlib.metadata.version("lerxml")`), så kaldere
ikke selv skal slå det op. 

## Beslutning 4 - validate_file, validate_string og validate rettes til at returnere Report

I dag returnerer de en iterator.
