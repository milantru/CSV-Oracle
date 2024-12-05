# Poznámky z 26.11.2024

## Priebeh

- Prešli sme výber frameworku (LlamaIndexu) na prácu s LLM + predošlé otázky.

## TODOs

- Napísať email ohľadom datasetov so schémou.
- Skúsiť nájsť nejaký dataset so schémou na Kaggle.
- Môžeš prezerať na Google Scholar related work.
- Napíš odstavec zadania do sisu (Dominik Prokop, inšpiruj sa jak on mal) a pošli mailom.

---

# Zápisky

## Links

- [The easiest way to work with large language models | Learn LangChain in 10min](https://youtu.be/kmbS6FDQh7c)
- [LlamaIndex overview & use cases | LangChain integration](https://youtu.be/cNMYeW2mpBs)
- [Introduction to LlamaIndex with Python (2024)](https://youtu.be/cCyYGYyCka4)

- [LangChain vs LlamaIndex: A Detailed Comparison](https://www.datacamp.com/blog/langchain-vs-llamaindex?dc_referrer=https%3A%2F%2Fwww.google.com%2F)
- [Which Tools to Use for LLM-Powered Applications: LangChain vs LlamaIndex vs NIM](https://www.freecodecamp.org/news/llm-powered-apps-langchain-vs-llamaindex-vs-nim/)

## Čo potrebujeme spraviť

1. Načítaj .csv súbory aj s ich .json profilingom a vytvor s nich dokumenty/indexy (indexy sú jsony, dajú sa uložiť persistentne).
2. Pomocou LLM1 a indexov sa môžeme pýtať predpripravené prompty. Nemusíme mať memory ako pre chat, ale potrebujeme odchytiť otázku a odpoveď a v určitom formáte ich predať LLM pre vytvorenie json poznámok. V pamäti si držíme poslednú verziu .json poznámok
3. Končí fáza s predvytvorenými promptami, nasleduje chat s užívateľom. .json poznámky sa asi môžu persistentne uložiť (je to 1. verzia poznámok), tento json sa môže znovu načítať a použiť ako ďalší document/index pre LLM1.
4. Keď užívateľ chatuje s LLM1 (chat, takže potrebujeme Memory), tak sa môžu vygenerovať inštrukcie (pomocou instr tagov). Tie potrebujeme odchytiť a ich obsah predať LLM2.
5. Stále keď sa objaví instr tag a predá LLM2, tak sa "updatne" poznámkový index alebo vytvorí nový (asi stačí len ak bude veľa správ, t.j. "dôjde" chat memory, napr. ak memory 10 správ, tak po 10 správach).

## Záver

- Vyzerá, že to čo chceme spraviť sa dá pomocou LlamaIndexu ale aj LangChainu.
- Ak si musím vybrať 1 z nich, vyberám si LlamaIndex, pretože ten je skôr zameraný na data retrieval.
- Dá sa využiť aj kombinácia, že používame LangChain na abstrahovanie modelov, chainy, aj na chat memory (vraj lepšia v [blogu](https://www.datacamp.com/blog/langchain-vs-llamaindex?dc_referrer=https%3A%2F%2Fwww.google.com%2F) písali) a LlamaIndex ako tool na data retrieval.
- Ale s LlamaIndex vieme tiež pracovať abstraktne s modelmi, má chat memory (vôbec sa mi nezdá že by to pre naše účely nestačilo, do .jsonu sa ukladá) a čo sa týka chainov, tak to by sa mohlo hodiť, ale tú logiku si vieme naprogramovať aj sami ľahko ("ak by si využili LangChain, tak by sme namiesto 3 riadkov napísali 1", asi tak nejak, viď [príklady](https://chatgpt.com/share/6741f0ae-ff54-8010-98df-171dc1ba22e5)). Pridanie LangChainu by pridalo ďalšie dependencies a komplexitu. Komplexitu nie v zmysle toho, že sa skomplikuje kód, ale v zmysle toho, že sa bude treba učiť nová knižnica.
- Z toho dôvodu si myslím, že stačí využiť LlamaIndex.
