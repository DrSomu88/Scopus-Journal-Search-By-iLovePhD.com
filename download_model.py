from sentence_transformers import SentenceTransformer

print("📥 Downloading model, please wait...")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
print("✅ Model downloaded successfully!")
