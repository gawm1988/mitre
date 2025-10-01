import os
import time
import ast
import pandas as pd
import requests
from tqdm import tqdm

base_url = "https://api.dictionaryapi.dev/api/v2/entries/en/"

class Word:
    def __init__(self, data):
        self.word = data[0]['word']
        self.data = data

    def get_def_and_syn(self, pos: str):
        definitions, synonyms = [], []
        for entry in self.data:
            for meaning in entry.get('meanings', []):
                if meaning.get("partOfSpeech") != pos:
                    continue
                for d in meaning.get("definitions", []):
                    if isinstance(d.get('definition'), str):
                        definitions.append(d['definition'])
                # flatten synonyms (list of strings)
                syns = meaning.get('synonyms') or []
                for s in syns:
                    if isinstance(s, str):
                        synonyms.append(s)
        return definitions, synonyms

def get_word_data(word: str):
    word = word.lower().strip()
    if not word:
        return None
    r = requests.get(base_url + word, timeout=10)
    if r.status_code == 200:
        return r.json()
    print(f"No data retrieved for {word} → {r.status_code}")
    return None

# load or create new dictionaries
os.makedirs("../resources/dictionaries", exist_ok=True)

def load_or_create(path: str) -> pd.DataFrame:
    if os.path.exists(path):
        print(f"Load dictionary from {path}")
        df = pd.read_csv(path)
        if "word" not in df.columns:
            df = df.reset_index()
    else:
        print(f"Create new dictionary for {path}")
        df = pd.DataFrame(columns=["word", "partOfSpeech", "definitions", "synonyms"])
    return df.set_index("word")

verb_dictionary_df   = load_or_create("../resources/dictionaries/verbs.csv")
noun_dictionary_df   = load_or_create("../resources/dictionaries/nouns.csv")
adverb_dictionary_df = load_or_create("../resources/dictionaries/adverbs.csv")

def get_word_list(words: list, pos: str, dictionary_df: pd.DataFrame):
    # normalize
    norm_words = []
    seen = set()
    for w in words:
        if not isinstance(w, str):
            continue
        t = w.strip().lower()
        if t and t not in seen:
            seen.add(t); norm_words.append(t)

    cache = set(dictionary_df.index.astype(str))

    new_rows = []  # für neue Wörter
    out_rows = []  # für Ausgabe (bestehend + neu)

    for w in norm_words:
        if w in cache:
            row = dictionary_df.loc[w]
            out_rows.append({
                "word": w,
                "partOfSpeech": pos,
                "definitions": row["definitions"],
                "synonyms": row["synonyms"],
            })
            continue

        time.sleep(0.4)  # rate-limit to avoid HTTP 429 response
        data = get_word_data(w)
        if not data:
            row = {"word": w, "partOfSpeech": pos, "definitions": "", "synonyms": []}
            new_rows.append(row)
            continue

        word = Word(data)
        defs, syns = word.get_def_and_syn(pos)
        row = {"word": w, "partOfSpeech": pos, "definitions": defs, "synonyms": syns}
        new_rows.append(row)
        out_rows.append(row)

    # add new words to dictionary_df
    if new_rows:
        new_df = pd.DataFrame(new_rows).set_index("word")
        dictionary_df = pd.concat([dictionary_df, new_df], axis=0)

    result_df = pd.DataFrame(out_rows)

    return dictionary_df, result_df


# ======================= main =======================

cluster_df = pd.read_csv('../resources/all-MiniLM-L6-v2/clustering/agc_384_0.2_average_clusters.csv')

# parse columns
for col in ["VERB", "ADV", "NOUN"]:
    cluster_df[col] = cluster_df[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else (x or []))

clusters = sorted(set(cluster_df["cluster"].tolist()))

for cluster in tqdm(clusters, desc="Get descriptions and synonyms"):
    verbs, adverbs, nouns = [], [], []

    for row in cluster_df.itertuples():
        if row.cluster != cluster:
            continue
        verbs.extend(row.VERB or [])
        adverbs.extend(row.ADV or [])
        nouns.extend(row.NOUN or [])

    cluster_out = pd.DataFrame(columns=["word","partOfSpeech","definitions","synonyms"])
    verb_dictionary_df, res = get_word_list(verbs, "verb", verb_dictionary_df)
    cluster_out = pd.concat([cluster_out, res], ignore_index=True)
    noun_dictionary_df, res = get_word_list(nouns, "noun", noun_dictionary_df)
    cluster_out = pd.concat([cluster_out, res], ignore_index=True)
    adverb_dictionary_df, res = get_word_list(adverbs, "adverb", adverb_dictionary_df)
    cluster_out = pd.concat([cluster_out, res], ignore_index=True)

    cluster_out.to_csv(f"./test/synonyms_cluster_{cluster}.csv", index=False)

verb_dictionary_df.reset_index().to_csv("../resources/dictionaries/verbs.csv", index=False)
noun_dictionary_df.reset_index().to_csv("../resources/dictionaries/nouns.csv", index=False)
adverb_dictionary_df.reset_index().to_csv("../resources/dictionaries/adverbs.csv", index=False)
