# Semantic analysis of the MITRE ATT&CK framework through reclustering

## Getting started
### Dependencies
Create a [HuggingFace](https://huggingface.co/) access token and install the dependencies (pip freeze > requirements.txt)
```bash
pip install -r requirements.txt
```

### Select a language model
Select a sentence-transformer model from [huggingface.co](https://huggingface.co/sentence-transformers/models) and download it by executing:

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
Download latest version (v17) of the ATT&CK matrix (.xlsx) from [MITRE](https://attack.mitre.org/resources/attack-data-and-tools/).
Read the ID, title and description, tactics from the matrix and save them as a new list techniques.csv:
```bash
python3 ./resources/ReadTechniques.py
```

### Clean Data
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
```bash
python3 ./embeddings/PreprocessData.py
```

## Create Embeddings
Create embeddings for each technique. The models can handle only a max sequence of tokens. 
Texts that exceed this limit will be chunked into smaller parts and aggregated by weighted mean pooling 
to keep the semantic of the sentences. The Embeddings will be saved in ./resources/embeddings/{model-name}\_{dim_size}.csv
```bash
python3 ./embeddings/CreateEmbeddings.py --model_name all-MiniLM-L6-v2
```
## Build similarity matrix
Create a matrix which lists pairwise similarities of the techniques. 
```bash
python3 ./embeddings/CreateSimilarityMatrix.py --file all-MiniLM-L6-v2_384.csv
```

## Read similar techniques
Read the techniques that exceed a given cosine similarity score (default 0.75). Technique - sub-techniques relationships will be ignored: <br>
\>= 0.85 → Duplicates/Paraphrases (almost identical) <br>
0.75 - 0.85 → clearly semantically similar

```bash
python3 ./embeddings/FindSimilarTechniques.py --file all-MiniLM-L6-v2_384.csv --threshold 0.85
```
For example: Using the all-MiniLM-L6-v2 model and setting the threshold to 0.9, 35 similar technique descriptions will be found:

| TacticID  | SimilarID  | Cosine Similarity  |
|-----------|------------|--------------------|
| T1498     | T1499      | 0.9105383009375732 |
| T1566     | T1598      | 0.9035376388807717 |
| T1583.007 | T1584.007  | 0.9844308065023536 |
| T1587.002 | T1588.003  | 0.9042584992078372 |
| T1589.003 | T1591      | 0.9149459772306404 |
| T1589.003 | T1591.004  | 0.922270917118881  |
| T1590     | T1596.001  | 0.9159396636800252 |
| T1590.001 | T1596      | 0.912517647203262  |
| T1590.001 | T1596.002  | 0.9161022405257429 |
| T1590.002 | T1596.001  | 0.9026267153817532 |
| T1590.004 | T1591.001  | 0.9051158469712368 |
| T1590.004 | T1591.002  | 0.9005931435249647 |
| T1590.004 | T1592.004  | 0.9092774337638656 |
| T1590.004 | T1596      | 0.9065141772572728 |
| T1590.004 | T1596.001  | 0.9094237908646816 |
| T1590.004 | T1596.005  | 0.90864370057196   |
| T1591     | T1593      | 0.9223212730118456 |
| T1591     | T1596      | 0.9162950721643308 |
| T1591.001 | T1593      | 0.9150870529498456 |
| T1591.002 | T1593      | 0.910255230856254  |
| T1591.002 | T1597.002  | 0.9109264014303432 |
| T1591.004 | T1593      | 0.9054788057680868 |
| T1591.004 | T1597.002  | 0.9021949763964756 |
| T1593     | T1596      | 0.9384679485867252 |
| T1593     | T1596.002  | 0.9039214360752212 |
| T1593     | T1596.005  | 0.9124127179267008 |
| T1593     | T1597      | 0.923864943468214  |
| T1593     | T1597.002  | 0.9042467510560684 |
| T1593.002 | T1596      | 0.9361064295630496 |
| T1593.002 | T1597      | 0.9013583983297324 |
| T1593.002 | T1597.002  | 0.9005568335956395 |
| T1595.001 | T1596.005  | 0.9211910012917508 |
| T1596     | T1597      | 0.9255244640771796 |
| T1596     | T1597.002  | 0.91173788821184   |
| T1596.005 | T1597      | 0.9253922319098944 |

## Reduce dimensionality
Reduce dim space before clustering if necessary
```bash
python3 ./embeddings/PrincipalComponentAnalysis.py --file all-MiniLM-L6-v2_384.csv --dimensions 10
```

## Run cluster algorithms
### HDBSCAN
| Advantages                                                       | Disadvantages                                               |
|:-----------------------------------------------------------------|-------------------------------------------------------------|
| Finds the number of clusters itself (no k required)              | Sensitive to hyperparameter (min_cluster_size, min_samples) |
| Explicit noise, outliers ar labeled \'-1'                        | High noise proportion in high-dimensional embeddings        |
| Works with different densities \& shapes                         |                                                             |
| Provides membership probabilities                                |                                                             |
| Can be run directly on precomputed distances (D = 1 - SimMatrix) |                                                             |

```bash
python3 ./clustering/HDBSCAN.py --file all-MiniLM-L6-v2_384.csv --min_cluster_size 5 --min_samples 2
```

### Agglomerative Clustering

```bash
python3 ./clustering/AgglomerativeClustering.py --file all-MiniLM-L6-v2_384.csv --threshold 0.25 --linkage average
```


### k-means
### Gaussian mixture

## Evaluate cluster
### Read Cluster
```bash
python3 ./clustering/ReadCluster.py --file hdbscan_all-MiniLM-L6-v2_384_min_cluster_size_5.csv
python3 ./clustering/ReadCluster.py --file agc_all-MiniLM-L6-v2_384_threshold_0.25.csv


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

## Suggestions for a good README

Every project is different, so consider which of these sections apply to yours. The sections used in the template are suggestions for most open source projects. Also keep in mind that while a README can be too long and detailed, too long is better than too short. If you think your README is too long, consider utilizing another form of documentation rather than cutting out information.

## Name
Choose a self-explaining name for your project.

## Description
Let people know what your project can do specifically. Provide context and add a link to any reference visitors might be unfamiliar with. A list of Features or a Background subsection can also be added here. If there are alternatives to your project, this is a good place to list differentiating factors.

## Badges
On some READMEs, you may see small images that convey metadata, such as whether or not all the tests are passing for the project. You can use Shields to add some to your README. Many services also have instructions for adding a badge.

## Visuals
Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method.

## Installation
Within a particular ecosystem, there may be a common way of installing things, such as using Yarn, NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible. If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a Requirements subsection.

## Usage
Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## Support
Tell people where they can go to for help. It can be any combination of an issue tracker, a chat room, an email address, etc.

## Roadmap
If you have ideas for releases in the future, it is a good idea to list them in the README.

## Contributing
State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## Authors and acknowledgment
Show your appreciation to those who have contributed to the project.

## License
For open source projects, say how it is licensed.

## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.
