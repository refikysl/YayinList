def format_apa_6(data):
    """
    Formats publication data into an APA 6.0 citation string.
    Supports: Makale, Kitap, Kitap Bölümü, Bildiri, Proje
    
    Data Structure Updates:
    - authors: List of dicts [{'name': '...', 'surname': '...'}]
    - editors: List of dicts [{'name': '...', 'surname': '...'}] OR string (fallback)
    - publication_date: 'YYYY-MM-DD'
    """
    
    pub_type = data.get('publication_type', 'Makale')
    
    # Helper to Ensure String
    def safe_str(val):
        if val is None: return ""
        return str(val).strip()

    # --- Author Formatting ---
    # Surname, A.
    authors = data.get('authors', [])
    author_str = ""
    
    formatted_authors = []
    if isinstance(authors, list):
        for auth in authors:
            surname = safe_str(auth.get('surname', ''))
            name = safe_str(auth.get('name', ''))
            if surname:
                # Initials logic: "Ali Veli" -> "A. V."
                initials = ""
                if name:
                    parts = name.split()
                    initials = " ".join([p[0] + "." for p in parts])
                
                full = f"{surname}, {initials}" if initials else surname
                formatted_authors.append(full)
            
    if not formatted_authors:
        author_str = "" 
    elif len(formatted_authors) == 1:
        author_str = formatted_authors[0]
    elif len(formatted_authors) == 2:
        author_str = f"{formatted_authors[0]} & {formatted_authors[1]}"
    else:
        # A, B, & C
        all_but_last = ", ".join(formatted_authors[:-1])
        author_str = f"{all_but_last}, & {formatted_authors[-1]}"
        
    if author_str and not author_str.endswith('.'):
        author_str += "."


    # --- Editor Formatting ---
    # In A. Editor (Ed.)
    # Editors typically formatted as "Initial. Surname" (Not Surname, Initial)
    editors_data = data.get('editors', [])
    editor_str = ""
    
    formatted_editors = []
    if isinstance(editors_data, list):
        for ed in editors_data:
            surname = safe_str(ed.get('surname', ''))
            name = safe_str(ed.get('name', ''))
            
            if surname:
                initials = ""
                if name:
                    parts = name.split()
                    initials = " ".join([p[0] + "." for p in parts])
                
                # Format: A. Surname
                full = f"{initials} {surname}" if initials else surname
                formatted_editors.append(full)
    elif isinstance(editors_data, str):
        # Fallback for old data or simple string
        if editors_data: 
            formatted_editors.append(editors_data)
            
    if not formatted_editors:
        editor_str = ""
    elif len(formatted_editors) == 1:
        editor_str = f"{formatted_editors[0]} (Ed.)"
    elif len(formatted_editors) == 2:
        editor_str = f"{formatted_editors[0]} & {formatted_editors[1]} (Eds.)"
    else:
        all_but_last = ", ".join(formatted_editors[:-1])
        editor_str = f"{all_but_last}, & {formatted_editors[-1]} (Eds.)"


    # --- Year Parsing ---
    pub_date = safe_str(data.get('publication_date', '')) 
    year = ""
    if pub_date and len(pub_date) >= 4:
        year = pub_date[:4]
    
    # Helper to Ensure Dot
    def ensure_dot(s):
        if s and not s.endswith(('.', '?', '!')):
            return s + "."
        return s

    title = safe_str(data.get('title', ''))
    
    # --- Format Selection ---
    
    if pub_type == 'Makale':
        journal = safe_str(data.get('journal_name', ''))
        volume = safe_str(data.get('volume', ''))
        issue = safe_str(data.get('issue', ''))
        pages = safe_str(data.get('pages', ''))
        
        parts = []
        if author_str: parts.append(author_str)
        if year: parts.append(f"({year}).")
        if title: parts.append(ensure_dot(title))
        
        container = ""
        if journal: container += f"*{journal}*"
        if volume: 
            if container: container += ", "
            container += f"*{volume}*"
        if issue: container += f"({issue})"
        if pages: 
            if container: container += ", "
            container += f"{pages}."
        elif container:
             container = ensure_dot(container)
             
        if container: parts.append(container)
        return " ".join(parts)

    elif pub_type == 'Kitap':
        publisher = safe_str(data.get('publisher', ''))
        location = safe_str(data.get('location', ''))
        
        parts = []
        if author_str: parts.append(author_str)
        if year: parts.append(f"({year}).")
        
        if title:
             styled_title = f"*{title}*"
             parts.append(ensure_dot(styled_title))
             
        source = ""
        if location: source += location
        if publisher:
            if source: source += ": "
            source += publisher
        if source: parts.append(ensure_dot(source))
        
        return " ".join(parts)

    elif pub_type == 'Kitap Bölümü':
        book_title = safe_str(data.get('book_title', ''))
        pages = safe_str(data.get('pages', ''))
        location = safe_str(data.get('location', ''))
        publisher = safe_str(data.get('publisher', ''))
        
        parts = []
        if author_str: parts.append(author_str)
        if year: parts.append(f"({year}).")
        if title: parts.append(ensure_dot(title))
        
        # Container with Editors
        # Format: In A. Editor (Ed.), *Book Title* (pp. xx-xx).
        container = "In "
        if editor_str: container += f"{editor_str}, "
        if book_title: container += f"*{book_title}*"
        if pages: container += f" (pp. {pages})"
        
        parts.append(ensure_dot(container))
        
        source = ""
        if location: source += location
        if publisher:
             if source: source += ": "
             source += publisher
        if source: parts.append(ensure_dot(source))
        
        return " ".join(parts)

    elif pub_type == 'Bildiri':
        conf_name = safe_str(data.get('book_title', ''))
        location = safe_str(data.get('location', ''))
        publisher = safe_str(data.get('publisher', ''))
        
        parts = []
        if author_str: parts.append(author_str)
        if year: parts.append(f"({year}).")
        if title: parts.append(ensure_dot(title))
        
        if conf_name: parts.append(f"In *{conf_name}*.")
        
        source = ""
        if location: source += location
        if publisher:
            if source: source += ": "
            source += publisher
        if source: parts.append(ensure_dot(source))
        
        return " ".join(parts)

    elif pub_type == 'Proje':
        agency = safe_str(data.get('funding_agency', ''))
        status = safe_str(data.get('project_status', ''))
        
        parts = []
        if author_str: parts.append(author_str)
        if year: parts.append(f"({year}).")
        if title: 
             styled_title = f"*{title}*"
             parts.append(ensure_dot(styled_title))
        
        meta = []
        if agency: meta.append(agency)
        if status: meta.append(status)
        
        meta_str = ", ".join(meta)
        if meta_str: parts.append(ensure_dot(meta_str))
        
        return " ".join(parts)

    return "Unknown Format"
