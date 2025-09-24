import pandas as pd
import requests
import ast

cluster_df = pd.read_csv('../resources/all-MiniLM-L6-v2/clustering/agc_384_0.2_average_clusters.csv')

# convert entries of column into lists
cluster_df["VERB"] = cluster_df["VERB"].apply(
    lambda x: ast.literal_eval(x) if isinstance(x, str) else x
)

verbs = cluster_df["VERB"].iloc[0]

class Synonym:
    def __init__(self, data):
        self.word = data[0]['word']
        self.meanings = data[0]['meanings']

    def get_synonyms(self):
        definitions = []
        synonyms = []
        for meaning in self.meanings:
            partOfSpeech = meaning["partOfSpeech"]
            if partOfSpeech != "verb":
                continue
            for definition in meaning["definitions"]:
                definitions.append(definition['definition'])
                synonyms.append(definition['synonyms'])
        return definitions, synonyms

    def __str__(self):
        definitions, synonyms = self.get_synonyms()
        return f"word: {self.word}\ndefinitions: {definitions}\nsynonyms: {synonyms}"

base_url = "https://api.dictionaryapi.dev/api/v2/entries/en/"

def get_synonyms(word:str):
    word = word.lower()
    response = requests.get(base_url + word)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"No data retrieved for {word} - {response.status_code}")
        return None

verbs_df = pd.DataFrame(
    {"verb": [],
     "synonyms": [],
     "definitions": []}
)

import pandas as pd

for verb in verbs:
    verb_info = get_synonyms(verb)
    if verb_info:
        synonym = Synonym(verb_info)
        definitions, synonyms = synonym.get_synonyms()
        entry = {"verb": verb, "synonyms": synonyms, "definitions": definitions}
        entry_df = pd.DataFrame([entry])  # aus dict → DataFrame
        verbs_df = pd.concat([verbs_df, entry_df], ignore_index=True)


print (verbs_df.head())
verbs_df.to_csv("./synonyms.csv", index=False)