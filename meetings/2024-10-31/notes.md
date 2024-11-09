# Poznámky z 31.10.2024

## Priebeh

- Prešli sme zápisky (viď dole), resp. ich "konečné zhrnutie" + otázky


## TODOs

- Vytvoriť prompty pre LLM, ktoré vytvára poznámky.
    - Dodatočné info k štruktúre poznámok:
        - Máme informácie o datasete:
            1. Informácie o datasete
                - Čo znamená tabuľka
                - Čo znamenajú jednotlivé stĺpčeky
                - ...
            2. Čo môžem robiť s datasetom, na aké úlohy sa hodí
            3. S čím tie úlohy môžem robiť? (knižnice...)
        - Príklad:
            1. Mám dataset o nejakých miestach, obsahuje ich GPS súradnice.
            2. Môžem ich zobraziť na mape? V barcharte? Má to zmysel?
            3. Pomocou čoho môžem implementovať vizualizáciu na mape?
        - 1\. a 2. spolu silno súvisia, 3. má byť oddelene

- Rozmyslieť či a ako spracúvať viacero datasetov.
- Nájsť lingvistickú metódu na spracovanie hodnôt v textovom stĺpci (hodnoty majú pomôcť zistiť význam stĺpca).
- Pozrieť sa na dátumové typy stĺpcov.
- Zasaď hodnotu korelácie do promptu.
- Skúsiť fixnúť featury diplomky.

---

# Zápisky

