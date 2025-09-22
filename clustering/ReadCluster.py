import argparse
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('--model_name', type=str, required=True)
parser.add_argument('--file', type=str, required=True)
args = parser.parse_args()

in_csv = f"./resources/{args.model_name}/clustering/{args.file}"
tech_csv = "./resources/techniques_clean_pos.csv"
txt_out = f"./resources/{args.model_name}/clustering/{args.file[:-4]}_cluster.txt"
csv_out = f"./resources/{args.model_name}/clustering/{args.file[:-4]}_clusters.csv"

cluster_df = pd.read_csv(in_csv)
techniques_df = pd.read_csv(tech_csv, index_col="ID")

has_probability = 'probability' in cluster_df.columns
if not has_probability:
    cluster_df['probability'] = pd.NA

df = cluster_df.merge(
    techniques_df,
    left_on='ID', right_index=True,
    how='left'
)

df = df.sort_values(['cluster', 'ID']).reset_index(drop=True)

valid_clusters = df.groupby('cluster').size()
valid_clusters = valid_clusters[valid_clusters > 1].index
df_valid = df[df['cluster'].isin(valid_clusters)].copy()

result_df = (
    df_valid[['ID', 'cluster', 'probability', 'text', 'VERB', 'ADV', 'PROPN', 'NOUN', 'X']]
)

result_df['probability'] = result_df['probability'].astype(object).where(result_df['probability'].notna(), 'na')

result_df.to_csv(csv_out, index=False, encoding="utf-8")


# Save txt
lines = [f"{args.file}\n"]  # Header

def _fmt_row(row):
    return f"{row['id']} ({row['probability']}): {row['description']}"

for clus, grp in df_valid.groupby('cluster', sort=True):
    body = "\n".join(_fmt_row(r) for _, r in grp.rename(columns={'ID':'id','text':'description'}).iterrows())
    lines.append(f"Cluster {clus} [ID (probability): description]\n{body}\n")

with open(txt_out, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

result_list = (
    df_valid.groupby('cluster')['ID']
    .apply(list)
    .reset_index()
    .rename(columns={'ID': 'IDs'})
    .to_dict('records')
)
