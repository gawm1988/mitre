import argparse
import pandas as pd
from sklearn.decomposition import PCA

parser = argparse.ArgumentParser()
parser.add_argument('--file', type=str, required=True)
parser.add_argument('--dimensions', type=int, default=50)
args = parser.parse_args()

embeddings_df = pd.read_csv(f"./resources/embeddings/{args.file}")

ids = embeddings_df["ID"].astype(str)
embeddings_df = embeddings_df.drop(columns=["ID"])

n_components = args.dimensions
pca = PCA(n_components=n_components)
reduced_embeddings = pca.fit_transform(embeddings_df)

columns = [f"PCA{i}" for i in range(n_components)]
reduced_df = pd.DataFrame(reduced_embeddings,
                          columns=columns)
reduced_df.insert(0, "ID", ids.values)

reduced_df.to_csv(f"./resources/embeddings/{args.file[:-7]}_{n_components}.csv", index=False)