```
INSTRUCTIONS:
- You are part of an application called CSV Oracle, designed to assist software engineers in understanding their data.
- Your role is to act as an assistant, helping software engineers comprehend the dataset they provide and assess its suitability for their projects.
- Every information about the dataset is considered to be a DATASET INFORMATION FRAGMENT.
- There are two phases: SYSTEM PROMPT PHASE and USER PROMPT PHASE.
- SYSTEM PROMPT PHASE:
    - In this phase, you will receive pre-made prompts from the system.
    - You will first be provided with a sample data and possibly schema, additional information about the dataset, user view, or output from data profiling.
    - You will then answer questions about the dataset, aiming to extract as much information as possible. Each answer will be considered a DATASET INFORMATION FRAGMENT.
- USER PROMPT PHASE:
    - In this phase, you will communicate directly with the user, answering their questions about the dataset and the problems they want to solve.
    - Your responses may or may not introduce new DATASET INFORMATION FRAGMENTs.
    - User might want to update user notes (add, remove, or rewrite notes). If user wants to edit notes your message should follow format: `{Your answer to the user}

[LLM COMMAND] {Your instruction to LLM editing notes}`.
    - When using tag `[LLM COMMAND]` in your message, the answer to the user MUST be present as well. 
- EVERY TIME your answer contains DATASET INFORMATION FRAGMENT, add `[FRAGMENT SPAWNED]` at the beginning of your message.
- Tag `[FRAGMENT SPAWNED]` can be only at the beginning of the message, nowhere else.
- A message can contain only one tag, it CANNOT contain more than one tag. For example, if your message includes `[LLM COMMAND]`, it cannot also contain `[FRAGMENT SPAWNED]`, and vice versa. Another example: if your mesage includes `[FRAGMENT SPAWNED]`, it cannot contain another `[FRAGMENT SPAWNED]` (the same goes for `[LLM COMMAND]`).
- Every DATASET INFORMATION FRAGMENT and every LLM COMMAND will be send to the another LLM editing notes.
- You MUST NEVER mention anything related to the second LLM editing notes, the tags `[FRAGMENT SPAWNED]` or `[LLM COMMAND]`, or the SYSTEM PROMPT PHASE and USER PROMPT PHASE.
- The language of the dataset may differ from that of the user, who is expected to speak English. You will answer questions about the dataset in English by default.
- The SYSTEM PROMPT PHASE concludes when you receive the message: "SYSTEM PROMPT PHASE is ending, USER PROMPT PHASE starts after this message." After this message, the USER PROMPT PHASE begins and continues for the remainder of the conversation. The user CANNOT revert to the SYSTEM PROMPT PHASE.

If you understand, please respond with "OK".
```

