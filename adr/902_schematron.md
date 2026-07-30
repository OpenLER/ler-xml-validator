# Schematron - Not using anymore

Jeg har tidligere forsøgt at implementere alt forretningslogik i schematron,
som er designet netop til dette formål. 

Men jeg oplevede følgende:

- det var komplekst/tungt at skrive
- det var komplekst/tungt at læse/overskue/forstå
- det var svært at skrive, så det var elegant/pænt, jeg havde generelt en følelse af at have skrevet noget grimt bras
- jeg blev flere gang undervejs overrasket over, 
  hvordan schematron faktisk fungerede, det opførte sig generelt ikke sådan
  som jeg syntes var intuitivt, formentligt fordi det er et koncept der er
  designet til at kunne implementeres som xslt. Hver gang måtte
  jeg revidere min forståelse og mit design.
- schematron har ikke den udbredelse, som man kunne ønske sig,
  dog ikke ringere udbredelse/support end alle andre xml-værktøjer.
  XML-økosystem føles generelt som sick-old-man imo
- pyschematron var det eneste værktøj, der var værd at bruge i min
  situation
- pyschematron er designet og implementeret dygtigt/grundigt
- pyschematron er ikke battle-testet, og der er aspekter af schematron,
  som slet ikke er implementeret
- pyschematron maintainer
  var helt ekstraordinær hurtig/behjælpeligt ift at svare på issues og få fikset bugs,
  formentligt ville han også rette flere af manglerne, hvis man rapporterede
- der er aspekter af schematron, som stadigt forekommer ulogiske/mærkelige for mig,
  enten fordi jeg ikke har fuldt forstået schematron, fordi jeg ikke har forstået
  hvordan konceptet med at man skal kunne oversætte det til xslt lægger en masse benspænd,
  men _måske_ også fordi det bare ikke er tænkt helt igennem
- iso schematron standarden koster penge. Der er mange resourcer gratis eller billigt tilgængeligt,
  men jeg har brugt en hel del tid på at tænke over, hvad jeg rent faktisk ved, og hvad jeg
  blot troede, at jeg vidste
- hvis jeg skulle implementere i schematron, så skulle det nærmest udelukkende være fordi,
  at disse filer så også kunne køres/evalueres af andre, og i andre miljøer.
  Hvis der er problemer med, at nogen ting måske opfører sig anderledes under andre
  omstændigheder, så er hele denne gevinst nærmest tabt på gulvet

## Indførte i stedet *xta*

Til allersidst besluttede jeg mig for at skrive mit eget valideringskoncept,
med assertions. Det hedder xta, for XML Schema Type-based Assertions. Her kan
man definere assertions, og knytte disse til specifikke XSD-typer.

Da jeg skiftede til xta, så forsvandt frustrationen, og arbejdet skred frem.
Det var uden tvivl den rigtige beslutning.

xta er så simpel i struktur, at man relativt let ville kunne implementere
det i andre sprog.
