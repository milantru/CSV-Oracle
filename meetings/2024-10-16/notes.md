# Poznámky z 16.10.2024

## Priebeh

Prešli sme moje poznámky:

# Datasety

1. Geografický prehľad zariadení na tepelné spracovanie odpadu:
    - Český dataset
    - Každoročne aktualizovaný
    - Napr. by sme mohli chcieť vytvoriť appku, ktorá by zisťovala, či niekto nespaľuje "na čierno"? (Že roky 2021, 2022 tam je spaľovňa, potom 2023 nie, a potom zase 2024 tam je) *ALEBO* Aplikáciu, ktorá zobrazí kde sú tieto zariadenia a na aký odpad.
    - Link: https://data.europa.eu/data/datasets/https-geoportal-gov-cz-php-micka-record-turtle-6638b406-4214-4ccb-9cf5-2a0376c0a8017c?locale=sk

2. Štruktúra obyvateľstva 2023:
    - Nemecký dataset
    - Môžeme skúsiť, či zvládneme aj keď po nemecky sú stĺpce?
    - Napr. možeme chcieť vytvoriť appku na vizualizáciu prechodu/presunu obyvatelstva?
    - Link: https://data.europa.eu/data/datasets/2b388393-97b7-482e-b7f8-c57953b5fcf0?locale=sk

# Prompty

## 0. Prvotné inštrukcie

```
Instructions:
- You are an assistant for the software engineers.
- Your job is to help the software engineers to understand the data they provide and assess its suitability for their project needs.
- In the next message you will receive an input in this format:
Dataset schema:
"""
{Dataset schema}
"""

First rows of the dataset:
"""
{First rows of the dataset}
""" 

Last rows of the dataset:
"""
{Last rows of the dataset}
"""

Additional info about the dataset:
"""
{Additional info about the dataset}
"""

User view for this dataset:
"""
{User view for this dataset}
"""

Output from the data profiling of the dataset:
"""
{Output from the data profiling of the dataset}
"""

- Some parts of the input are optional and might be left out.
- After receiving the mentioned input, you may analyze it. Afterwards you will be prompted by premade system prompts (not user prompts) to answer questions about the dataset. Your answers will be processed and displayed to the user.
- You will be notified when the premade system prompts end and the user prompts will begin by message "PREMADE SYSTEM PROMPTS HAS ENDED, USER PROMPTS START NOW". After that you will be speaking to the user and you will answer user's questions regarding the dataset and the user's view (if provided).
- It is expected that the dataset does not belong to the user and thus the language of the dataset may differ from the language of the user.
- It is expected that the user speaks English. Because of that you will answer question about the dataset in English.
- If you understand your job, just type OK.
```

## 1. Vloženie inputu v požadovanom formáte (príklad)

