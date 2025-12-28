# Offline Model Setup Guide

This guide helps you download and cache HuggingFace models locally so the app works without internet connection.

## Quick Fix

Run this Python script to download all required models:

```python
# download_models.py
from sentence_transformers import SentenceTransformer
from transformers import pipeline

print("Downloading models...")

# Download embedding model (used in scoring.py)
print("\n1. Downloading embedding model: all-mpnet-base-v2")
model = SentenceTransformer('all-mpnet-base-v2')
print("✓ Embedding model downloaded")

# Download NER model (used in parser.py for entity recognition)
print("\n2. Downloading NER model: dslim/bert-base-NER")
try:
    ner = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")
    print("✓ NER model downloaded")
except Exception as e:
    print(f"⚠️ NER model failed: {e}")

print("\n✅ All models downloaded! They are now cached locally.")
print("You can run the app offline now.")
```

## How to Use

1. **Make sure you're online** (one-time setup)
2. **Activate your virtual environment:**

   ```bash
   venv\Scripts\activate
   ```

3. **Run the download script:**

   ```bash
   python download_models.py
   ```

4. **Models will be cached** in:
   - Windows: `C:\Users\<username>\.cache\huggingface\`
   - The app will use these cached models automatically

## Alternative: Manual Fix

If you prefer, just run the app once while connected to internet. The models will download automatically and be cached for future offline use.

## What Gets Fixed

✅ This warning will disappear:

```
WARNING: No sentence-transformers model found with name...
ERROR: Embedding model failed: We couldn't connect to 'https://huggingface.co'
```

## Note

The app currently works fine with fallback methods even without the models, but having them downloaded improves:

- Resume parsing accuracy (better entity recognition)
- Scoring accuracy (better semantic matching)
