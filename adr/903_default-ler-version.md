# 903 - Skal der være en default LER-version?

I øjeblikket defaulter den til nyeste registrerede version.
Det gælder for alle funktionskald, der tager et version argument.
E.g.:

    validate(doc: _ElementTree, version: str = xsd.DEFAULT_VERSION)

Men det er egentligt lidt risky, der er måske noget client kode,
der virker nu, men breaker når en ny LER-version udgives.

Så jeg vil fjerne default.

## Hvorfor ikke bare afgøre version ud fra schemaVersion

En graveforespørgsel har XML, der starter cirka sådan her:

```xml
<ler:Graveforespoergselssvar
    xmlns:ler="http://data.gov.dk/schemas/LER/2/gml"
    xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    gml:id="gsvar-001"
    schemaVersion="2.2">
```

Og schema version kan aflæses fra attributten schemaVersion.

Og langt de fleste gange, hvor vi kalder validate,
så vil xml indeholde denne.

Men jeg har faktisk hele tiden været bevidst om, at jeg også
vil have muligheden for at kalde den med brudstykker, fx
xml for en enkelt feature. Og de har jo ikke nogen angivelse
af schemaVersion.

## Schema version bruger X.Y, ikke X.Y.Z

Well... Normalt så betyder det sidste Z et fix, ikke
ændring i regler eller design. Og det må ikke give breaking changes.

Men så vidt jeg husker, så er der faktisk netop meget stor forskel
på 2.0.0 og 2.0.1. Anyway, jeg tror roligt vi kan antage, at vi altid
skal bruge 2.0.1, hvis schemaVersion=2.0.

## Beslutning 1 - Funktioner skal ikke have en default for version

So be it.

## Beslutning 2 - De nuværende validate funktioner skal smide warning, hvis schemaVersion ikke matcher 

Hvis man kalder validate(gfsvar_xml, '2.2.0'), men xml indeholder en schemaVersion=2.1.0,
så skal den smide en warning.

## Beslutning 3 - CLI

Indtil videre skal man også angive version i CLI. Mandatory.

For at holde det konsistent.
