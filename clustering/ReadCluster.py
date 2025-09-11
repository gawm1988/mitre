import argparse

import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('--file', type=str, required=True)
args = parser.parse_args()

cluster_df = pd.read_csv(f"./resources/clustering/{args.file}")

max_cluster = cluster_df["cluster"].iloc[-1]


result_list = []

for j in range(max_cluster+1):
    cluster_list = []
    for i, row in cluster_df.iterrows():
        if row["cluster"] == j:
            cluster_list.append(row["ID"])
    if cluster_list.__len__() > 0:
        result_list.append({"cluster": j, "IDs": cluster_list})

result_df = pd.DataFrame(result_list)

print(result_df)

result_df.to_csv(f"./resources/clustering/{args.file[:-4]}_clusters.csv", index=False)