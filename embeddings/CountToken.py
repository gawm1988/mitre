import pandas as pd
from transformers import AutoTokenizer
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--file', type=str, required=True)
parser.add_argument('--model_name', type=str, default='all-MiniLM-L6-v2')
args = parser.parse_args()

CSV_PATH = f"./resources/{args.file}"
df = pd.read_csv(CSV_PATH)

# Tokenizer
tok = AutoTokenizer.from_pretrained(f"./models/{args.model_name}")

def n_tokens(text: str) -> int:
    return len(tok(text, add_special_tokens=False)["input_ids"])


token_counts = df["text"].apply(n_tokens)

out_df = pd.DataFrame({
    "token_count": token_counts,
    "text": df["text"]
}).reset_index(drop=True)

print("done")

out_df.to_csv(f"./resources/{args.model_name}/number_of_tokens.csv", index=False)