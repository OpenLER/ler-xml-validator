Der er 26 feature types, heraf 22 konkrete og 4 abstrakte.

Der er 81 restriktioner. 

Heraf 46 unikt navngivne restriktioner. 

Hvis man grupperer efter både navne og expression, så er der 59 unikke restriktioner.

Alle restriktioner er defineret for et givet feature type (evt abstract).

XSD tillader at nedarve fra konkrete typer, men det forekommer ikke
i LER's XSD 2.2. Dvs. restriktionerne for en given abstrakt feature kan
kun testes ved at instantiere et element af en konkret xsd type, som
er child type af førnævnte.

Den bedste måde overordnet at sørge for at dække alle restriktioner må
være at have en mappe/fil fokuseret på at teste den restriktion. 

Lad os først tænke på alle dem, der ikke har 