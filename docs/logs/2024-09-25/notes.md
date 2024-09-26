# Poznámky z 25.9.2024

## Priebeh

- Prešli sme obrázky/návrhy aplikácie
- Pozreli sme sa na otvorené dáta (https://data.gov.cz/, https://data.slovensko.sk/, https://data.europa.eu/sk) a boli mi predstavené "high-value datasety"

## TODOs

- Oprav obrázok... Pridaj k inputom miesto pre vloženie infa o datasete? Príp. niečo viac ak napadne.
- Preskúmaj otvorené dáta (viď stránky vyššie) a vyber zopár datasetov, na ktorých by sa mohol program skúšať (odporúčanie: high-value datasety)
- Vyskúšaj či by to celé fungovalo... Teda:
    1. Skús vykonať data profiling (pom. Pythonu a nejakej knižnice napr.)
    2. Vlož dáta (csv, príp. schemu, data profiling...) do nejakého LLM (napr. ChatGPT)
    3. Skús ho vypromptovať. Zatiaľ vymyslené prompty:

```
ZADANÉ CSV DATA:
- Stručne opíš dáta, povedz čo vyjadrujú, môžeš uviesť z akého prostredia pochádzajú. 
- PRE KAŽDÝ STĹPEC: Napíš mi stručný popis stĺpca (čo opisuje, čo znamená?).
- Napíš mi čo predstavuje riadok tabuľky (čo za entitu, prípadne viacero entít).
- AK CHÝBAJÚ HODNOTY V STĹPCI (nejaký threshold? Alebo stačí >= 1, aby chýbala?): Uveď pravdepodobný dôvod prečo v tomto stĺpci chýbajú hodnoty.
- AK STĹPCE KORELUJÚ: Uveď pravdepodobný dôvod prečo tieto stĺpce spolu korelujú.

ZADANÉ SCHEMA:
- (?) Prečo existuje také obmedzenie/pravidlo?

ZADANÝ USER VIEW/PURPOSE:
- Toto je user view/purpose: 
"{VIEW/PURPOSE}"
Na základe tohto užívateľského pohľadu ďalej odpovedaj na otázky týkajúce sa poskytnutých dát. Ak view/purpose obsahuje otázku alebo z neho vieš vydedukovať odpoveď na užívateľský problém, odpovedz naň. Ináč napíš "NONE".
```
