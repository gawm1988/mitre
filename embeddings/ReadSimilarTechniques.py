"""
This script filters all tupels of vectors that have a cosine similarity score greater than a given threshold (by default 0.75)
Technique-sub-technique relationships are excluded.
"""
import argparse
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('--model_name', type=str, required=True)
parser.add_argument('--dimensions', type=int, required=True)
parser.add_argument('--threshold', type=float, default=0.75)
args = parser.parse_args()

threshold = args.threshold

similarity_matrix_df = (pd.read_csv(f"./resources/{args.model_name}/similarity/sim_matrix_{args.dimensions}.csv")
                        .set_index("ID")
                        .apply(pd.to_numeric, errors="coerce"))

data = []

for row_id, row in similarity_matrix_df.iterrows():
    for col_id in similarity_matrix_df.columns:
        s0 = row_id[0:5]
        s1 = col_id[0:5]
        if s0 == s1:                        # skip selves and sub-techniques
            continue
        val = similarity_matrix_df.loc[row_id, col_id]
        if pd.notna(val) and val >= threshold:
            if [col_id, row_id, float(val)] in data:
                continue
            data.append([row_id, col_id, float(val)])

pairs_df = pd.DataFrame(data, columns=["id", "similar_id", "similarity"])

out_path = f"./resources/{args.model_name}/similarity/sim_tupels_{args.dimensions}_{threshold}.csv"
pairs_df.to_csv(out_path, index=False)

print(f"Similarities saved ➜ {out_path}")
