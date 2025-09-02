"""
This scripts counts the number of tokens for a given String
"""

import pandas as pd
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer

CSV_PATH = "techniques.csv"
df = pd.read_csv(CSV_PATH)

# Tokenizer
tok = AutoTokenizer.from_pretrained("../models/all-MiniLM-L6-v2")

def n_tokens(text: str) -> int:
    return len(tok(text, add_special_tokens=False)["input_ids"])


token_counts = df["text"].apply(n_tokens)

out_df = pd.DataFrame({
    "token_count": token_counts,
    "text": df["text"]
}).reset_index(drop=True)

print("done")

out_df.to_csv("number_of_tokens.csv", index=False)