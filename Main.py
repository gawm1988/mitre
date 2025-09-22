import subprocess
from tqdm import tqdm

def main():
    model_name = "all-mpnet-base-v2"
    model_path = "sentence-transformers"
    dimensions = "768"
    attack_file = "enterprise-attack-v17.1.xlsx"
    text_preprocessing = False
    # =======================

    commands_preprocessing =  [
        # 2) Read techniques from ATT&CK matrix
        ["python3", "./embeddings/preprocessing/ReadTechniques.py",
         "--file", attack_file],

        # 3) Clean data
        ["python3", "./embeddings/preprocessing/CleanData.py",
         "--file", "techniques.csv"],

        # 11) POS Tagging
        ["python3", "./evaluation/PoSTagging.py",
         "--file", "techniques_clean.csv"],
]

    commands = [
        # 1) Download model
        ["python3", "./models/DownloadModel.py",
         "--model_name", model_name, "--model_path", model_path],

        # 4) Count tokens
        ["python3", "./embeddings/CountToken.py",
         "--file", "techniques_clean.csv", "--model_name", model_name],

        # 5) Create embeddings
        ["python3", "./embeddings/CreateEmbeddings.py",
         "--model_name", model_name],

        # 6) Create similarity matrix
        ["python3", "./embeddings/CreateSimilarityMatrix.py",
         "--model_name", model_name, "--dimensions", dimensions],

        # 7) Read similar techniques
        ["python3", "./embeddings/ReadSimilarTechniques.py",
         "--model_name", model_name, "--dimensions", dimensions, "--threshold", "0.85"],

        # 8) (Optional) PCA reduction (hier Beispiel: 10 Dimensionen)
        ["python3", "./embeddings/PrincipalComponentAnalysis.py",
         "--model_name", model_name, "--old_dimensions", dimensions, "--new_dimensions", "10"],

        # 9) HDBSCAN clustering
        ["python3", "./clustering/HDBSCAN.py",
         "--model_name", model_name, "--dimensions", dimensions,
         "--min_cluster_size", "5", "--min_samples", "2"],

        # 10) Agglomerative clustering
        ["python3", "./clustering/AgglomerativeClustering.py",
         "--model_name", model_name, "--dimensions", dimensions,
         "--threshold", "0.2", "--linkage", "average"],

        # 12) Read Clusters (Agglomerative)
        ["python3", "./clustering/ReadCluster.py",
         "--model_name", model_name, "--file", f"agc_{dimensions}_0.2_average.csv"],

        # 13) Read Clusters (HDBSCAN)
        ["python3", "./clustering/ReadCluster.py",
         "--model_name", model_name, "--file", f"hdbscan_{dimensions}_5_2.csv"],
    ]

    if text_preprocessing:
        for cmd in tqdm(commands_preprocessing, "Run preprocessing: "):
            print(f"\n>> Running: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)

    for cmd in tqdm(commands,"Run commands: "):
        print(f"\n>> Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)

if __name__ == "__main__":
    main()
