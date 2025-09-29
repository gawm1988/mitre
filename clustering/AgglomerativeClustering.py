"""
Performs Agglomerative Clustering on text embeddings using cosine distance and a user-defined threshold.
Pure Technique/Subtechnique clusters are removed and the remaining clusters are saved as CSV.
Parameters:
    --model_name:   Name of the sentence-transformer model
    --dimensions:   Embedding dimensionality (used to select the correct embedding file)
    --threshold:    Distance threshold for cutting the dendrogram (default: 0.25, corresponds to 1 - similarity)
    --linkage:      Linkage criterion for clustering ("average", "complete", etc.; default: "average")
"""

import argparse
import re
import pandas as pd
from sklearn.cluster import AgglomerativeClustering

parser = argparse.ArgumentParser()
parser.add_argument('--model_name', type=str, required=True)
parser.add_argument('--dimensions', type=int, required=True)
parser.add_argument('--threshold', type=float, default=0.25)
parser.add_argument('--linkage', type=str, default='average')
args = parser.parse_args()

embeddings_df = pd.read_csv(f"./resources/{args.model_name}/embeddings/{args.dimensions}.csv")

ids = embeddings_df["ID"].astype(str)
embeddings_df = embeddings_df.drop(columns=["ID"])

agc = AgglomerativeClustering(
    n_clusters=None,
    metric="cosine",
    linkage=args.linkage,
    distance_threshold=args.threshold   # threshold = 1 - similarity
)

agc.fit(embeddings_df)
labels = agc.labels_

# Result DataFrame: Remove noise and rearrange DataFrame
agc_df = pd.DataFrame({"ID": ids, "cluster": labels})
agc_df = agc_df[agc_df["cluster"] != -1].reset_index(drop=True)
agc_df = agc_df.sort_values(by=["cluster", "ID"]).reset_index(drop=True)

# --- Filter pure Technique<->SubTechnique Cluster
def root(tid: str) -> str:
    tid = str(tid)
    m = re.match(r'^(T\d{4})', tid)
    return m.group(1) if m else tid.split('.')[0]

agc_df["__root"] = agc_df["ID"].map(root)
roots_per_cluster = agc_df.groupby("cluster")["__root"].nunique()
pure_clusters = roots_per_cluster[roots_per_cluster == 1].index.tolist()
agc_df = agc_df[~agc_df["cluster"].isin(pure_clusters)].drop(columns="__root")

print(f"Removed pure Technique/Subtechnique-Cluster: {len(pure_clusters)} → {pure_clusters}")

out_path = f"./resources/{args.model_name}/clustering/agc_{args.dimensions}_{args.threshold}_{args.linkage}.csv"
agc_df.to_csv(out_path, index=False)
print("File saved → ", out_path)