```
First rows of the dataset:
"""
IC;S42_X;S42_Y;ICP;NAZEV;POZN;NAZEV_P;ULICE_P;OBEC_P;NAZEV_Z;ULICE_Z;OBEC_Z;ROK;DAL;DRUHY;KAPACITA (t/rok);ODPAD;LINEK;LINKY;PLYNY;ZL1;MJ1;MNO1;ZL2;MJ2;MNO2;ZL3;MJ3;MNO3;ZL4;MJ4;MNO4;ZL5;MJ5;MNO5;ZL6;MJ6;MNO6;ZL7;MJ7;MNO7;ZL8;MJ8;MNO8;ZL9;MJ9;MNO9;ZL10;MJ10;MNO10;ZL11;MJ11;MNO11;ZL12;MJ12;MNO12;ZL13;MJ13;MNO13;ZL14;MJ14;MNO14;ZL15;MJ15;MNO15;ZL16;MJ16;MNO16;ZL17;MJ17;MNO17;ZL18;MJ18;MNO18;ZL19;MJ19;MNO19;ZL20;MJ20;MNO20;ZL21;MJ21;MNO21;ZL22;MJ22;MNO22;ZL23;MJ23;MNO23;ZL24;MJ24;MNO24;ZL25;MJ25;MNO25;ZL26;MJ26;MNO26
27253236;3476995;5517233;602190081;Nemocnice Rudolfa a Stefanie Bene�ov, a.s., nemocnice St�edo�esk�ho kraje � Kotelna a spalovna;;Nemocnice Rudolfa a Stefanie Bene�ov, a.s., nemocnice St�edo�esk�ho kraje;M�chova 400;25601 Bene�ov;Nemocnice Rudolfa a Stefanie Bene�ov, a.s., nemocnice St�edo�esk�ho kraje � Kotelna a spalovna;M�chova 400;25601 Bene�ov;2001;2004 � instalace technologie na z�chyt PCDD/F, 2009 � rekonstrukce syst�mu na �i�t�n� spalin;nemocni�n� a zdravotnick� odpady;1000;806;1;spalovna PL-10-200;such� vyp�rka spalin (adsorpce), tkaninov� ruk�vcov� filtr, dioxinov� filtr s aktivn�m koksem, alkalick� vyp�rka spalin;TZL;t/rok;0,059;SO2;t/rok;0,204;NOx;t/rok;3,662;CO;t/rok;0,449;C;t/rok;0,11;Sb;kg/rok;0,003;As;kg/rok;0,013;Cd;kg/rok;0,003;Cr;kg/rok;0,043;Hg;kg/rok;0,442;Co;kg/rok;0,003;Mn;kg/rok;0,066;Cu;kg/rok;0,021;Ni;kg/rok;0,025;Pb;kg/rok;0,016;V;kg/rok;0,007;Tl;kg/rok;0,002;F;kg/rok;9,4;Cl;kg/rok;58,7;PCDD+PCDF;mg/rok;0,27;;;;;;;;;;;;;;;;;;
45274649;3413864;5605943;604340041;�EZ, a.s. ? Elektr�rna Ledvice;Zm�nou integrovan�ho povolen� �. 27 ze dne 31. 10. 2022 byla povolena spalovac� zkou�ka kal� z likvidace odpadn�ch vod spolu s hn�d�m uhl�m. Emise poch�zej� p�ev�n� ze spalov�n� uhl�.;�EZ, a.s.;Duhov� 1444;14000 Praha 4;�EZ, a.s. ? Elektr�rna Ledvice;Osada 141;41801 B�lina;2022;;kaly z likvidace odpadn�ch vod ( 19 08 14 ? kaly z jin�ch zp�sob� �i�t�n� pr�myslov�ch odpadn�ch vod neuveden� pod ��slem 19 08 13);70;15;1;blok B4 s fluidn�m kotlem;such� ods��en� pomoc� v�pence ve fluidn�m lo�i, elektrostatick� odlu�ova�;TZL;t/rok;23,258;SO2;t/rok;630,381;NOx;t/rok;522,117;CO;t/rok;25,36;Sb;kg/rok;2,624;As;kg/rok;64,29;Cd;kg/rok;3,936;Cr;kg/rok;83,315;Hg;kg/rok;20,337;Co;kg/rok;36,767;Mn;kg/rok;1036,515;Cu;kg/rok;28,865;Ni;kg/rok;43,297;Pb;kg/rok;36,737;V;kg/rok;27,553;Zn;kg/rok;176,47;Tl;kg/rok;24,929;F;kg/rok;276,841;Cl;kg/rok;1280,063;PCDD+PCDF;mg/rok;50,251;;;;;;;;;;;;;;;;;;
60713470;3621505;5452525;611110451;SAKO Brno, a.s. � divize 3 ZEVO;;SAKO Brno, a.s.;Jedovnick� 4247;62800 Brno;SAKO Brno, a.s. � divize 3 ZEVO;Jedovnick� 4247;62800 Brno;1989;1994 � spu�t�n� 2. stupn� �i�t�n� spalin, 2004 � SNCR, 2009�2010 � rekonstrukce za��zen�;sm�sn� komun�ln� odpad;248000;242532;2;spalovensk� kotle K2 a K3 (syst�m D�sseldorf);nekatalytick� redukce oxid� dus�ku n�st�ikem roztoku mo�oviny, aktivn� uhl�, absorpce plyn� v�pennou vyp�rkou, textiln� filtr s vl�knitou vrstvou;TZL;t/rok;0,326;SO2;t/rok;39,962;NOx;t/rok;307,607;CO;t/rok;8,6;C;t/rok;1,239;NH3;t/rok;1,547;Sb;kg/rok;0,653;As;kg/rok;0,331;Cd;kg/rok;0,057;Cr;kg/rok;1,785;Hg;kg/rok;0,41;Co;kg/rok;0,021;Mn;kg/rok;0,651;Cu;kg/rok;6,616;Ni;kg/rok;1,246;Pb;kg/rok;4,249;V;kg/rok;0,048;Zn;kg/rok;30,91;Tl;kg/rok;0,018;F;kg/rok;130;Cl;kg/rok;10804;PCDD+PCDF;mg/rok;6;;;;;;;;;;;;
""" 

Last rows of the dataset:
"""
25638955;3428982;5612951;774970301;Recovera Vyu�it� zdroj� a.s. � Spalovna pr�myslov�ch odpad� Trmice;Od 19 .4. 2022 do�lo ke zm�n� n�zvu provozovatele (d��ve SUEZ CZ a.s.).;Recovera Vyu�it� zdroj� a.s.;�pan�lsk� 1073;12000 Praha 2;Recovera Vyu�it� zdroj� a.s.� Spalovna pr�myslov�ch odpad� Trmice;Na Rovn�m 865;40004 Trmice;1993;2004 � za��zen� pro z�chyt PCDD/F;odpady z r�zn�ch odv�tv� pr�m. �innosti, odpady ze zdravotn� a veterin�rn� p��e;16000;9725;3;samostatn� spalovac� linky � rota�n� pece RC 198/158 300 EG;dioxinov� a prachov� filtr, t��stup�ov� mokr� vyp�rka (odpr�en�, vodn� a alkalick� vyp�rka);TZL;t/rok;0,292;SO2;t/rok;1,359;NOx;t/rok;10,745;CO;t/rok;1,962;C;t/rok;0,099;Sb;kg/rok;1,41;As;kg/rok;0,537;Cd;kg/rok;0,2;Cr;kg/rok;8,391;Hg;kg/rok;3,213;Co;kg/rok;0,141;Mn;kg/rok;1,061;Cu;kg/rok;13,931;Ni;kg/rok;1,913;Pb;kg/rok;10,002;V;kg/rok;0,131;Tl;kg/rok;0,089;F;kg/rok;19,014;Cl;kg/rok;280,124;PCDD+PCDF;mg/rok;5,7;;;;;;;;;;;;;;;;;;
11835;3715152;5486845;776430491;DEZA, a.s. � Spalovna;;DEZA, a.s.;Masarykova 753;75701 Vala�sk� Mezi����;DEZA, a.s. � Spalovna;Masarykova 753;75701 Vala�sk� Mezi����;2000;;odpady z �ist�ren odp. vod, odpady z r�zn�ch odv�tv� pr�m. �innosti, obaly, tkaniny, zdrav. odpady, n�t�r. hmoty;10000;6874;1;spalovna pr�myslov�ch odpad� � rota�n� pec s doho��vac� komorou;tkaninov� t��komorov� filtr, mokr� t��stup�ov� alkalick� vyp�rka;TZL;t/rok;0,062;SO2;t/rok;0,107;NOx;t/rok;13,539;CO;t/rok;0,007;C;t/rok;0,053;Sb;kg/rok;0,672;As;kg/rok;0,672;Cd;kg/rok;0,672;Cr;kg/rok;0,672;Hg;kg/rok;2,626;Co;kg/rok;0,672;Mn;kg/rok;0,672;Cu;kg/rok;0,672;Ni;kg/rok;0,672;Pb;kg/rok;1,679;V;kg/rok;0,672;Tl;kg/rok;0,672;F;kg/rok;20,147;Cl;kg/rok;11,653;PCDD+PCDF;mg/rok;0,244;;;;;;;;;;;;;;;;;;
92584;3577251;5415800;793410111;Nemocnice Znojmo, p��sp�vkov� organizace � Kotelna a spalovna;;Nemocnice Znojmo, p��sp�vkov� organizace;MUDr. Jana Jansk�ho 2675;66902 Znojmo;Nemocnice Znojmo, p��sp�vkov� organizace � Kotelna a spalovna;MUDr. Jana Jansk�ho 2675;66902 Znojmo;1994;2004 � instalace nov� such� technologie �i�t�n� spalin;nemocni�n� a zdravotnick� odpady;780;847;1;dvoustup�ov� spalovac� pec HOVAL GG 14 (pyrol�zn� komora a dopalovac� termoreaktor);such� filtr s d�vkov�n�m aktivn�ch l�tek pro z�chyt t�k�ch kov� a dioxin�;TZL;t/rok;0,002;SO2;t/rok;0,021;NOx;t/rok;1,076;CO;t/rok;0,125;C;t/rok;0,015;Sb;kg/rok;0,011;As;kg/rok;0,011;Cd;kg/rok;0,001;Cr;kg/rok;0,316;Hg;kg/rok;0,015;Co;kg/rok;0,003;Mn;kg/rok;0,239;Cu;kg/rok;0,087;Ni;kg/rok;1,252;Pb;kg/rok;0,015;V;kg/rok;0,011;Tl;kg/rok;0,011;F;kg/rok;0,207;Cl;kg/rok;9,1;PCDD+PCDF;mg/rok;0,02;;;;;;;;;;;;;;;;;;
"""

Additional info about the dataset:
"""
Geographical overview of thermal waste treatment facilities

Yearly updated geographical navigator: The geographic navigator presents overall annual information about facilities for the incineration and co-incineration of waste, which are obtained from summary operating records. These are the following: identification number (IČ), name of the facility, address of the operator, address of the facility, putting into operation, types of waste incinerated, nominal capacity, amount of waste incinerated in tonnes per year, number and brief description of incineration lines, enumeration of equipment for reducing emissions, annual emissions of all pollutants reported.

The Czech Hydrometeorological Institute processes and continuously updates the database of equipment for thermal treatment of waste in cooperation with ČIŽP. Pursuant to Article 55 of Directive 2010/75/EU, which regulates access to information and public participation, we are making available a list of all thermal waste treatment facilities.
"""

User view for this dataset:
"""
I want to use this dataset to create a software which will visualise on the map where are the facilities for the incineration located and which type of waste can be incinerated there.
"""

If you understand this input, just type OK.
```