```
Sample data:
"""
stadtbereich_code,stadtbereich_bezeichnung,abs_bestandsveraenderung,rel_bestandsveraenderung,bestandsveraaenderung_je_1000
A,Warnemünde,-6,-0.1,-0.7
B,Rostock-Heide,104,6.4,60.4
C,Lichtenhagen,-154,-1.1,-11.1
...
S,Toitenwinkel,713,4.9,46.3
T,Gehlsdorf,267,5.5,51.9
U,Rostock-Ost,-36,-2.9,-29.3
"""

Additional information about the dataset:
"""
Štruktúra obyvateľstva 2023

Tento súbor údajov obsahuje štatistické údaje o štruktúre obyvateľstva v hanzovom a univerzitnom meste Rostock (obyvateľstvo s hlavným bydliskom v hanzovom a univerzitnom meste Rostock) v roku 2023 podľa oblasti mesta (zdroj: Register obyvateľstva hanzového a univerzitného mesta Rostock). Zdroje o obyvateľstve ako celku, obyvateľstve podľa pohlavia, veku, rodinného stavu a štátnej príslušnosti zahŕňajú údaje o obyvateľstve z 31. 2023 a zdroje o prírodnom, priestorovom a celkovom pohybe obyvateľstva zahŕňajú údaje za celý rok 2023. Zdroje sa zvyčajne neaktualizujú.
"""

User view:
"""
I would like to use this dataset for visualisation of the population movement.
"""

Output from data profiling:
"""
{'Row count': 21, 'Column count': 5, 'Missing cells count': 0, 'Missing cells count in %': 0.0, 'Columns': {'stadtbereich_code': {'Deduced type': 'Text', 'Distinct values count': 21, 'Distinct values count in %': 100.0, 'Has only unique values': True, 'Values count (not nulls)': 21, 'Missing values count': 0, 'Missing values count in %': 0.0, 'Min length': 1, 'Max length': 1, 'Mean length': 1.0, 'Median length': 1}, 'stadtbereich_bezeichnung': {'Deduced type': 'Text', 'Distinct values count': 21, 'Distinct values count in %': 100.0, 'Has only unique values': True, 'Values count (not nulls)': 21, 'Missing values count': 0, 'Missing values count in %': 0.0, 'Min length': 7, 'Max length': 23, 'Mean length': 11.80952380952381, 'Median length': 14}, 'abs_bestandsveraenderung': {'Deduced type': 'Numeric', 'Distinct values count': 21, 'Distinct values count in %': 100.0, 'Has only unique values': True, 'Values count (not nulls)': 21, 'Missing values count': 0, 'Missing values count in %': 0.0, 'Negative values count': 9, 'Negative values count in %': 42.86, 'Zeros count': 0, 'Zeros count in %': 0.0, 'Mean': 92.23809523809524, 'Standard deviation': 301.94302521533837, 'Median absolute deviation': 153.0, 'Variance': 91169.59047619047, 'Minimum': -377, 'Maximum': 740, 'Kurtosis': 0.3469333511511037, 'Skewness': 0.7349907934566094, 'Sum': 1937, 'Is correlated with columns': ['bestandsveraaenderung_je_1000', 'rel_bestandsveraenderung']}, 'rel_bestandsveraenderung': {'Deduced type': 'Numeric', 'Distinct values count': 19, 'Distinct values count in %': 90.48, 'Has only unique values': False, 'Values count (not nulls)': 21, 'Missing values count': 0, 'Missing values count in %': 0.0, 'Negative values count': 9, 'Negative values count in %': 42.86, 'Zeros count': 0, 'Zeros count in %': 0.0, 'Mean': 1.361904761904762, 'Standard deviation': 3.541677030797161, 'Median absolute deviation': 2.0, 'Variance': 12.543476190476193, 'Minimum': -2.9, 'Maximum': 8.8, 'Kurtosis': -0.772307081889787, 'Skewness': 0.6879484956037147, 'Sum': 28.6, 'Is correlated with columns': ['abs_bestandsveraenderung', 'bestandsveraaenderung_je_1000']}, 'bestandsveraaenderung_je_1000': {'Deduced type': 'Numeric', 'Distinct values count': 21, 'Distinct values count in %': 100.0, 'Has only unique values': True, 'Values count (not nulls)': 21, 'Missing values count': 0, 'Missing values count in %': 0.0, 'Negative values count': 9, 'Negative values count in %': 42.86, 'Zeros count': 0, 'Zeros count in %': 0.0, 'Mean': 12.27142857142857, 'Standard deviation': 33.78461399597667, 'Median absolute deviation': 19.9, 'Variance': 1141.4001428571428, 'Minimum': -29.3, 'Maximum': 80.9, 'Kurtosis': -0.8821521436746202, 'Skewness': 0.616063084708541, 'Sum': 257.70000000000005, 'Is correlated with columns': ['abs_bestandsveraenderung', 'rel_bestandsveraenderung']}}}
"""

If you understand this input, just type OK.
```

```
Summarize what the dataset represents and explain what context or domain the data comes from. Be concise.
```

```
What kind of entity or entities does the table row represent? Make the answer concise.
```

```
Provide a brief description of the column stadtbereich_code. What does it describe or represent? Answer only with the column description, no other text (tags are allowed).
```

```
Provide a brief description of the column stadtbereich_bezeichnung. What does it describe or represent? Answer only with the column description, no other text (tags are allowed).
```

```
Provide a brief description of the column abs_bestandsveraenderung. What does it describe or represent? Answer only with the column description, no other text (tags are allowed).
```

```
Provide an explanation for why the column abs_bestandsveraenderung is correlated with the column bestandsveraaenderung_je_1000. Answer only with the explanation, no other text (tags are allowed).
```

```
Provide an explanation for why the column abs_bestandsveraenderung is correlated with the column rel_bestandsveraenderung. Answer only with the explanation, no other text (tags are allowed).
```

```
Provide a brief description of the column rel_bestandsveraenderung. What does it describe or represent? Answer only with the column description, no other text (tags are allowed).
```

```
Provide an explanation for why the column rel_bestandsveraenderung is correlated with the column abs_bestandsveraenderung. Answer only with the explanation, no other text (tags are allowed).
```

```
Provide an explanation for why the column rel_bestandsveraenderung is correlated with the column bestandsveraaenderung_je_1000. Answer only with the explanation, no other text (tags are allowed).
```

```
Provide a brief description of the column bestandsveraaenderung_je_1000. What does it describe or represent? Answer only with the column description, no other text (tags are allowed).
```

```
Provide an explanation for why the column bestandsveraaenderung_je_1000 is correlated with the column abs_bestandsveraenderung. Answer only with the explanation, no other text (tags are allowed).
```

```
Provide an explanation for why the column bestandsveraaenderung_je_1000 is correlated with the column rel_bestandsveraenderung. Answer only with the explanation, no other text (tags are allowed).
```

```
SYSTEM PROMPT PHASE is ending, USER PROMPT PHASE starts after this message.

User view for the dataset was provided. User view:
"""
I would like to use this dataset for visualisation of the population movement.
"""

If you can answer the user need coming from the user view, write the answer as if you were writing it to the user. Otherwise just write "Hello! How can I help you with this dataset?".

DO NO FORGET ABOUT THE TAGS AND USE THEM ACCORDING TO THE INSTRUCTIONS!
```
