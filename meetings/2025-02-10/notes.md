# Poznámky z 10.2.2025

## Priebeh

- Predstavená aplikácia.

## TODOs

- Pokračovať s implementáciou programu.
    - Opraviť načítanie datasetov (nech neni loading animácia na začiatku, keď neni loadnutý status, nech sa status loaduje s datasetom hneď asi radšej).
    - LLM nemôže kompletne manipulovať s celou dataset knowledge (JSONom).
    - Zrýchliť program (ak niekde pomalé načítanie, odpoveď pri chatovaní).
    - Nemalo by ChatLLM využívať pri chatovaní aj dataset knowledge ako index?
    - Lepší príklad. O datasete. Napr.:
        - Aké sú v datasete "population figures"? (Toto slovné spojenie bolo spomenuté v odpovedi na need z user view.)
        - Je to počet obyvateľov v nejakom časovom období? Alebo k jednotlivým rokom? Alebo ako?
        - Ak užívateľ povie niečo v tom zmysle "Ja si nemyslím, že to je takto, teraz som si pozrel dáta a je to inak." -> Má zapísať do knowledge, lebo user mu povedal nejaký fakt o datasete.
- Ako funguje Llamaindex, resp. ReActAgent, index (čo to presne je, to celé csv tam je? Vektory na vety zas pojdu alebo ako to? Nevadí, že ak veľké je?)... Nemôžem používať len užívateľsky, musím presne vedieť ako to funguje. Asi ak využívam.
- Google Scholar. 
---
- Zamyslenia:
    - MSQL možno bude treba nahradiť, napr. SOLRom?
    - Z akých všetkých súborov vytvárať indexy? Napr. všetky csv -> 1 index alebo 1 csv -> 1 index? (Zrejme treba experiment, vybrať aspoň 2 možnosti na meranie).