## 2. Provided CSV data

```
Summarize what the dataset represents and explain what context or domain the data comes from. Be concise.
```

```
What kind of entity or entities does the table row represent? Make the answer concise.
```

### 2.1 For each column

```
For each column provide a brief description of the column. What does it describe or represent? Answer for each column should be on a separate line and it should have format '<column name> : <column description>', no other text. If column name is not considered human readable, come up with the best suiting name for the column
```

#### 2.1.1 If missing values are present (either based on a threshold or if at least one value is missing) 

```
If some columns have missing values, please provide a likely explanation as to why the values are missing in this column. For each column write the answer on a separate line in a format '<column name> : <explanation>', no other text. If no column has a missing value or you have no explanation, just write "I have no explanation".
```

### 2.2 If columns correlate (if certain columns correlate...)

```
If some columns are correlated, provide a likely explanation for why these columns are correlated. For each correlated pair of columns write the answer on a separate line in a format `<column name> x <column name> : <explanation>`, no other text. If there is no pair of columns that are correlated or you have no explanation, just write "I have no explanation".
```

## 3. Provided schema

### 3.1 For each column

#### 3.1.1 For each constraint

```
Why does this constraint exist? Explain the reasoning behind the given constraint or rule in the schema.
```

## 4. Provided user view

```
If user view for the dataset is provided and you can deduce the user's question as well as the answer from the this view, write the answer as if you were writing it to the user. Otherwise write "Hello! How can I help you with this dataset?".
```

