"""
Script to download and save a sentence-transformer model from [huggingface.co](https://huggingface.co/sentence-transformers).
"""

import argparse
from sentence_transformers import SentenceTransformer
import os


parser = argparse.ArgumentParser()
parser.add_argument('--model_name', type=str, required=True)
parser.add_argument('--model_path', type=str)

args = parser.parse_args()

model_path = args.model_path+'/' if args.model_path else 'sentence-transformers/'

try:
    os.mkdir(f"./resources/{args.model_name}")
    os.mkdir(f"./resources/{args.model_name}/embeddings")
    os.mkdir(f"./resources/{args.model_name}/similarity")
    os.mkdir(f"./resources/{args.model_name}/clustering")
    os.mkdir(f"./resources/{args.model_name}/evaluation")
except FileExistsError:
    print("Note: Directories already exist!")

model = SentenceTransformer(model_path+args.model_name)
model.save(f'./models/{args.model_name}', args.model_name)
print(f"Model '{args.model_name}' saved successfully.")