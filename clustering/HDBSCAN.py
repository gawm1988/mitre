import argparse
import re
import numpy as np
import pandas as pd
import hdbscan

parser = argparse.ArgumentParser()
parser.add_argument('--file', type=str, required=True)
parser.add_argument('--min_cluster_size', type=int, default=5)
parser.add_argument('--min_samples', type=int, default=5)
args = parser.parse_args()

S_df = pd.read_csv(f"./resources/similarity_matrix/{args.file}")
ids = S_df["ID"].astype(str)
S = S_df.drop(columns=["ID"], errors="ignore").apply(pd.to_numeric, errors="coerce").to_numpy(float)

# --- Similarity -> Distance ---
D = 1.0 - S
np.fill_diagonal(D, 0.0)

# --- HDBSCAN (precomputed) ---
hdb = hdbscan.HDBSCAN(min_cluster_size=args.min_cluster_size, min_samples=args.min_samples, metric='precomputed')
labels = hdb.fit_predict(D)
probabilities = hdb.probabilities_

# Result DataFrame: Remove noise and rearrange DataFrame
hdbscan_df = pd.DataFrame({"ID": ids, "cluster": labels, "Probability":probabilities})
hdbscan_df = hdbscan_df[hdbscan_df["cluster"] != -1].reset_index(drop=True)
hdbscan_df = hdbscan_df.sort_values(by=["cluster", "ID"]).reset_index(drop=True)

# --- Filter pure Technique<->SubTechnique Cluster
def root(tid: str) -> str:
    tid = str(tid)
    m = re.match(r'^(T\d{4})', tid)   # extrahiert z. B. "T1080" aus "T1080.001"
    return m.group(1) if m else tid.split('.')[0]

hdbscan_df["__root"] = hdbscan_df["ID"].map(root)
roots_per_cluster = hdbscan_df.groupby("cluster")["__root"].nunique()
pure_clusters = roots_per_cluster[roots_per_cluster == 1].index.tolist()
hdbscan_df = hdbscan_df[~hdbscan_df["cluster"].isin(pure_clusters)].drop(columns="__root")

print(f"Removed pure Technique/Subtechnique-Cluster: {len(pure_clusters)} → {pure_clusters}")

out_path = f"./resources/clustering/hdbscan_{args.file[:-4]}_{args.min_cluster_size}.csv"
hdbscan_df.to_csv(out_path, index=False)
print("File saved → ", out_path)
