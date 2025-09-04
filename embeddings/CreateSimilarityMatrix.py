import argparse
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


parser = argparse.ArgumentParser()
parser.add_argument('--file', type=str, required=True)
args = parser.parse_args()

embeddings_df = pd.read_csv(f"./resources/embeddings/{args.file}")

ids = embeddings_df["ID"].astype(str)
embeddings_df = embeddings_df.drop(columns=["ID"])

similarity_matrix = cosine_similarity(embeddings_df.values)

similarity_df = pd.DataFrame(
    similarity_matrix,
    index=ids,
    columns=ids
)

output_path = f"./resources/similarity_matrix/{args.file}"
similarity_df.to_csv(output_path)

print(f"Similarity-matrix saved ➜ {output_path}")
