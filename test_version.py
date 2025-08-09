# Simplified test version - no external dependencies
import csv

# Create sample data
sample_data = [
    {
        'Title': 'Journal of Science',
        'Publisher': 'Science Publisher',
        'ISSN': '1234-5678',
        'Subject Area': 'Physics',
        'Open Access': 'Yes',
        'Website': 'https://example.com'
    },
    {
        'Title': 'Research Journal',
        'Publisher': 'Research Publisher',
        'ISSN': '8765-4321',
        'Subject Area': 'Chemistry',
        'Open Access': 'No',
        'Website': 'https://research.com'
    }
]

# Test the text creation function
def create_combined_text(row):
    return f"""
    Title: {row['Title']}
    Publisher: {row['Publisher']}
    ISSN: {row['ISSN']}
    Subject Area: {row['Subject Area']}
    Open Access: {row['Open Access']}
    Website: {row['Website']}
    """

# Test with sample data
for row in sample_data:
    print(create_combined_text(row))
    print("-" * 50)

print("Test completed successfully!")