## 5. Ending the premade system prompts

```
PREMADE SYSTEM PROMPTS HAS ENDED, USER PROMPTS START NOW

If you understand, just write OK.
```

# Postrehy a otázky

- Dať output z data profilingu do ChatGPT je problém, pretože správa je príliš veľká, neodošle sa. Mal som nápad, že by sme mali 2 LLMka, jedno by sa využilo na spracovanie (zmenšenie, zostručnenie) outputu z data profilingu a druhé by bolo asistentom pre SW inžinierov. Ale output z data profilingu bol aj tomto prípade príliš veľký (predtým sa okrem outputu z data profilingu dávalo viac, chcel som ho dať posamo). Potom som si všimol, že sú v jsone aj vizualizácie (napr. heatmapa vo formáte XML alebo také niečo...), samples (head, tail tabuľky)... tak som ich zmazal. Ale nestačilo to. Asi by pomohlo mazať počty výskytov slov. Ale neskúšal som to zatiaľ. **OTÁZKA** Oplatí sa mazať? Pravdepodobne by bolo najlepšie algoritmicky spracovať report, vziať a LLM predať len dôležité info, napr. v akých stĺpcoch chýbajú hodnoty alebo aké su korelácie stĺpcov (a podľa toho využívať prompty podmienene, teda napr. ak korelácia vyššia ako X, opýtaj sa prečo je tam korelácia.)
- **OTÁZKA** Ako zistíme jazyk užívateľa? Predstava: Vykonajú sa predvytvorené prompty, získané info sa zobrazí v angličtine? Jazyk vieme získať z inputu, konkrétne z "Additional info" alebo "User view". Ale "Additional info" nemusí byť v jazyku užívateľa (možno ani view?). Návrhy:
    - Užívateľ ako input zadá jazyk (príp. sa vezme z jazyku stránky ak viacjazyčná, ale to asi nebude, lebo to neni náš cieľ)
    - Prvý sa ozve užívateľ a z toho vydedukujeme jeho jazyk (Ako by užívateľ začal? Čo ak z view sa dá zistiť užívateľova otázka/odpoveď)
    - Začneme defaultne v angličtine (teda aj zistené info promptami bude vypísané v angličtine) a jazyk zmeníme:
        - ak si to užívateľ vyžiada
        - vždy keď detekujeme zmenu jazyka (príde mi čudné ak by to systém stále text prekladal, čo ak by kvôli neustálym prekladom vznikli chyby?)
    - Obmedzíme sa len na angličtinu (momentálne je v inštrukciách, že užívateľ hovorí anglicky)
- **POZOR!** "ZL1 to ZL26 : popis stĺpcov" dalo, namiesto toho, aby všetky vypísalo po jednom.
- **POZOR!** Zdá sa, že aj keď v stĺpci nechýba hodnota, tak si myslí, že áno? A vymyslí dôvod, že prečo chýba. Viď stĺpec Názov v konverzácii nižšie. Ale ak sa proces viacej "zprogramatizuje" (využitie data profilingu), tak to bude asi OK.
- **POZOR!** Pri nahrávaní prvých a posledných riadkov pre LLM by asi bolo dobré vyberať riadky, kde je najviac hodnôt (resp. najmenej chýba), aby malo LLM čo najviac informácií, s ktorými môže pracovať.

---

[Link to the conversation 1](https://chatgpt.com/share/670d36eb-e758-8010-a3bc-ec85c39eb652)  
[Link to the conversation 2](https://chatgpt.com/share/670f8d5e-2d18-8010-91d6-793367f300ea)

## TODOs

- viď záznam 2024-10-16
