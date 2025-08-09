# Scopus Search Index

This project creates a searchable index of Scopus journal data for academic research.

## 🚀 What Was Fixed

The original `Step2_build_faiss.py` had several issues:

1. **Large Excel file handling**: The 10.9MB Excel file with 47,758 rows was causing memory issues
2. **Model download problems**: The HuggingFace sentence transformer model was corrupted in cache
3. **No progress indicators**: Long operations had no feedback
4. **No error handling**: Script would crash on any data issues

## ✅ Solution Implemented

### Files Created:

1. **`Step2_full_dataset.py`** - Main script that processes the complete dataset
2. **`search_scopus.py`** - Interactive search interface
3. **`scopus_search_index.pkl`** - Generated search index (32.4 MB)

### Key Improvements:

- **Robust data loading**: Handles large Excel files efficiently
- **TF-IDF based search**: Uses scikit-learn for reliable text search (instead of problematic transformers)
- **Progress indicators**: Shows progress for all long operations
- **Error handling**: Graceful handling of data issues
- **Memory optimization**: Processes data efficiently without memory overflow
- **Interactive search**: Easy-to-use search interface

## 📊 Dataset Statistics

- **Total journals**: 47,758
- **Search features**: 10,000 TF-IDF features
- **Index sparsity**: 99.73% (very efficient storage)
- **Search time**: Sub-second response for most queries

## 🔍 How to Use

### 1. Create the Search Index

```bash
python Step2_full_dataset.py
```

This will:
- Load all 47,758 journal entries from `ext_list_Jul_2025.xlsx`
- Create searchable text representations
- Build TF-IDF vectors for semantic search
- Save the index to `scopus_search_index.pkl`

### 2. Search the Index

```bash
python search_scopus.py
```

This starts an interactive search interface where you can:
- Enter search queries (e.g., "computer science artificial intelligence")
- Use `--details` flag for detailed results
- Use `--count N` to get N results
- Type `quit` to exit

### 3. Programmatic Usage

```python
from search_scopus import ScopusSearchEngine

# Initialize search engine
engine = ScopusSearchEngine()

# Search for journals
results = engine.search("machine learning", top_k=5)

# Print results
engine.print_results(results, show_details=True)
```

## 📋 Search Results Include

- Journal title and publisher
- Source type (Journal, Book Series, etc.)
- ISSN/eISSN numbers
- Open access status
- Subject area codes (ASJC)
- Coverage information
- Language codes
- Similarity scores

## 🎯 Example Searches

The system works well for queries like:
- "computer science artificial intelligence"
- "medical health journal"
- "environmental science climate"
- "economics finance business"
- "physics engineering"

## 🔧 Technical Details

- **Search Method**: TF-IDF with cosine similarity
- **Features**: 10,000 most important terms (1-2 word combinations)
- **Language**: English stopwords removed
- **Minimum frequency**: Terms must appear in at least 5 documents
- **Maximum frequency**: Terms in >95% of documents are ignored

## 🚧 Future Improvements

1. Could add FAISS for faster similarity search on very large queries
2. Could implement more advanced embeddings (BERT, etc.) when model issues are resolved
3. Could add filters (by publisher, open access status, etc.)
4. Could add export functionality for search results

The current solution provides fast, reliable search across the entire Scopus journal database!
