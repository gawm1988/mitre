pip freeze > requirements.txt

# Evaluation
## Verben
- [ ] Konzentration auf die Verben.
- [ ] Synonyme per API abfragen? [https://dictionaryapi.dev/](https://dictionaryapi.dev/)
- [ ] mögliche Quellen:  Dürscheid: Syntax (gut lesbar), Eisenberg: Grundriss der deutschen Grammatik. Band 2. Der Satz (wissenschaftlich anerkannt), die Grammatik aus dem Duden-Verlag, Elektronisches Valenzwörterbuch  des Deutschen: E valbu, angesiedelt beim Institut für deutsche Sprache (IDS) in Mannheim

## PoS Tagging
| POS-Tag | Beschreibung                                         | Beispiel                         |
| ------- | ---------------------------------------------------- | -------------------------------- |
| `ADJ`   | **Adjektiv** – beschreibt Eigenschaften              | *schnell*, *beautiful*           |
| `ADP`   | **Adposition** – Präposition oder Postposition       | *in*, *auf*, *under*, *with*     |
| `ADV`   | **Adverb** – beschreibt ein Verb oder anderes Adverb | *schnell*, *very*, *oft*         |
| `AUX`   | **Hilfsverb**                                        | *haben*, *sein*, *do*, *is*      |
| `CCONJ` | **Koordinierende Konjunktion**                       | *und*, *aber*, *or*, *and*       |
| `DET`   | **Determiner / Artikel**                             | *der*, *die*, *the*, *some*      |
| `INTJ`  | **Interjektion / Ausruf**                            | *oh*, *ah*, *wow*, *hey*         |
| `NOUN`  | **Substantiv** – gewöhnliche Nomen                   | *Haus*, *dog*, *book*            |
| `NUM`   | **Zahl**                                             | *zwei*, *100*, *first*, *drei*   |
| `PART`  | **Partikel** – grammatikalische Marker               | *nicht*, *to*, *zu*              |
| `PRON`  | **Pronomen**                                         | *ich*, *du*, *he*, *sie*, *wir*  |
| `PROPN` | **Eigenname**                                        | *Berlin*, *John*, *Mercedes*     |
| `PUNCT` | **Satzzeichen**                                      | `.` `,` `!` `?`                  |
| `SCONJ` | **Subordinierende Konjunktion**                      | *weil*, *dass*, *if*, *although* |
| `SYM`   | **Symbol**                                           | `+` `#` `%`                      |
| `VERB`  | **Vollverb**                                         | *gehen*, *run*, *schreiben*      |
| `X`     | **Unbekannt oder andere Klasse**                     | selten, z. B. bei Fehlern        |
| `SPACE` | **Leerzeichen** (nicht sichtbar)                     | `" "` (wird manchmal ignoriert)  |


# Diskussion Proposal
## Max_token limit
### Anzahl an Techniken die das Limit überschreiten
- [ ] 80 von 679 Techniken mit mehr als 512 token
- [ ] Maximum bei ca. 1040 token

### Max_token erhöhen
- [ ] Vorschlag die Anzahl der max. erlaubten token im source code ändern.
- [ ] Laut Dokumentation: Arbeitsspeicherbedarf steigt exponentiell und max. kann nicht überschritten werden.

### Verschiedene Encoder verwenden
- [ ] Modelle verwenden, die mehr token als Eingabe zulassen
- [ ] Müssen für ggfs. angepasst werden für text-embeddings

### Summary erstellen vor Erstellung der Embeddings
- [ ] Texte kürzen durch vorher von LM erstellten Zusammenfassungen
- [ ] War allerdings in einem Paper nicht von Erfolg gekrönt, da Semantik nicht 1:1 übertragen wurde

## Approach
### Abgleich der gefundenen ambiguities
- [ ] sind die Ähnlichkeiten auch in menschlicher Sprache zu erkennen?

## Ambiguities
### Mehrere Taktiken zu einer Technik
- [ ] A: worin liegt das Problem, dass eine Technik mehreren Taktiken zugeordnet sind?
- [ ] Idee: Werden falsche Rückschlüsse für die Abwehr von Cyberangriffen gezogen, wenn ein Analyst sich in der falschen Phase eine Angriffs wähnt?
- [ ] Müssen die ähnlichen Angriffe für verschiedene Stadien einer Attack-Chain unterschiedlich beschrieben / bewertet werden?
- [ ] Problem beim Clustering: Es wird durch die meisten Algorithmen immer nur 0 oder 1 cluster zugeordnet.


