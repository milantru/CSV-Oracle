# Poznámky z 19.11.2024

## Priebeh

- Prešli sme zápisky (viď dole).

## TODOs

- **POZOR!** Neboli prejdené všetky otázky, takže na ďalšom stretnutí prejsť!
- Pozrieť knižnice na prácu s LLM, napr. Langchain, Llamaindex.

---

# Zápisky

- ~~TODO: Ešte raz skontroluj prompty (myslím, že treba niečo zmazať + zaokruhliť hodnoty nejaké).~~
- TODO: Lingvistická metóda na textový stĺpec? Zisti a doimplementuj asi.
    - Napísal som do ChatGPT aké sú možnosti... Sprav z jeho [odpovede](https://chatgpt.com/share/6738f5cb-d0a4-8010-a8ee-7d1db1cfd6fc) analýzu (daj do textu).
    - (**OTÁZKA**) Opýtaj sa akú metódu využiť, reps. ako zvoliť/podľa čoho?
- TODO: Zožeň dataset so schemou a skús aj s ňou celý proces.
    - (**OTÁZKA**) CSV schema to je [toto](https://github.com/adamretter/csv-schema/blob/master/example-schemas/ADM_362-technical-acquisition-with-minimal-transcription.csvs)?
    - (**OTÁZKA**) Len asi prilepím do input promptu, či?
    - (**OTÁZKA**) Nejaký "rozumný" dataset?
- ~~TODO: Prompty pre LLM pre *tú* vizualizáciu(?).~~
    - ~~Skúsil som a myslím si, že by nemal byť problém.~~
    - ~~(**OTÁZKA**) Mohlo by to byť ako optional?~~
- cmds:
```
python create_notes_llm_prompts.py -p "datasets"
```

```
python create_system_prompts.py -p "datasets" -s "," -e "utf-8" -a "Štruktúra obyvateľstva 2023

Tento súbor údajov obsahuje štatistické údaje o štruktúre obyvateľstva v hanzovom a univerzitnom meste Rostock (obyvateľstvo s hlavným bydliskom v hanzovom a univerzitnom meste Rostock) v roku 2023 podľa oblasti mesta (zdroj: Register obyvateľstva hanzového a univerzitného mesta Rostock). Zdroje o obyvateľstve ako celku, obyvateľstve podľa pohlavia, veku, rodinného stavu a štátnej príslušnosti zahŕňajú údaje o obyvateľstve z 31. 2023 a zdroje o prírodnom, priestorovom a celkovom pohybe obyvateľstva zahŕňajú údaje za celý rok 2023. Zdroje sa zvyčajne neaktualizujú." -u "I would like to use this dataset for visualisation of the population movement."
```

```
python create_user_prompts.py -s "You can use this dataset to visualize population movement in Rostock by plotting the population changes over time across different city districts. The columns detailing population changes (such as abs_bestandsveraenderung, rel_bestandsveraenderung, and bestandsveraaenderung_je_1000) can be visualized to show both absolute and relative changes in population, as well as per-thousand changes. You can also compare population distribution between male and female residents using the anzahl_maennlich and anzahl_weiblich columns. A combination of bar charts, line graphs, and heatmaps could be effective for representing these dynamics."
```

- [Skúsil som rozdeliť system a user prompting fázy](https://chatgpt.com/share/67323937-b26c-8010-87a8-828a473624e5) a spôsobuje to problém. Keď na začiatku poskytnem dataset knowledge, potom sa LLM niekedy snaží upravovať notes (ten knowledge), viď koniec chatu, a to aj keď mu v inštrukciách píšem, aby to nerobil. Zdá sa, že sa musím vrátiť k predošlému spôsobu, i keď možno nie úplne... skúsim nevypínať koverzáciu, ale využijem inštruckie oddelene (prepisovanie inštrukcií).  
**[UPDATE]** [Keď som dal obe fázy do jednej konverzácie](https://chatgpt.com/share/67335e81-3dcc-8010-8521-45b5703fab98), tak sa zdá, že v pohode to funguje všetko ([chat pre vytvaranie notes](https://chatgpt.com/share/673360ae-78c0-8010-8821-b4b50911f3b2)).

---

## Zhrnutie ako to aktuálne prebieha:
- SYSTEM PROMPTING ide, potom v rovnakom chate USER PROMPTING, v ktorom sa využívajú tagy `<instr>` a `</instr>`.
- Počas SYSTEM PROMPTINGu NOTES LLM dostáva správy v určitom formáte, viď:
```
Question: 
"""
Summarize what the dataset (as all tables together, prompts about each table separately will come later) represents and explain what context or domain the data comes from. Be concise.
"""
Answer: 
"""
The dataset provides population statistics for the city of Rostock in 2023, divided by city areas. It covers overall population changes (absolute and relative) and gender-specific population counts and percentages. The data includes metrics on population growth or decline per area, and the distribution of male and female residents. The context is demographic and urban statistics for monitoring population structure and movement in Rostock, based on data from the city's population register.
"""

Add obtained information to the notes.
```

dokonca aj pre user view, viď:

```
Question: 
"""
User view for the dataset was provided. User view:
"""
I would like to use this dataset for visualisation of the population movement.
"""

If you can answer the user need coming from the user view, write the answer as if you were writing it to the user (provide only answer, no questions, e.g. "Would you like assistance with some specific task?"). Otherwise just write "Hello! How can I help you with this dataset?".
"""

Answer: 
"""
You can use this dataset to visualize population movement in Rostock by plotting the population changes over time across different city districts. The columns detailing population changes (such as abs_bestandsveraenderung, rel_bestandsveraenderung, and bestandsveraaenderung_je_1000) can be visualized to show both absolute and relative changes in population, as well as per-thousand changes. You can also compare population distribution between male and female residents using the anzahl_maennlich and anzahl_weiblich columns. A combination of bar charts, line graphs, and heatmaps could be effective for representing these dynamics.
"""

Add obtained information to the notes.
```

A potom jak USER PROMPTING začne, tak už len obsah medzi tagmi `<instr>` a `</instr>` sa berie a dáva NOTES LLMku.


- **MOŽNÉ ROZŠÍRENIE...** Zatiaľ máme MD poznámky len, ale môžme spraviť aj *tú* UI vizualizáciu. Predstavme si, že každá komponenta má nastavený prompt, ktorým získa od 3. LLM (ktoré číta poznámky) svoje info, ktoré zoobrazí (viď [chat](https://chatgpt.com/share/6734db47-c74c-8010-be8b-6a5ca843a804)).
