import pickle
import os
from sklearn.metrics.pairwise import cosine_similarity

class ScopusSearchEngine:
    """A simple search engine for Scopus journal data."""
    
    def __init__(self, index_file='scopus_search_index.pkl'):
        """Initialize the search engine with the saved index."""
        if not os.path.exists(index_file):
            raise FileNotFoundError(f"Index file '{index_file}' not found. Please run Step2_full_dataset.py first.")
        
        print(f"📚 Loading Scopus search index from {index_file}...")
        with open(index_file, 'rb') as f:
            self.index_data = pickle.load(f)
        
        self.tfidf_matrix = self.index_data['tfidf_matrix']
        self.vectorizer = self.index_data['vectorizer']
        self.texts = self.index_data['texts']
        self.metadatas = self.index_data['metadatas']
        
        info = self.index_data['dataset_info']
        print(f"✅ Index loaded successfully!")
        print(f"   - {info['total_documents']:,} journals")
        print(f"   - {info['total_features']:,} search features")
        print()
    
    def search(self, query, top_k=10, min_score=0.1):
        """
        Search for journals matching the query or ISSN.
        
        Args:
            query (str): Search query or ISSN number
            top_k (int): Maximum number of results to return
            min_score (float): Minimum similarity score (0-1)
        
        Returns:
            list: List of search results with scores and metadata
        """
        try:
            # Check if query looks like an ISSN (format: XXXX-XXXX or XXXXXXXX)
            issn_pattern = query.replace('-', '').replace(' ', '')
            is_issn_search = (len(issn_pattern) == 8 and issn_pattern.isdigit()) or ('-' in query and len(query.replace('-', '')) == 8)
            
            if is_issn_search:
                # Direct ISSN search
                results = []
                for idx, metadata in enumerate(self.metadatas):
                    issn_match = (
                        issn_pattern in metadata['issn'].replace('-', '') or
                        issn_pattern in metadata['eissn'].replace('-', '') or
                        query in metadata['issn'] or
                        query in metadata['eissn']
                    )
                    
                    if issn_match:
                        results.append({
                            'score': 1.0,  # Perfect match for ISSN
                            'rank': len(results) + 1,
                            'title': metadata['source_title'],
                            'publisher': metadata['publisher'],
                            'type': metadata['source_type'],
                            'issn': metadata['issn'],
                            'eissn': metadata['eissn'],
                            'open_access': metadata['open_access'],
                            'active_status': metadata['active_status'],
                            'coverage': metadata['coverage'],
                            'language': metadata['language'],
                            'sourcerecord_id': metadata['sourcerecord_id'],
                            'full_text': self.texts[idx]
                        })
                        
                        if len(results) >= top_k:
                            break
                
                return results
            
            else:
                # Regular text search
                query_vec = self.vectorizer.transform([query])
                scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
                top_indices = scores.argsort()[-top_k:][::-1]
                
                results = []
                for idx in top_indices:
                    if scores[idx] >= min_score:
                        results.append({
                            'score': scores[idx],
                            'rank': len(results) + 1,
                            'title': self.metadatas[idx]['source_title'],
                            'publisher': self.metadatas[idx]['publisher'],
                            'type': self.metadatas[idx]['source_type'],
                            'issn': self.metadatas[idx]['issn'],
                            'eissn': self.metadatas[idx]['eissn'],
                            'open_access': self.metadatas[idx]['open_access'],
                            'active_status': self.metadatas[idx]['active_status'],
                            'coverage': self.metadatas[idx]['coverage'],
                            'language': self.metadatas[idx]['language'],
                            'sourcerecord_id': self.metadatas[idx]['sourcerecord_id'],
                            'full_text': self.texts[idx]
                        })
                
                return results
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    
    def print_results(self, results, show_details=False):
        """Print search results in a formatted way."""
        if not results:
            print("No results found.")
            return
        
        print(f"Found {len(results)} results:")
        print("=" * 60)
        
        for result in results:
            print(f"{result['rank']}. {result['title']}")
            print(f"   Publisher: {result['publisher']}")
            print(f"   Type: {result['type']}")
            print(f"   Similarity Score: {result['score']:.4f}")
            
            if show_details:
                if result['issn']:
                    print(f"   ISSN: {result['issn']}")
                if result['eissn']:
                    print(f"   eISSN: {result['eissn']}")
                if result['open_access']:
                    print(f"   Open Access: {result['open_access']}")
                if result['subject_areas']:
                    print(f"   Subject Areas: {result['subject_areas']}")
            
            print()
    
    def interactive_search(self):
        """Start an interactive search session."""
        print("🔍 Scopus Journal Search Interface")
        print("=" * 50)
        print("Enter your search queries. Type 'quit' to exit.")
        print("Commands:")
        print("  - Normal search: just type your query")
        print("  - Detailed results: add '--details' to your query")
        print("  - More results: add '--count N' to get N results")
        print()
        
        while True:
            try:
                user_input = input("Search> ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye! 👋")
                    break
                
                if not user_input:
                    continue
                
                # Parse options
                parts = user_input.split()
                show_details = '--details' in parts
                
                top_k = 10
                if '--count' in parts:
                    try:
                        count_idx = parts.index('--count')
                        if count_idx + 1 < len(parts):
                            top_k = int(parts[count_idx + 1])
                            parts = parts[:count_idx] + parts[count_idx + 2:]
                    except (ValueError, IndexError):
                        print("Invalid count format. Using default.")
                
                # Remove options from query
                query = ' '.join([p for p in parts if not p.startswith('--')])
                
                if not query:
                    print("Please enter a search query.")
                    continue
                
                print(f"\n🔍 Searching for: '{query}'")
                results = self.search(query, top_k=top_k)
                print()
                self.print_results(results, show_details=show_details)
                print()
                
            except KeyboardInterrupt:
                print("\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"Error: {e}")

def main():
    """Main function to run the search interface."""
    try:
        # Initialize search engine
        engine = ScopusSearchEngine()
        
        # Start interactive search
        engine.interactive_search()
        
    except FileNotFoundError as e:
        print(f"❌ {e}")
        print("\nTo create the search index, run:")
        print("python Step2_full_dataset.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
