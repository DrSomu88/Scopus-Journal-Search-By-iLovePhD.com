# step1_create_faiss_index.py

import pandas as pd
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
import os

# Load Excel and clean column names
df = pd.read_excel("ext_list_Jul_2025.xlsx")
df.columns = df.columns.str.strip()  # Remove any accidental spaces

# Optional: check column names
print(df.columns.tolist())

# Function to create combined searchable text
def create_combined_text(row):
    return f"""
    Sourcerecord ID: {row['Sourcerecord ID']}
    Source Title: {row['Source Title']}
    ISSN: {row['ISSN']}
    EISSN: {row['EISSN']}
    Active or Inactive: {row['Active or Inactive']}
    Coverage: {row['Coverage']}
    Titles Discontinued by Scopus Due to Quality Issues: {row['Titles Discontinued by Scopus Due to Quality Issues']}
    Article Language: {row['Article Language in Source (Three-Letter ISO Language Codes)']}
    Medline-sourced Title?: {row['Medline-sourced Title? (See additional details under separate tab.)']}
    Open Access Status: {row['Open Access Status']}
    Articles in Press Included?: {row['Articles in Press Included?']}
    Added to List Jul. 2025: {row['Added to List Jul. 2025']}
    Source Type: {row['Source Type']}
    Title History Indication: {row['Title History Indication']}
    Related Title 1: {row['Related Title 1']}
    Other Related Title 2: {row['Other Related Title 2']}
    Other Related Title 3: {row['Other Related Title 3']}
    Other Related Title 4: {row['Other Related Title 4']}
    Publisher: {row['Publisher']}
    Publisher Imprints Grouped to Main Publisher: {row['Publisher Imprints Grouped to Main Publisher']}
    All Science Journal Classification Codes (ASJC): {row['All Science Journal Classification Codes (ASJC)']}
    """

# Test with first row
print(create_combined_text(df.iloc[0]))

