import os
import pandas as pd
from sentence_transformers import SentenceTransformer
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from tqdm import tqdm

# ---------------------------
# 1. Load your Excel file efficiently
# ---------------------------
csv_path = "ext_list_Jul_2025.xlsx"  # Update if needed

print("📊 Loading Excel file...")
print(f"File size: {os.path.getsize(csv_path) / (1024*1024):.1f} MB")

# First, check the total number of rows
try:
    import openpyxl
    wb = openpyxl.load_workbook(csv_path, read_only=True)
    ws = wb.active
    total_rows = ws.max_row - 1  # Subtract header row
    print(f"Total rows in file: {total_rows:,}")
    wb.close()
except Exception as e:
    print(f"Warning: Could not determine file size: {e}")
    total_rows = None

# Read the Excel file efficiently
print("📥 Reading Excel file...")
try:
    # Excel files don't support chunksize, so read all at once with progress
    df = pd.read_excel(csv_path, engine='openpyxl')
    print(f"✅ Successfully loaded {len(df):,} rows with {len(df.columns)} columns")
    
except Exception as e:
    print(f"❌ Failed to read Excel file: {e}")
    print("Make sure the Excel file is not corrupted and not open in another application.")
    exit(1)

# ---------------------------
# 2. Combine row text for embedding
# ---------------------------
def create_combined_text(row):
    """Create combined text from row data with error handling for missing values."""
    try:
        return f"""
    Sourcerecord ID: {row.get('Sourcerecord ID', 'N/A')}
    Source Title: {row.get('Source Title', 'N/A')}
    ISSN: {row.get('ISSN', 'N/A')}
    EISSN: {row.get('EISSN', 'N/A')}
    Active or Inactive: {row.get('Active or Inactive', 'N/A')}
    Coverage: {row.get('Coverage', 'N/A')}
    Titles Discontinued by Scopus Due to Quality Issues: {row.get('Titles Discontinued by Scopus Due to Quality Issues', 'N/A')}
    Article Language in Source: {row.get('Article Language in Source (Three-Letter ISO Language Codes)', 'N/A')}
    Medline-sourced Title?: {row.get('Medline-sourced Title? (See additional details under separate tab.)', 'N/A')}
    Open Access Status: {row.get('Open Access Status', 'N/A')}
    Articles in Press Included?: {row.get('Articles in Press Included?', 'N/A')}
    Added to List Jul. 2025: {row.get('Added to List Jul. 2025', 'N/A')}
    Source Type: {row.get('Source Type', 'N/A')}
    Title History Indication: {row.get('Title History Indication', 'N/A')}
    Related Title 1: {row.get('Related Title 1', 'N/A')}
    Other Related Title 2: {row.get('Other Related Title 2', 'N/A')}
    Other Related Title 3: {row.get('Other Related Title 3', 'N/A')}
    Other Related Title 4: {row.get('Other Related Title 4', 'N/A')}
    Publisher: {row.get('Publisher', 'N/A')}
    Publisher Imprints Grouped to Main Publisher: {row.get('Publisher Imprints Grouped to Main Publisher', 'N/A')}
    All Science Journal Classification Codes (ASJC): {row.get('All Science Journal Classification Codes (ASJC)', 'N/A')}
        """.strip()
    except Exception as e:
        print(f"Warning: Error processing row: {e}")
        return f"Source Title: {row.get('Source Title', 'Unknown')}"

# Process texts with progress bar
print("🔤 Creating combined texts...")
texts = []
for idx, (_, row) in enumerate(tqdm(df.iterrows(), total=len(df), desc="Processing rows")):
    text = create_combined_text(row)
    texts.append(text)

print(f"✅ Created {len(texts):,} text entries for embedding")

# ---------------------------
# 3. Setup Hugging Face embeddings
# ---------------------------
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

print("🤖 Setting up embeddings model...")
try:
    # Try to load the model first, this will download if needed
    print(f"Loading model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    print("✅ Model loaded successfully!")
    
    # Now create the embeddings wrapper
    embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)
    print("✅ Embeddings initialized successfully!")
    
except Exception as e:
    print(f"❌ Error loading model: {e}")
    print("Trying to download the model...")
    
    try:
        # Force download
        from huggingface_hub import snapshot_download
        snapshot_download(repo_id=MODEL_NAME)
        
        # Try again
        model = SentenceTransformer(MODEL_NAME)
        embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)
        print("✅ Model downloaded and loaded successfully!")
        
    except Exception as e2:
        print(f"❌ Failed to download/load model: {e2}")
        print("Please check your internet connection and try again.")
        exit(1)

# ---------------------------
# 4. Create FAISS index
# ---------------------------
print("⚡ Creating FAISS index...")
print(f"Processing {len(texts):,} documents...")

try:
    # For very large datasets, process in batches
    if len(texts) > 5000:
        print("Large dataset detected, processing in batches...")
        batch_size = 1000
        vectorstore = None
        
        for i in tqdm(range(0, len(texts), batch_size), desc="Creating FAISS batches"):
            batch_texts = texts[i:i+batch_size]
            
            if vectorstore is None:
                # Create initial vectorstore
                vectorstore = FAISS.from_texts(batch_texts, embeddings)
            else:
                # Add to existing vectorstore
                batch_vectorstore = FAISS.from_texts(batch_texts, embeddings)
                vectorstore.merge_from(batch_vectorstore)
                
        print(f"✅ FAISS index created with {len(texts):,} documents")
    else:
        # For smaller datasets, process all at once
        vectorstore = FAISS.from_texts(texts, embeddings)
        print(f"✅ FAISS index created with {len(texts):,} documents")
    
    # Save the index
    print("💾 Saving FAISS index...")
    vectorstore.save_local("faiss_index")
    print("✅ FAISS index saved to 'faiss_index' directory")
    
    # Verify the index
    print(f"🔍 Index verification: {vectorstore.index.ntotal} vectors stored")
    
except Exception as e:
    print(f"❌ Error creating FAISS index: {e}")
    print("This might be due to insufficient memory or corrupted data.")
    exit(1)
