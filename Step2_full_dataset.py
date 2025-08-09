import os
import pandas as pd
from tqdm import tqdm
import pickle

print("🚀 Full Dataset FAISS Index Builder")
print("=" * 50)

# ---------------------------
# 1. Load the complete Excel file
# ---------------------------
csv_path = "ext_list_Jul_2025.xlsx"
print(f"📊 File size: {os.path.getsize(csv_path) / (1024*1024):.1f} MB")

try:
    print("📥 Loading complete dataset...")
    df = pd.read_excel(csv_path, engine='openpyxl')
    print(f"✅ Loaded {len(df):,} rows with {len(df.columns)} columns")
except Exception as e:
    print(f"❌ Error loading Excel file: {e}")
    print("The Excel file might be too large or corrupted.")
    exit(1)

# ---------------------------
# 2. Create text representations
# ---------------------------
print("🔤 Creating text representations...")
texts = []
metadatas = []

for idx, (_, row) in enumerate(tqdm(df.iterrows(), desc="Processing rows", total=len(df))):
    try:
        # Create comprehensive text
        text_parts = []
        
        # Add key fields with better formatting
        if pd.notna(row.get('Source Title')):
            text_parts.append(f"Title: {row['Source Title']}")
            
        if pd.notna(row.get('Publisher')):
            text_parts.append(f"Publisher: {row['Publisher']}")
            
        if pd.notna(row.get('Source Type')):
            text_parts.append(f"Type: {row['Source Type']}")
            
        if pd.notna(row.get('All Science Journal Classification Codes (ASJC)')):
            text_parts.append(f"Subject Areas: {row['All Science Journal Classification Codes (ASJC)']}")
            
        if pd.notna(row.get('Coverage')):
            text_parts.append(f"Coverage: {row['Coverage']}")
            
        if pd.notna(row.get('Open Access Status')):
            text_parts.append(f"Open Access: {row['Open Access Status']}")
            
        if pd.notna(row.get('Article Language in Source (Three-Letter ISO Language Codes)')):
            text_parts.append(f"Language: {row['Article Language in Source (Three-Letter ISO Language Codes)']}")
        
        text = " | ".join(text_parts) if text_parts else "No information available"
        texts.append(text)
        
        # Create comprehensive metadata
        metadata = {
            'sourcerecord_id': str(row.get('Sourcerecord ID', '')),
            'source_title': str(row.get('Source Title', '')),
            'issn': str(row.get('ISSN', '')),
            'eissn': str(row.get('EISSN', '')),
            'publisher': str(row.get('Publisher', '')),
            'source_type': str(row.get('Source Type', '')),
            'active_status': str(row.get('Active or Inactive', '')),
            'open_access': str(row.get('Open Access Status', '')),
            'coverage': str(row.get('Coverage', '')),
            'asjc_codes': str(row.get('All Science Journal Classification Codes (ASJC)', '')),
            'language': str(row.get('Article Language in Source (Three-Letter ISO Language Codes)', '')),
            'row_index': idx
        }
        metadatas.append(metadata)
        
    except Exception as e:
        print(f"Warning: Error processing row {idx}: {e}")
        # Add minimal entry for problematic rows
        texts.append("Error processing this entry")
        metadatas.append({'row_index': idx, 'error': str(e)})

print(f"✅ Created {len(texts):,} text entries")

# ---------------------------
# 3. Create TF-IDF index
# ---------------------------
print("🧮 Creating TF-IDF vectors...")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    
    # Create TF-IDF vectors with optimized parameters for large dataset
    vectorizer = TfidfVectorizer(
        max_features=10000,  # Increased for larger dataset
        stop_words='english',
        ngram_range=(1, 2),
        max_df=0.95,
        min_df=5,  # Increased minimum frequency
        lowercase=True,
        strip_accents='unicode'
    )
    
    print("Computing TF-IDF matrix...")
    tfidf_matrix = vectorizer.fit_transform(texts)
    print(f"✅ TF-IDF matrix created: {tfidf_matrix.shape}")
    print(f"   - {tfidf_matrix.shape[0]:,} documents")
    print(f"   - {tfidf_matrix.shape[1]:,} features")
    print(f"   - {tfidf_matrix.nnz:,} non-zero values")
    print(f"   - Sparsity: {(1 - tfidf_matrix.nnz / (tfidf_matrix.shape[0] * tfidf_matrix.shape[1])) * 100:.2f}%")
    
except ImportError:
    print("❌ scikit-learn not installed. Install with: pip install scikit-learn")
    exit(1)
except Exception as e:
    print(f"❌ Error creating TF-IDF vectors: {e}")
    exit(1)

# ---------------------------
# 4. Save the index
# ---------------------------
print("💾 Saving index data...")

try:
    index_data = {
        'tfidf_matrix': tfidf_matrix,
        'vectorizer': vectorizer,
        'texts': texts,
        'metadatas': metadatas,
        'feature_names': vectorizer.get_feature_names_out(),
        'dataset_info': {
            'total_documents': len(texts),
            'total_features': len(vectorizer.get_feature_names_out()),
            'original_rows': len(df),
            'source_file': csv_path
        }
    }
    
    with open('scopus_search_index.pkl', 'wb') as f:
        pickle.dump(index_data, f)
    
    print("✅ Complete index saved to 'scopus_search_index.pkl'")
    print(f"   File size: {os.path.getsize('scopus_search_index.pkl') / (1024*1024):.1f} MB")
    
except Exception as e:
    print(f"❌ Error saving index: {e}")
    exit(1)

# ---------------------------
# 5. Test the search functionality
# ---------------------------
print("\n🔍 Testing search functionality...")

def search_scopus(query, top_k=5):
    """Search the Scopus index for relevant journals."""
    try:
        from sklearn.metrics.pairwise import cosine_similarity
        
        # Transform query
        query_vec = vectorizer.transform([query])
        
        # Calculate similarities
        scores = cosine_similarity(query_vec, tfidf_matrix).flatten()
        
        # Get top results
        top_indices = scores.argsort()[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0:  # Only return results with some similarity
                results.append({
                    'score': scores[idx],
                    'text': texts[idx],
                    'metadata': metadatas[idx]
                })
        
        return results
    except Exception as e:
        print(f"Search error: {e}")
        return []

# Test searches
test_queries = [
    "computer science artificial intelligence",
    "medical health journal",
    "physics engineering",
    "environmental science climate",
    "economics finance business"
]

for query in test_queries:
    print(f"\n📝 Query: '{query}'")
    print("-" * 40)
    
    results = search_scopus(query, top_k=3)
    
    if results:
        for i, result in enumerate(results, 1):
            print(f"{i}. Score: {result['score']:.4f}")
            print(f"   Title: {result['metadata']['source_title']}")
            print(f"   Publisher: {result['metadata']['publisher']}")
            print(f"   Type: {result['metadata']['source_type']}")
            print()
    else:
        print("   No relevant results found.")

print("🎉 Success! Your Scopus search index is ready.")
print("\nTo use the index in other scripts:")
print("1. Load with: index_data = pickle.load(open('scopus_search_index.pkl', 'rb'))")
print("2. Use the search_scopus function above as a template")
print("3. Access metadata for detailed information about each journal")
