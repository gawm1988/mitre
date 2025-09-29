# Semantic analysis of the MITRE ATT&CK framework through reclustering

## Getting started
### Dependencies
Create a [HuggingFace](https://huggingface.co/) access token and install the dependencies 
```bash
pip install -r requirements.txt
```

### Select a language model
Select and download a sentence-transformer model from [huggingface.co](https://huggingface.co/sentence-transformers/models) e.g.:

|          Model | [all-mpnet-base-v2](https://huggingface.co/sentence-transformers/all-mpnet-base-v2) | [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) | [SentSecBERT_10k](https://huggingface.co/QCRI/SentSecBert_10k) |
|---------------:|:-----------------------------------------------------------------------------------:|:---------------------------------------------------------------------------------:|:--------------------------------------------------------------:|
|           Path |                                sentence-transformer                                 |                               sentence-transformer                                |                              QCRI                              |
|     Dimensions |                                         768                                         |                                        384                                        |                              768                               |
| Max_Seq_Lenght |                                         384                                         |                                        256                                        |                              514                               |
|           Size |                                       120 MB                                        |                                       80 MB                                       |                               ?                                |

```bash
python3 ./models/DownloadModel.py --model_name all-MiniLM-L6-v2 --model_path sentence-transformers
```

### Read data from MITRE ATT&CK matrix
Download latest version (v17) of the ATT&CK matrix (.xlsx) from [MITRE](https://attack.mitre.org/resources/attack-data-and-tools/). Read the id, title and description, tactics from the matrix and save them as a new dataframe [techniques.csv](./resources/techniques.csv):
```bash
python3 ./embeddings/preprocessing/ReadTechniques.py --file enterprise-attack-v17.1.xlsx
```

### Clean Data
Prepare the texts for further processing by performing:
- Remove control character (especially \n, \t)
- Remove line breaks
- Remove URLs & Markdown-Links, keep link text
- Remove HTML-Tags (\<p>, \<br>, …)
- Remove Inline-Code-Backticks \`vim-cmd`)
- Remove Multiple spaces/tabs
- Trim leading/trailing spaces
- Remove List marker (- , * , 1.)
- Remove Non-breaking space (\u00A0)
- Remove Markdown-Headers (# …)
The clean texts can be used to create text embeddings. Output dataframe [techniques_clean.csv](resources/techniques_clean.csv)
```bash
python3 ./embeddings/preprocessing/CleanData.py --file techniques.csv
```

## Create numerical representations
### Count number of token
Sentence transformers can only process a limited number of tokens (`model.max_seq_length`). The number of tokens per text can be displayed using the following script.
```bash
python3 ./embeddings/CountToken.py --file techniques_clean.csv --model_name all-MiniLM-L6-v2
```

### Create Embeddings
Create text-embeddings for each technique. Texts whose tokens exceed max_sequence_length are chunked into smaller parts with overlap and aggregated by weighted mean pooling to keep the semantic of the sentences. The Embeddings will be saved in a new dataframe in the embeddings folder of the corresponding model as [numberOfDimensions.csv](./resources/all-MiniLM-L6-v2/embeddings/384.csv)
```bash
python3 ./embeddings/CreateEmbeddings.py --model_name all-MiniLM-L6-v2
```
## Build similarity matrix
Precompute a matrix which lists pairwise cosine similarities between the text embeddings. The matrix can be used as input parameter for clustering algorithms and is stored in the corresponding similarity folder of each model as [sim_matrix_numberOfDimensions.csv](./resources/all-MiniLM-L6-v2/similarity/sim_matrix_384.csv).
Cosine similarity between two vectors is defined as: <br>
    $$cos(x,y) = x · y / (||x|| * ||y||)$$
where:
    <center>
    x · y is the dot product of vectors x and y.<br>
    ||x|| is the Euclidean length (magnitude) of vector x.<br>
    ||y|| is the Euclidean length (magnitude) of vector y.
    </center>
```bash
python3 ./embeddings/CreateSimilarityMatrix.py --model_name all-MiniLM-L6-v2 --dimensions 384
```

## Read similar techniques
Filter tuples of techniques that exceed a given cosine similarity score (default 0.75). Technique - sub-techniques relationships will be ignored. A score of greater than 0.85 indicates duplicates or paraphrases (almost identical), between 0.75 - 0.85 a clearly semantically similarity. The tupels are saved in a file within the similarity folder of each model: [sim_tupel_numberOfDimensions.csv](./resources/all-MiniLM-L6-v2/similarity/sim_tupels_384_0.85.csv)
```bash
python3 ./embeddings/ReadSimilarTechniques.py --model_name all-MiniLM-L6-v2 --dimensions 384 --threshold 0.85
```

## Reduce dimensionality
The execution of clustering algorithms can involve high computational costs if the used distance metric they is not precomputed in advance. A common method is Principal Component Analysis (PCA) to reduce the dimensionality of the vector space before clustering. PCA transforms a dataset with many correlated variables into a smaller set of uncorrelated variables, while retaining most of the original information (variance). 
```bash
python3 ./embeddings/PrincipalComponentAnalysis.py --model_name all-MiniLM-L6-v2 --old_dimensions 384 --new_dimensions 10
```

## Run clustering algorithms
Clustering algorithms are used to automatically structure unordered data into groups (clusters) so that similar objects are grouped together and dissimilar ones are separated. They are useful when patterns are to be derived from the data itself.<br><br>
Classic clustering algorithms such as k-means are less suitable for detecting semantic similarities between Mitre ATT\&CK techniques.  i) It is often necessary to know the number of clusters in advance, ii) convex, spherical clusters are assumed and iii) each point will be assigned to a fixed cluster.<br><br>
To address these challenges, we focus instead on density-based and hierarchical clustering algorithms.

### HDBSCAN
HDBSCAN (Hierarchical Density-Based Spatial Clustering of Applications with Noise) is a density-based clustering method that does not require the number of clusters to be specified, recognises clusters of any shape and explicitly treats noise as a separate category.
| Advantages                                                       | Disadvantages                                               |
|:-----------------------------------------------------------------|-------------------------------------------------------------|
| Finds the number of clusters itself (no k required)              | Sensitive to hyperparameter (min_cluster_size, min_samples) |
| Explicit noise, outliers ar labeled \'-1'                        | High noise proportion in high-dimensional embeddings        |
| Works with different densities \& shapes                         |                                                             |
| Provides membership probabilities                                |                                                             |
| Can be run directly on precomputed distances (D = 1 - SimMatrix) |                                                             |

```bash
python3 ./clustering/HDBSCAN.py --model_name all-MiniLM-L6-v2 --dimensions 384 --min_cluster_size 5 --min_samples 2
```

### Agglomerative Clustering
Agglomerative clustering is a hierarchical process in which similar data points or clusters are gradually merged, creating a cluster hierarchy from which the desired cluster structure can be derived by means of a suitable cut.

| Advantages                                                                     | Disadvantages                                                    |
|:-------------------------------------------------------------------------------|------------------------------------------------------------------|
| Interpretable (dendrogram shows hierarchy and possible cut-offs)               | Requires manually selected threshold value or number of clusters |
| Well suited for small to medium-sized data sets                                | Sensitive to outliers (no noise concept)                         |
| Flexible in the choice of distance and linkage (average, complete, ward, etc.) |                                                                  |


```bash
python3 ./clustering/AgglomerativeClustering.py --model_name all-MiniLM-L6-v2 --dimensions 384 --threshold 0.2 --linkage average
```

## Evaluate cluster
### Part of Speech Tagging
Use [spaCy](https://spacy.io/usage/linguistic-features#pos-tagging) part of speech tagging to get lists of  verbs, adverbs, auxiliary verbs, proper_nouns, nouns and unknown words in alphabetically order
```bash
python3 ./evaluation/PoSTagging.py --file techniques_clean.csv
```

### Read Cluster
```bash
python3 ./clustering/ReadCluster.py --model_name all-MiniLM-L6-v2 --file agc_384_0.2_average.csv
python3 ./clustering/ReadCluster.py --model_name all-MiniLM-L6-v2 --file hdbscan_384_5_2.csv
```



### External metric 
- [ ] to compare to ground truth
### internal metric 
- [ ] detect outliers and uncertain tactic assignment

### Compare results manually
- [ ] how do the results differ from similarity in human language?

***
```
cd existing_repo
git remote add origin https://gitlab.uni-oldenburg.de/fawi8699/mitre.git
git branch -M main
git push -uf origin main
```

***

# Editing this README

When you're ready to make this README your own, just edit this file and use the handy template below (or feel free to structure it however you want - this is just a starting point!). Thanks to [makeareadme.com](https://www.makeareadme.com/) for this template.

## Roadmap
If you have ideas for releases in the future, it is a good idea to list them in the README.

## License
For open source projects, say how it is licensed.

## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.