- **(OTÁZKA)** Je OK cez argumenty predávať additional info a user view? Lebo na [stránke](https://learn.microsoft.com/en-us/troubleshoot/windows-client/shell-experience/command-line-string-limitation#more-information) píšu že limit je 8191 znakov.
- **(OTÁZKA)** Tie typy OK? Všetky "typy" z [docs](https://docs.profiling.ydata.ai/latest/getting-started/concepts/#data-types). A podľa [ChatGPT](https://chatgpt.com/share/671e6f33-b7ec-8010-ab00-35cfea7781a5).
- Correlations nie sú vždy.
- cmds:
```
python profiling.py -p "datasets\navigator2022.csv" -s ";" -e "ISO-8859-1" -a "Geographical overview of thermal waste treatment facilities

Yearly updated geographical navigator: The geographic navigator presents overall annual information about facilities for the incineration and co-incineration of waste, which are obtained from summary operating records. These are the following: identification number (IČ), name of the facility, address of the operator, address of the facility, putting into operation, types of waste incinerated, nominal capacity, amount of waste incinerated in tonnes per year, number and brief description of incineration lines, enumeration of equipment for reducing emissions, annual emissions of all pollutants reported.

The Czech Hydrometeorological Institute processes and continuously updates the database of equipment for thermal treatment of waste in cooperation with ČIŽP. Pursuant to Article 55 of Directive 2010/75/EU, which regulates access to information and public participation, we are making available a list of all thermal waste treatment facilities." -u "I want to use this dataset to create a software which will visualise on the map where are the facilities for the incineration located and which type of waste can be incinerated there."

```

```
python profiling.py -p "datasets\bevoelkerungsstruktur_2023_bewegung_gesamt.csv" -s "," -e "utf-8" -a "Štruktúra obyvateľstva 2023

Tento súbor údajov obsahuje štatistické údaje o štruktúre obyvateľstva v hanzovom a univerzitnom meste Rostock (obyvateľstvo s hlavným bydliskom v hanzovom a univerzitnom meste Rostock) v roku 2023 podľa oblasti mesta (zdroj: Register obyvateľstva hanzového a univerzitného mesta Rostock). Zdroje o obyvateľstve ako celku, obyvateľstve podľa pohlavia, veku, rodinného stavu a štátnej príslušnosti zahŕňajú údaje o obyvateľstve z 31. 2023 a zdroje o prírodnom, priestorovom a celkovom pohybe obyvateľstva zahŕňajú údaje za celý rok 2023. Zdroje sa zvyčajne neaktualizujú." -u "I would like to use this dataset for visualisation of the population movement."
```

## Testovanie promptov

- Skúsil som [chat s novými promptmi](https://chatgpt.com/share/671e839a-36b8-8010-91d8-886dd32f2b34) (prvýkrát sa skúšajú automaticky vygenerované)... Moje pozorovania:
    1. ~~Treba zmeniť prompty  "Provide a likely explanation for why the column X is correlated with column Y...", pretože potom odpovedá "The column X is likely correlated with Y because...". Kedže už naisto kvôli data profileru vieme, že korelujú, treba povedať "Provide an explanation for why...." (vynechať likely), možno potom aj LLM nebude písať "likely".~~
    2. Ďalšia vec... Prompty ako ten predošlý, ale aj "Provide a brief description..." začínajú "The column X represents/is...". Ak tieto informácie budú v nejakej sekcii daného stĺpca (predstava je, že napr. názov stĺpca bude názov sekcie), takže vieme, že reč je o ňom, tak mi príde zbytočné stále opakovať "Stĺpec X reprezentuje/je...", "Stĺpec X reprezentuje/je..." atď. Ale tak toto možno vyrieši časť kedy sa budú spojovať/prepisovať takéto informačne útržky/fragmenty.
    3. **(OTÁZKA)** Ďalej ma prekvapilo, že prompt "If user view for the dataset is provided..." nefungoval. User view (taký, na ktorý sa dá odpovedať) bol poskytnutý, ale LLM naň neodpovedalo. Ale v predošlých testoch so staršou verziou promptov odpovedalo...
        - Možno sa vtedy využíval lepší model GPT-4o, teraz bol GPT-4o mini. *UPDATE:* Toto fungovalo.
        - Alebo to bolo kvôli tomu, že teraz bol poskytnutý aj čiastočný output z data profileru, možno už bolo príliš veľa dát a na user view zabudol? *UPDATE:* Skúsil som to bez nich a aj tak na user view nezareagoval.
        - Možno by stačilo sa pýtať na user view skôr (momentálne sa naň pýta na konci, idea bola, že na konci toho bude vedieť viac lebo veľa promptov prešlo). *UPDATE:* Toto fungovalo.
        - Možno náhoda a znova keby dáme, tak už odpovie na suer view. *UPDATE:* Skúsil som 2x a rovnaký výsledok, takže asi to nebude náhoda.
    4. ~~**Hlavná vec** je upraviť prompty, resp. vymyslieť formát LLM outputov tak, aby sa dali spracovať a zobrazovať.~~

- Skúsil som [novú verziu promptov](https://chatgpt.com/share/671fc889-e768-8010-98c7-f0ce071ee7c4). Pozorovania:
    1. Problém s "likely" (predošlý bod 1.) už neni.
    2. ~~K predošlému 4. bodu... Instr. prompt je upravený a správy sa píšu vo formáte, ktorý sa dá spracovať. A to tak, že sa pred odpoveďou LLMka pridá prefix. AVŠAK nie vždy sa pridá a to je problém.~~
    3. **(OTÁZKA)** Ak užívateľ požiada LLM, aby pridal niečo do poznámok, LLM ho počúvne, ale neviem či to takto chceme nechať (viď chat). LLM napísalo nejaké info, užívateľ požiadal LLM, aby to dalo do poznámok. LLM síce posluchlo, ale znovu napísalo tú istú správu. Možné riešenia:
        - Dodať napr. \* k prefixu a vtedy sa správa užívateľovi nevypíše.
        - Prepísať instr. prompt komplexnejšie, aby keď vyžiada užívateľ prepisovanie poznámok explicitne, tak aby okrem prefixu a poznámky ešte dodal správu pre užívateľa (napr. "Done" alebo "OK").
    4. ~~**(OTÁZKA)** Prompt "Provide an explanation for why the column X is correlated with the column Y..." končí s tým, že ak LLM nevie, tak má napísať "I have no explanation". Doteraz asi stále (možno okrem úplne prvých pokusov) niečo odpovedalo, prvýkrát teraz napísalo LLM "I have no explanation". Ale my vieme z data profileru že určite korelujú, preto navrhujem~~
        - ~~túto časť úplne vynechať (nech stále niečo napíše)~~
        - ~~alebo nech ak si nie je istý použije slovo "probably" (alebo také niečo). Aby sme stále mali čo zobraziť užívateľovi. Keďže určite korelujú, tak by nemalo LLM napísať úplnú hlúposť... POZOR aj pri missing values to je! (Resp. bolo.)~~

*UPDATE k 2. bodu (a 4.):* 
- [Skúsil som odstrániť Markdown značky z inštrukcií](https://chatgpt.com/share/671fd381-82b4-8010-998e-f8e192aa920e), či to nepomôže a nemohlo... ALE! Všimol som si, že prestane písať prefixy od momentu, keď napíše "I have no explanation". Vyzerá, že túto odpoveď nečakal (podľa instr. promptu mali byť všetky jeho odpovede informácie o datasete, takže asi to aj dáva zmysel, že takú svoju odpoveď nečakal). 
- Skúsil som odstrániť "I have no explanation" (aby to nepísal) a skutočne to pomohlo. Takže sa tým rieši bod 2. a 4., teda bod 2. nie celkom... pretože keď sa mení SYSTEM na USER prompting tak tam znova má napísať nejaké správy bez prefixov a rozbije sa to.

- [Skúsil som opäť ďalšiu verziu promptov](https://chatgpt.com/share/671ff727-ea3c-8010-b588-5404d613ddd3) a podarilo sa sa mi (snáď) definitívne vyriešiť 2. bod.

---

### "Zhrnutie"/Otázky:

- **(OTÁZKA):** Niektoré prompty, napr. "Provide a brief description..." začínajú "The column X represents/is...". Ak tieto informácie budú v nejakej sekcii daného stĺpca (predstava je, že napr. názov stĺpca bude názov sekcie), takže vieme, že reč je o ňom, tak mi príde zbytočné stále opakovať "Stĺpec X reprezentuje/je...", "Stĺpec X reprezentuje/je..." atď. Ale tak toto možno vyrieši časť kedy sa budú spojovať/prepisovať takéto informačne útržky/fragmenty. Mohlo by to riešiť druhé LLM? Kľudne menšie.
- **(OTÁZKA: Ktoré riešenie použiť?)** Ďalej ma prekvapilo, že prompt "If user view for the dataset is provided..." nefungoval. User view (taký, na ktorý sa dá odpovedať) bol poskytnutý, ale LLM naň neodpovedalo. Ale v predošlých testoch so staršou verziou promptov odpovedalo...
    - Možno sa vtedy využíval lepší model GPT-4o, teraz bol GPT-4o mini. *UPDATE:* Toto fungovalo.
    - Alebo to bolo kvôli tomu, že teraz bol poskytnutý aj čiastočný output z data profileru, možno už bolo príliš veľa dát a na user view zabudol? *UPDATE:* Skúsil som to bez nich a aj tak na user view nezareagoval.
    - Možno by stačilo sa pýtať na user view skôr (momentálne sa naň pýta na konci, idea bola, že na konci toho bude vedieť viac lebo veľa promptov prešlo). *UPDATE:* Toto fungovalo.
    - Možno náhoda a znova keby dáme, tak už odpovie na suer view. *UPDATE:* Skúsil som 2x a rovnaký výsledok, takže asi to nebude náhoda.
- **(OTÁZKA?)** Ak užívateľ požiada LLM, aby pridal niečo do poznámok, LLM ho počúvne, ale neviem či to takto chceme nechať (viď chat). LLM napísalo nejaké info, užívateľ požiadal LLM, aby to dalo do poznámok. LLM síce posluchlo, ale znovu napísalo tú istú správu. Možné riešenia:
    - Prepísať instr. prompt nech dodá napr. \* k prefixu a vtedy sa správa užívateľovi nevypíše (Je OK mať správu užívateľa 2x za sebou?).
    - Prepísať instr. prompt komplexnejšie, aby keď vyžiada užívateľ prepisovanie poznámok explicitne, tak aby okrem prefixu a poznámky ešte dodal správu pre užívateľa (napr. "Done" alebo "OK").
- **(OTÁZKA: Vynechal som. Je to OK?)** Prompt "Provide an explanation for why the column X is correlated with the column Y..." končí s tým, že ak LLM nevie, tak má napísať "I have no explanation". Doteraz asi stále (možno okrem úplne prvých pokusov) niečo odpovedalo, prvýkrát teraz napísalo LLM "I have no explanation". Ale my vieme z data profileru že určite korelujú, preto navrhujem
    - túto časť úplne vynechať (nech stále niečo napíše) 
    - alebo nech ak si nie je istý použije slovo "probably" (alebo také niečo). Aby sme stále mali čo zobraziť užívateľovi. Keďže určite korelujú, tak by nemalo LLM napísať úplnú hlúposť... POZOR aj pri missing values to je! (Resp. bolo.) Ak by napísal hlúposť pri missing values, tak užívateľ môže zmazať.


## NOVÝ PRÍSTUP

- [FRAGMENT SPAWNED], [LLM COMMAND], [FOR USER]? + ďalšie LLM (hoc menej parametrové napr. nová Llama3.2)

- **(OTÁZKA)**: Oplatí sa vôbec mať 2 fázy v 1 konverzácii? Keby sme mali jednu, potom vypli a zapli konverzáciu novú a bola by fáza druhá?

- Oukej, [vyskúšal som nový prístup](https://chatgpt.com/share/672018a6-2ac4-8010-92f8-4d61330245b7) a zdá sa mi že funguje super. Teda možno až na ten koniec, ale myslím si, že keď trošku upravím inštrukcie tak to bude OK. V podstate aj toto ako je by mohlo fungovať. (Keď som mu povedal, že nechcem mať info v poznámkach, tak nedal cmd a keď som mu explicitne povedal, aby zmazal, tak dal cmd, ale bez textu pre užívateľa. Takže asi lemn postačí lepšie opísať čo za editovanie môže robiť (pridávať, mazať, prepisovať) + explicitne povedať, že nestačí napísať cmd, ale ku každému cmd musí poskytnúť aj text pre užívateľa)

- [Ďalšia verzia promptov](https://chatgpt.com/share/67226ccc-0604-8010-85a2-c9a346a85a99). Zdá sa, že LLM:
    - lepšie rozlišuje kedy má pridať LLM CMD na editáciu
    - dôraz na to, aby písal správu aj pre užívateľa, nie len LLM CMD
    - FRAGMENT tag sa pridáva len na začiatku (počas vývoja promptov sa objavil problém s tým, ale už vyriešené)
    - znovu sa objavil problém s tým, že FRAGMENT tag sa prestal pridávať (vyriešené, "no other text" asi robil problém)
    - **(OTÁZKA)** Viď koniec konverzácie, FRAGMENT tag pridal aj na knižnice. To už je asi príliš, či? Alebo aj také informácie sa majú pridávať?

---

### "Zhrnutie"/Otázky:

- **(OTÁZKA)** Je OK cez argumenty predávať additional info a user view? Lebo na [stránke](https://learn.microsoft.com/en-us/troubleshoot/windows-client/shell-experience/command-line-string-limitation#more-information) píšu že limit je 8191 znakov.
- **(OTÁZKA)** Tie typy OK? Všetky "typy" z [docs](https://docs.profiling.ydata.ai/latest/getting-started/concepts/#data-types). A podľa [ChatGPT](https://chatgpt.com/share/671e6f33-b7ec-8010-ab00-35cfea7781a5).
- **(OTÁZKA):** Niektoré prompty, napr. "Provide a brief description..." začínajú "The column X represents/is...". Ak tieto informácie budú v nejakej sekcii daného stĺpca (predstava je, že napr. názov stĺpca bude názov sekcie), takže vieme, že reč je o ňom, tak mi príde zbytočné stále opakovať "Stĺpec X reprezentuje/je...", "Stĺpec X reprezentuje/je..." atď. Ale tak toto možno vyrieši časť kedy sa budú spojovať/prepisovať takéto informačne útržky/fragmenty. Mohlo by to riešiť druhé LLM? Kľudne menšie.
- **(OTÁZKA: Vynechal som. Je to OK?)** Prompt "Provide an explanation for why the column X is correlated with the column Y..." končí s tým, že ak LLM nevie, tak má napísať "I have no explanation". Doteraz asi stále (možno okrem úplne prvých pokusov) niečo odpovedalo, prvýkrát teraz napísalo LLM "I have no explanation". Ale my vieme z data profileru že určite korelujú, preto navrhujem
    - túto časť úplne vynechať (nech stále niečo napíše) 
    - alebo nech ak si nie je istý použije slovo "probably" (alebo také niečo). Aby sme stále mali čo zobraziť užívateľovi. Keďže určite korelujú, tak by nemalo LLM napísať úplnú hlúposť... POZOR aj pri missing values to je! (Resp. bolo.) Ak by napísal hlúposť pri missing values, tak užívateľ môže zmazať.
- **(OTÁZKA)** Viď koniec konverzácie, FRAGMENT tag pridal aj na knižnice. To už je asi príliš, či? Alebo aj také informácie sa majú pridávať?
- **(OTÁZKA)**: Oplatí sa vôbec mať 2 fázy v 1 konverzácii? Keby sme mali jednu, potom vypli a zapli konverzáciu novú a bola by fáza druhá?
