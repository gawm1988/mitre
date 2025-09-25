"""
This script creates numerical vector representations of the technique descriptions.
Texts whose token count exceeds the model limit (max_sequence_length) are first divided into smaller chunks with overlap
and aggregated using mean pooling.

The embeddings are saved in a new DataFrame in the corresponding ./resource/{model_name}/embeddings folder.
"""
import argparse
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument('--model_name', type=str, required=True)
args = parser.parse_args()

# Sentence-Transformer
model = SentenceTransformer(f"./models/{args.model_name}")
max_seq_len = model.max_seq_length
print(f"max sequence length: {max_seq_len}")

# Tokenizer
tok = model.tokenizer

chunked_count = 0

# Chunk-Parameter relative to max_seq_len
CHUNK = max(64, int(0.75 * max_seq_len))
print(f"Chunk size: {CHUNK}")
OVERLAP = max(16, int(0.15 * max_seq_len))
print(f"Overlap size: {OVERLAP}")

df = pd.read_csv("./resources/techniques_clean.csv", encoding="utf-8")

def chunk_by_tokens(text, chunk_size=CHUNK, overlap=OVERLAP):
    ids = tok.encode(text, add_special_tokens=False)
    n = len(ids)
    chunks = []
    start = 0
    while start < n:
        end = min(start + chunk_size, n)
        piece_ids = ids[start:end]
        chunks.append(tok.decode(piece_ids))
        if end == n:
            break
        start = end - overlap
    return chunks

def embed_document(text):
    ids = tok.encode(text, add_special_tokens=False)

    # Number of token < max_seq_len:
    if len(ids) <= max_seq_len:
        vec = model.encode([text], normalize_embeddings=True)[0]
        return vec, False

    # Number of token < max_seq_len: Chunks + length-weighted Mean
    chunks = chunk_by_tokens(text)
    embs, weights = [], []
    for ch in chunks:
        emb = model.encode([ch], normalize_embeddings=True)[0]
        embs.append(emb)
        weights.append(len(tok.encode(ch, add_special_tokens=False)))
    embs = np.vstack(embs)
    weights = np.array(weights, dtype=np.float32)
    doc_vec = (embs * weights[:, None]).sum(axis=0) / weights.sum()
    # normalize L2
    doc_vec /= np.linalg.norm(doc_vec)
    return doc_vec, True

print("Create embeddings:")
doc_embeddings = []
for text in tqdm(df["text"].tolist(), total=len(df)):
    vec, was_chunked = embed_document(text)
    doc_embeddings.append(vec)
    if was_chunked:
        chunked_count += 1

doc_embeddings = np.vstack(doc_embeddings)

print(f"Chunked texts: {chunked_count} / {len(df)}")

embeddings_df = pd.DataFrame(doc_embeddings)
embeddings_df.insert(0, "ID", df["ID"].values)
embeddings_df.sort_values("ID", inplace=True)
out_path = f"./resources/{args.model_name}/embeddings/{model.get_sentence_embedding_dimension()}.csv"
embeddings_df.to_csv(out_path, index=False)
print(f"Embeddings saved ➜ {out_path}")
