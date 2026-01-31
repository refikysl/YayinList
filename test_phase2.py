import db_manager
import apa_formatter
import os

def test_phase2():
    print("Testing Phase 2 Logic (Authors & Dates)...")
    
    # Repro init to be sure
    if os.path.exists("publications.db"):
        os.remove("publications.db")
    db_manager.init_db()
    
    # 1. Author Logic Test
    # Case A: 1 Author
    data1 = {
        'publication_type': 'Makale',
        'authors': [{'surname': 'Yilmaz', 'name': 'Ahmet'}],
        'publication_date': '2024-05-15',
        'title': 'Paper One',
        'journal_name': 'J1', 'volume': '1', 'issue': '1', 'pages': '1-2'
    }
    
    # Case B: 3 Authors
    data2 = {
        'publication_type': 'Makale',
        'authors': [
            {'surname': 'Doe', 'name': 'John'},
            {'surname': 'Smith', 'name': 'Jane'},
            {'surname': 'Brown', 'name': 'Bob'}
        ],
        'publication_date': '2025-06-20',
        'title': 'Paper Two',
        'journal_name': 'J2', 'volume': '2', 'issue': '2', 'pages': '3-4'
    }
    
    db_manager.add_publication(data1)
    db_manager.add_publication(data2)
    print("Data added.")
    
    # 2. Date Filter Test
    # Search covering only 2025
    results_2025 = db_manager.get_publications('2025-01-01', '2025-12-31')
    assert len(results_2025) == 1
    assert results_2025[0]['title'] == 'Paper Two'
    print("Date Filtering: PASS")
    
    # 3. Formatting Test
    # Apa 1: Yilmaz, A.
    citation1 = apa_formatter.format_apa_6(data1)
    print(f"Cit1: {citation1}")
    assert "Yilmaz, A. (2024)." in citation1
    
    # Apa 2: Doe, J., Smith, J., & Brown, B.
    citation2 = apa_formatter.format_apa_6(data2)
    print(f"Cit2: {citation2}")
    expected_auth = "Doe, J., Smith, J., & Brown, B."
    assert expected_auth in citation2
    print("APA Author Formatting: PASS")

if __name__ == "__main__":
    test_phase2()
