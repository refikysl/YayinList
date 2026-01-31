import db_manager
import apa_formatter
import os

def test_backend():
    print("Testing Backend Logic...")
    
    # 1. Reset DB
    if os.path.exists("publications.db"):
        os.remove("publications.db")
    db_manager.init_db()
    print("DB Initialized.")
    
    # 2. Add Data
    data1 = {
        'author_name': 'Test, A.',
        'publication_year': 2024,
        'title': 'Test Title',
        'journal_name': 'Test Journal',
        'volume': '10',
        'issue': '1',
        'pages': '100-110'
    }
    db_manager.add_publication(data1)
    print("Data added.")
    
    # 3. Retrieve Data
    # Assuming today is included in the default query if we query broadly, 
    # but the function asks for specific dates.
    # Let's mock the today date or just query wide range.
    pubs = db_manager.get_publications('2020-01-01', '2030-01-01')
    
    assert len(pubs) == 1
    print(f"Data retrieved: {len(pubs)} record(s).")
    
    # 4. formatting
    citation = apa_formatter.format_apa_6(pubs[0])
    expected = "Test, A. (2024). Test Title. *Test Journal*, *10*(1), 100-110."
    print(f"Formatted: {citation}")
    assert citation == expected
    print("APA Formatting Verified.")
    
    print("ALL TESTS PASSED.")

if __name__ == "__main__":
    test_backend()
