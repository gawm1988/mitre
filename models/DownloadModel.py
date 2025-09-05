import argparse
from sentence_transformers import SentenceTransformer

parser = argparse.ArgumentParser()
parser.add_argument('--model_name', type=str, required=True)
parser.add_argument('--model_path', type=str)

args = parser.parse_args()

model_path = args.model_path+'/' if args.model_path else 'sentence-transformers/'

model = SentenceTransformer(model_path+args.model_name)
model.save(f'./models/{args.model_name}', args.model_name)
print(f"Model '{args.model_name}' saved successfully.")