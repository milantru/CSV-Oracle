```
Instructions:
- You are an assistant for the software engineers.
- Your job is to help the software engineers to understand the data they provide and assess its suitability for their project needs.
- In the next message you will receive an input in this format:
Dataset schema:
"""
{Dataset schema}
"""

Sample of the dataset:
"""
{Sample of the dataset}
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

```
Sample of the dataset:
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

Additional info about the dataset:
"""
Štruktúra obyvateľstva 2023

Tento súbor údajov obsahuje štatistické údaje o štruktúre obyvateľstva v hanzovom a univerzitnom meste Rostock (obyvateľstvo s hlavným bydliskom v hanzovom a univerzitnom meste Rostock) v roku 2023 podľa oblasti mesta (zdroj: Register obyvateľstva hanzového a univerzitného mesta Rostock). Zdroje o obyvateľstve ako celku, obyvateľstve podľa pohlavia, veku, rodinného stavu a štátnej príslušnosti zahŕňajú údaje o obyvateľstve z 31. 2023 a zdroje o prírodnom, priestorovom a celkovom pohybe obyvateľstva zahŕňajú údaje za celý rok 2023. Zdroje sa zvyčajne neaktualizujú.
"""

User view for this dataset:
"""
I would like to use this dataset for visualisation of the population movement.
"""

Output from the data profiling of the dataset:
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
Provide a brief description of the column stadtbereich_code. What does it describe or represent? Answer only with the column description, no other text.
```

```
Provide a brief description of the column stadtbereich_bezeichnung. What does it describe or represent? Answer only with the column description, no other text.
```

```
Provide a brief description of the column abs_bestandsveraenderung. What does it describe or represent? Answer only with the column description, no other text.
```

```
Provide a likely explanation for why the column abs_bestandsveraenderung is correlated with column bestandsveraaenderung_je_1000. Answer only with the explanation, no other text. If you have no explanation, just write "I have no explanation".
```

```
Provide a likely explanation for why the column abs_bestandsveraenderung is correlated with column rel_bestandsveraenderung. Answer only with the explanation, no other text. If you have no explanation, just write "I have no explanation".
```

```
Provide a brief description of the column rel_bestandsveraenderung. What does it describe or represent? Answer only with the column description, no other text.
```

```
Provide a likely explanation for why the column rel_bestandsveraenderung is correlated with column abs_bestandsveraenderung. Answer only with the explanation, no other text. If you have no explanation, just write "I have no explanation".
```

```
Provide a likely explanation for why the column rel_bestandsveraenderung is correlated with column bestandsveraaenderung_je_1000. Answer only with the explanation, no other text. If you have no explanation, just write "I have no explanation".
```

```
Provide a brief description of the column bestandsveraaenderung_je_1000. What does it describe or represent? Answer only with the column description, no other text.
```

```
Provide a likely explanation for why the column bestandsveraaenderung_je_1000 is correlated with column abs_bestandsveraenderung. Answer only with the explanation, no other text. If you have no explanation, just write "I have no explanation".
```

```
Provide a likely explanation for why the column bestandsveraaenderung_je_1000 is correlated with column rel_bestandsveraenderung. Answer only with the explanation, no other text. If you have no explanation, just write "I have no explanation".
```

```
If user view for the dataset is provided and you can deduce the user's question as well as the answer from the this view, write the answer as if you were writing it to the user. Otherwise write "Hello! How can I help you with this dataset?".
```

```
PREMADE SYSTEM PROMPTS HAS ENDED, USER PROMPTS START NOW

If you understand, just write OK.
```
