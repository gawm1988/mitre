# https://spacy.io/usage/linguistic-features#pos-tagging
import pandas as pd
import spacy
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--file', type=str, required=True)
args = parser.parse_args()

techniques_df = pd.read_csv(f"./resources/clustering/{args.file}")

descriptions = techniques_df["description"]
result_verbs = []
result_nouns = []
result_proper_nouns = []
result_unknown = []
result_aux = []
nlp = spacy.load("en_core_web_sm")

for d in descriptions:
    verbs = []
    proper_nouns = []
    nouns = []
    aux = []
    unknown = []
    doc = nlp(d)
    for token in doc:
        pos = token.pos_
        if pos == "VERB":
            verbs.append(token.lemma_)
        if pos == "PROPN":
            proper_nouns.append(token.lemma_)
        if pos == "NOUN":
            nouns.append(token.lemma_)
        if pos == "AUX":
            aux.append(token.lemma_)
        if pos == "X":
            unknown.append(token.lemma_)
    result_verbs.append(verbs)
    result_nouns.append(nouns)
    result_proper_nouns.append(proper_nouns)
    result_unknown.append(unknown)
    result_aux.append(aux)


techniques_df["verbs"] = result_verbs
techniques_df["proper_nouns"] = result_proper_nouns
techniques_df["nouns"] = result_nouns
techniques_df["unknown"] = result_unknown
techniques_df["aux"] = result_aux

print(techniques_df)

techniques_df.to_csv(f"./resources/evaluation/{args.file}")
