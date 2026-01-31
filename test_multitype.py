import db_manager
import apa_formatter
import os

def test_multitype():
    print("Testing Multi-Type Support...")
    
    # 1. Reset/Init DB (ensure migration runs without error)
    if os.path.exists("publications.db"):
        try:
            os.remove("publications.db")
        except:
            pass
    db_manager.init_db()
    print("DB Initialized.")
    
    # 2. Test Cases
    cases = [
        {
            'publication_type': 'Makale',
            'author_name': 'Author, A.', 'publication_year': 2024, 'title': 'Article Title',
            'journal_name': 'Journal X', 'volume': '10', 'issue': '2', 'pages': '10-20',
            'expected': "Author, A. (2024). Article Title. *Journal X*, *10*(2), 10-20."
        },
        {
            'publication_type': 'Kitap',
            'author_name': 'Book Author, B.', 'publication_year': 2023, 'title': 'My Book',
            'publisher': 'Pub Co', 'location': 'Rome',
            'expected': "Book Author, B. (2023). *My Book*. Rome: Pub Co."
        },
        {
            'publication_type': 'Kitap Bölümü',
            'author_name': 'Chapter, C.', 'publication_year': 2022, 'title': 'Chapter One',
            'editors': 'Ed. One', 'book_title': 'Big Book', 'pages': '50-60',
            'publisher': 'Pub Co', 'location': 'London',
            'expected': "Chapter, C. (2022). Chapter One. In Ed. One (Ed.), *Big Book* (pp. 50-60). London: Pub Co."
        },
        {
            'publication_type': 'Bildiri',
            'author_name': 'Conf, D.', 'publication_year': 2021, 'title': 'Conf Paper',
            'book_title': 'Conference 2021', # mapped from conf_name
            'publisher': 'Org', 'location': 'Paris',
            'expected': "Conf, D. (2021). Conf Paper. In *Conference 2021*. Paris: Org."
        },
        {
            'publication_type': 'Proje',
            'author_name': 'Proj, E.', 'publication_year': 2020, 'title': 'Project Alpha',
            'funding_agency': 'TUBITAK', 'project_status': '1001',
            'expected': "Proj, E. (2020). *Project Alpha*. TUBITAK, 1001."
        }
    ]
    
    for case in cases:
        # Add to DB
        db_manager.add_publication(case)
        
        # Test Format
        formatted = apa_formatter.format_apa_6(case)
        print(f"[{case['publication_type']}] {formatted}")
        
        if formatted == case['expected']:
            print(" -> PASS")
        else:
            print(f" -> FAIL\n    Expected: {case['expected']}\n    Got:      {formatted}")

    print("Multi-type tests completed.")

if __name__ == "__main__":
    test_multitype()
