import pandas as pd
import spacy
import argparse
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument('--file', type=str, required=True)
args = parser.parse_args()

techniques_df = pd.read_csv(f"./resources/{args.file}")

descriptions = techniques_df["text"]


nlp = spacy.load("en_core_web_sm")

pos_map = ["VERB", "ADV", "AUX", "PROPN", "NOUN", "X"]
results = []

for d in tqdm(descriptions, desc="Filter part of speech"):
    doc = nlp(d)
    current = {pos: [] for pos in pos_map}
    for token in doc:
        if token.pos_ in current:
            current[token.pos_].append(token.lemma_)
    for pos in current:
        current[pos].sort()     # sort alphabetically
    results.append(current)

pos_df = pd.DataFrame(results)
techniques_df = pd.concat([techniques_df, pos_df], axis=1)

out_path = f"./resources/{args.file[:-4]}_pos.csv"
techniques_df.to_csv(out_path, index=False)
print(f"File saved → {out_path}")