from flask import Flask, render_template, request, jsonify
import os
import json
import re
from search_scopus import ScopusSearchEngine

app = Flask(__name__)

def generate_journal_description(result):
    """Generate a 2-line NLP description for a journal based on its metadata."""
    try:
        title = result.get('title', 'Unknown Journal')
        publisher = result.get('publisher', 'Unknown Publisher')
        journal_type = result.get('type', 'Journal')
        open_access = result.get('open_access', '')
        coverage = result.get('coverage', '')
        active_status = result.get('active_status', '')
        
        # Extract coverage years if available
        coverage_years = ''
        if coverage and coverage != 'nan':
            # Extract years from coverage string
            years = re.findall(r'\d{4}', str(coverage))
            if years:
                if len(years) >= 2:
                    coverage_years = f"from {years[0]} to {years[-1]}"
                else:
                    coverage_years = f"since {years[0]}"
        
        # Generate first line
        if journal_type.lower() == 'journal':
            line1 = f"{title} is a scholarly journal published by {publisher}."
        else:
            line1 = f"{title} is a {journal_type.lower()} published by {publisher}."
        
        # Generate second line with additional info
        info_parts = []
        
        if active_status and active_status.lower() == 'active':
            info_parts.append("currently active")
        elif active_status and active_status.lower() == 'inactive':
            info_parts.append("no longer active")
            
        if coverage_years:
            info_parts.append(f"with coverage {coverage_years}")
            
        if open_access and open_access.lower() in ['full', 'hybrid']:
            access_type = "full open access" if open_access.lower() == 'full' else "hybrid open access"
            info_parts.append(f"offering {access_type}")
        
        if info_parts:
            line2 = f"This publication is {', '.join(info_parts)}."
        else:
            line2 = "This publication provides academic content in its field of study."
        
        return f"{line1} {line2}"
        
    except Exception as e:
        return f"This is {result.get('title', 'a journal')} published by {result.get('publisher', 'an academic publisher')}. It provides scholarly content for researchers and academics in its field."

# Initialize the search engine
print("🚀 Initializing Scopus Search Engine...")
try:
    search_engine = ScopusSearchEngine()
    print("✅ Search engine ready!")
except Exception as e:
    print(f"❌ Error initializing search engine: {e}")
    search_engine = None

@app.route('/')
def index():
    """Main page with search interface."""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    """Handle search requests via API with advanced filtering."""
    if not search_engine:
        return jsonify({
            'error': 'Search engine not available. Please ensure scopus_search_index.pkl exists.',
            'results': []
        }), 500
    
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        top_k = int(data.get('top_k', 20))
        min_score = float(data.get('min_score', 0.1))
        
        # Advanced filters
        filters = data.get('filters', {})
        publisher_filter = filters.get('publisher', '').strip().lower()
        type_filter = filters.get('type', '').strip()
        open_access_filter = filters.get('open_access', '').strip()
        subject_filter = filters.get('subject_areas', '').strip()
        language_filter = filters.get('language', '').strip()
        
        if not query:
            return jsonify({
                'error': 'Please enter a search query',
                'results': []
            }), 400
        
        # Perform search with higher top_k to allow for filtering
        search_limit = max(top_k * 3, 100) if any([publisher_filter, type_filter, open_access_filter, subject_filter, language_filter]) else top_k
        results = search_engine.search(query, top_k=search_limit, min_score=min_score)
        
        # Apply advanced filters
        filtered_results = []
        for result in results:
            # Publisher filter
            if publisher_filter and publisher_filter not in result['publisher'].lower():
                continue
                
            # Type filter
            if type_filter and type_filter != result['type']:
                continue
                
            # Open access filter
            if open_access_filter and open_access_filter not in result['open_access']:
                continue
                
            # Subject areas filter
            if subject_filter:
                subject_codes = [code.strip() for code in subject_filter.split(',')]
                result_subjects = result['subject_areas'].split(';') if result['subject_areas'] != 'nan' else []
                if not any(code in result_subjects for code in subject_codes):
                    continue
                    
            # Language filter
            if language_filter and language_filter != result['language']:
                continue
            
            filtered_results.append(result)
            
            # Stop when we have enough results
            if len(filtered_results) >= top_k:
                break
        
        # Format results for JSON response
        formatted_results = []
        for i, result in enumerate(filtered_results):
            formatted_result = {
                'rank': i + 1,
                'title': result['title'],
                'publisher': result['publisher'],
                'type': result['type'],
                'issn': result['issn'] if result['issn'] != 'nan' else '',
                'eissn': result['eissn'] if result['eissn'] != 'nan' else '',
                'open_access': result['open_access'] if result['open_access'] != 'nan' else '',
                'active_status': result.get('active_status', ''),
                'coverage': result['coverage'] if result['coverage'] != 'nan' else '',
                'language': result['language'] if result['language'] != 'nan' else '',
                'sourcerecord_id': result['sourcerecord_id'],
                'description': generate_journal_description(result)
            }
            formatted_results.append(formatted_result)
        
        return jsonify({
            'query': query,
            'filters_applied': filters,
            'total_results': len(formatted_results),
            'results': formatted_results
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Search error: {str(e)}',
            'results': []
        }), 500

@app.route('/stats')
def stats():
    """Get dataset statistics."""
    if not search_engine:
        return jsonify({'error': 'Search engine not available'}), 500
    
    try:
        info = search_engine.index_data['dataset_info']
        return jsonify({
            'total_journals': info['total_documents'],
            'total_features': info['total_features'],
            'source_file': info['source_file'],
            'index_size_mb': round(os.path.getsize('scopus_search_index.pkl') / (1024*1024), 1)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/suggestions')
def suggestions():
    """Get search suggestions."""
    return jsonify({
        'suggestions': [
            "computer science artificial intelligence",
            "medical health journal",
            "environmental science climate change",
            "physics quantum mechanics",
            "economics finance business",
            "biology molecular genetics",
            "chemistry organic synthesis",
            "engineering mechanical design",
            "psychology cognitive science",
            "mathematics statistical analysis",
            "neuroscience brain research",
            "materials science nanotechnology",
            "social sciences anthropology",
            "education learning teaching",
            "renewable energy sustainability"
        ]
    })

if __name__ == '__main__':
    print("\n🌐 Starting Scopus Search Web Interface...")
    print("📍 Open your browser and go to: http://localhost:5000")
    print("Press Ctrl+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
