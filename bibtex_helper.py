import bibtexparser
from bibtexparser.bparser import BibTexParser
import streamlit as st

def parse_bibtex(file_content):
    """
    Parses a BibTeX string and returns a dictionary of mapped fields 
    compatible with the application schema.
    Returns the first entry found in the file.
    """
    try:
        parser = BibTexParser()
        parser.ignore_nonstandard_types = False
        
        # Parse the string
        bib_database = bibtexparser.loads(file_content, parser=parser)
        
        if not bib_database.entries:
            return None
            
        # Take the first entry
        entry = bib_database.entries[0]
        
        # Mapping Result
        mapped = {}
        
        # --- Type Mapping ---
        bib_type = entry.get('ENTRYTYPE', '').lower()
        if bib_type == 'article':
            mapped['publication_type'] = 'Makale'
        elif bib_type == 'book':
            mapped['publication_type'] = 'Kitap'
        elif bib_type == 'inbook' or bib_type == 'incollection':
            mapped['publication_type'] = 'Kitap Bölümü'
        elif bib_type == 'inproceedings' or bib_type == 'conference':
            mapped['publication_type'] = 'Bildiri'
        # Default or others? Let user manually select if unknown, 
        # but we can try to guess or leave it to UI default.
        
        # --- Common Fields ---
        mapped['title'] = entry.get('title', '').replace('{', '').replace('}', '')
        
        # Date/Year
        # Bibtex usually has 'year'.
        year = entry.get('year', '')
        if year:
            # We need full date for the picker. Default to Jan 1 of that year.
            from datetime import date
            try:
                mapped['publication_date'] = date(int(year), 1, 1)
            except:
                pass
        
        # --- Author Parsing ---
        # Format: "Smith, John and Doe, Jane"
        if 'author' in entry:
            authors_list = []
            raw_authors = entry['author'].split(' and ')
            for raw in raw_authors:
                # Simple parsing: Split by comma if exists "Surname, Name"
                # Else "Name Surname" logic is harder, assume BibTeX standard "Surname, Name"
                parts = raw.split(',')
                if len(parts) >= 2:
                    surname = parts[0].strip()
                    name = parts[1].strip()
                else:
                    # Fallback "Name Surname" -> Last token is surname
                    tokens = raw.strip().split()
                    if len(tokens) > 1:
                        surname = tokens[-1]
                        name = " ".join(tokens[:-1])
                    else:
                        surname = raw.strip()
                        name = ""
                        
                authors_list.append({'surname': surname, 'name': name})
            
            mapped['authors'] = authors_list
            
        # --- Editors Parsing ---
        if 'editor' in entry:
            editors_list = []
            raw_editors = entry['editor'].split(' and ')
            for raw in raw_editors:
                parts = raw.split(',')
                if len(parts) >= 2:
                    surname = parts[0].strip()
                    name = parts[1].strip()
                else:
                    tokens = raw.strip().split()
                    if len(tokens) > 1:
                        surname = tokens[-1]
                        name = " ".join(tokens[:-1])
                    else:
                        surname = raw.strip()
                        name = ""
                editors_list.append({'surname': surname, 'name': name})
            
            mapped['editors'] = editors_list

        # --- Specific Fields ---
        # Makale
        mapped['journal_name'] = entry.get('journal', '')
        mapped['volume'] = entry.get('volume', '')
        mapped['issue'] = entry.get('number', '')
        mapped['pages'] = entry.get('pages', '')
        
        # Kitap / Kitap Bölümü
        mapped['publisher'] = entry.get('publisher', '')
        mapped['location'] = entry.get('address', '') # BibTeX uses 'address' for location
        mapped['book_title'] = entry.get('booktitle', '')
        
        # Bildiri
        # booktitle usually used for conference name
        if not mapped['book_title']:
            mapped['book_title'] = entry.get('series', '') # Fallback

        return mapped
        
    except Exception as e:
        print(f"BibTeX Error: {e}")
        return None
