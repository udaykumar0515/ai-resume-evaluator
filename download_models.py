# download_models.py
# Run this script once while connected to internet to cache HuggingFace models locally

from sentence_transformers import SentenceTransformer
from transformers import pipeline

print("=" * 60)
print("  HuggingFace Model Downloader")
print("  AI Resume Evaluator - Offline Setup")
print("=" * 60)

# Download embedding model (used in scoring.py)
print("\n[1/2] Downloading embedding model: all-mpnet-base-v2...")
try:
    model = SentenceTransformer('all-mpnet-base-v2')
    print("✅ Embedding model downloaded successfully!")
except Exception as e:
    print(f"❌ Failed to download embedding model: {e}")

# Download NER model (used in parser.py for entity recognition)
print("\n[2/2] Downloading NER model: dslim/bert-base-NER...")
try:
    ner = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")
    print("✅ NER model downloaded successfully!")
except Exception as e:
    print(f"❌ Failed to download NER model: {e}")

print("\n" + "=" * 60)
print("✅ Setup Complete!")
print("=" * 60)
print("\nModels are now cached locally. You can run the app offline.")
print("Run: streamlit run main_app.py")
