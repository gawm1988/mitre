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

result_ids = []
result_clusters = []
result_probabilities = []
result_descriptions = []

for j in range(max_cluster+1):
    cluster_list = []
    text = ""
    for i, row in cluster_df.iterrows():
        if row["cluster"] == j:
            cluster_list.append(row["ID"])
            result_ids.append(row["ID"])
            result_clusters.append(row["cluster"])
            result_descriptions.append(techniques_df.loc[row["ID"], "text_clean"])
            if (has_probability):
                text = f"{text}{row["ID"]} ({row["probability"]}): {techniques_df.loc[row["ID"], "text_clean"]} \n"
                result_probabilities.append(row["probability"])
            else:
                text = f"{text}{row["ID"]}: {techniques_df.loc[row["ID"], "text_clean"]} \n"
                result_probabilities.append("na")
    if cluster_list.__len__() == 1:
        result_ids.pop()
        result_clusters.pop()
        result_descriptions.pop()
        result_probabilities.pop()
    else:
        result_list.append({"cluster": j, "IDs": cluster_list})
        with open(result_file, "a") as file:
            file.write(f"Cluster {j} [ID (probability): description]\n{text}\n")

result = {'id': result_ids, 'cluster': result_clusters, 'probabilitiy': result_probabilities, 'description': result_descriptions}
result_df = pd.DataFrame(result)

output_path = f"./resources/clustering/results_{args.file}"
result_df.to_csv(output_path)

print(result_df)

result_df.to_csv(f"./resources/clustering/{args.file[:-4]}_clusters.csv", index=False)