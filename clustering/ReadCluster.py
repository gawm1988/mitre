import argparse
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('--file', type=str, required=True)
args = parser.parse_args()

cluster_df = pd.read_csv(f"./resources/clustering/{args.file}")
max_cluster = cluster_df["cluster"].iloc[-1]
has_probability = (lambda cluster_df: True if 'probability' in cluster_df.columns else False)(cluster_df)

techniques_df = pd.read_csv(f"./resources/techniques_clean.csv", index_col="ID")
result_list = []
result_file = f"./resources/clustering/{args.file[:-4]}.txt"

with open(result_file, "w") as file:
    file.write(f"{args.file} \n\n")

for j in range(max_cluster+1):
    cluster_list = []
    text = ""
    for i, row in cluster_df.iterrows():
        if row["cluster"] == j:
            cluster_list.append(row["ID"])
            if (has_probability):
                text = f"{text}{row["ID"]} ({row["probability"]}): {techniques_df.loc[row["ID"], "text_clean"]} \n"
            else:
                text = f"{text}{row["ID"]}: {techniques_df.loc[row["ID"], "text_clean"]} \n"
    if cluster_list.__len__() > 0:
        result_list.append({"cluster": j, "IDs": cluster_list})
        with open(result_file, "a") as file:
            file.write(f"Cluster {j} [ID (probability): description]\n{text}\n")

result_df = pd.DataFrame(result_list)

print(result_df)

result_df.to_csv(f"./resources/clustering/{args.file[:-4]}_clusters.csv", index=False)