import streamlit as st
import db_manager
import apa_formatter
from datetime import date
import os

# Page configuration
st.set_page_config(page_title="Akademik Yayın Yönetim Sistemi", page_icon="📚", layout="wide")

# Check connectivity
if not db_manager.get_api_url():
    st.warning("⚠️ Sistem henüz kurulmamış.")
    st.info("Lütfen kurulum kılavuzundaki adımları takip ederek aldığınız **Web App URL**'sini 'api_url.txt' dosyasına kaydedin.")
    
    url_input = st.text_input("Veya URL'yi buraya yapıştırıp Enter'a basın:", placeholder="https://script.google.com/macros/s/...")
    if url_input:
        with open("api_url.txt", "w") as f:
            f.write(url_input)
        st.success("URL kaydedildi! Sayfa yenileniyor...")
        st.rerun()
    st.stop()

# Initialize DB
db_manager.init_db()

# Sidebar
st.sidebar.title("Navigasyon")
page = st.sidebar.radio("Sayfa Seçiniz:", ["Veri Girişi (Hocalar/Asistanlar)", "Raporlama (Admin)"])

# --- Session State for Dynamic Rows ---
if 'num_authors' not in st.session_state:
    st.session_state.num_authors = 1
if 'num_editors' not in st.session_state:
    st.session_state.num_editors = 1

def add_author():
    if st.session_state.num_authors < 5:
        st.session_state.num_authors += 1

def remove_author():
    if st.session_state.num_authors > 1:
        st.session_state.num_authors -= 1
        
def add_editor():
    if st.session_state.num_editors < 5:
        st.session_state.num_editors += 1

def remove_editor():
    if st.session_state.num_editors > 1:
        st.session_state.num_editors -= 1

if page == "Veri Girişi (Hocalar/Asistanlar)":
    st.title("📚 Akademik Yayın Veri Girişi")
    
    pub_type = st.selectbox(
        "Yayın Türü Seçiniz", 
        ["Makale", "Kitap", "Kitap Bölümü", "Bildiri", "Proje"]
    )
    
    st.markdown("---")
    
    with st.form("entry_form"):
        # --- Authors Section (Dynamic) ---
        st.subheader("Yazarlar")
        
        authors_data = []
        for i in range(1, st.session_state.num_authors + 1):
            col_auth1, col_auth2 = st.columns(2)
            with col_auth1:
                surname = st.text_input(f"{i}. Yazar Soyadı", key=f"surname_{i}")
            with col_auth2:
                name = st.text_input(f"{i}. Yazar Adı", key=f"name_{i}")
            
            if surname and name:
                authors_data.append({'surname': surname, 'name': name})
        
        # Helper cols for buttons inside form? No, buttons inside form submit the form. 
        # Streamlit doesn't support dynamic add buttons easily INSIDE a form without rerun.
        # But st.form doesn't update on interactive elements unless submitted.
        # Solution: Move dynamic buttons OUTSIDE the form or use `st.form_submit_button` hack?
        # Better: Put the buttons OUTSIDE the form to adjust the count, then render form.
        pass # We will place buttons outside
        
        # --- Common Fields ---
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            publication_date = st.date_input("Yayın Tarihi (Gün/Ay/Yıl)", value=date.today())
            title = st.text_input("Başlık (Makale/Kitap/Bölüm/Proje Adı)")
        
        # --- Dynamic Fields ---
        data = {}
        missing_fields = []
        editors_data = [] # For book chapter
        
        with col2:
            if pub_type == "Makale":
                journal_name = st.text_input("Dergi Adı")
                volume = st.text_input("Cilt (Volume)")
                issue = st.text_input("Sayı (Issue)")
                pages = st.text_input("Sayfa Aralığı")
                
                if not journal_name: missing_fields.append("Dergi Adı")
                data.update({'journal_name': journal_name, 'volume': volume, 'issue': issue, 'pages': pages})
                
            elif pub_type == "Kitap":
                publisher = st.text_input("Yayınevi")
                location = st.text_input("Basım Yeri (Şehir)")
                
                if not publisher: missing_fields.append("Yayınevi")
                if not location: missing_fields.append("Basım Yeri")
                data.update({'publisher': publisher, 'location': location})
                
            elif pub_type == "Kitap Bölümü":
                book_title = st.text_input("Kitap Adı")
                
                # Dynamic Editors within Form? Re-rendering is tricky.
                # Let's render slots based on session state managed outside.
                st.markdown("**Editörler**")
                for j in range(1, st.session_state.num_editors + 1):
                    ce1, ce2 = st.columns(2)
                    with ce1:
                        e_surname = st.text_input(f"{j}. Editör Soyadı", key=f"ed_surname_{j}")
                    with ce2:
                        e_name = st.text_input(f"{j}. Editör Adı", key=f"ed_name_{j}")
                    
                    if e_surname and e_name:
                        editors_data.append({'surname': e_surname, 'name': e_name})

                publisher = st.text_input("Yayınevi")
                location = st.text_input("Basım Yeri")
                pages = st.text_input("Bölüm Sayfa Aralık")
                
                if not book_title: missing_fields.append("Kitap Adı")
                if not publisher: missing_fields.append("Yayınevi")
                
                data.update({
                    'book_title': book_title, 
                    'publisher': publisher, 
                    'location': location, 
                    'pages': pages,
                    'editors': editors_data # Pass list
                })
                
            elif pub_type == "Bildiri":
                conf_name = st.text_input("Konferans/Sempozyum Adı")
                location = st.text_input("Konferans Yeri")
                publisher = st.text_input("Organizasyon/Yayınlayan")
                
                if not conf_name: missing_fields.append("Konferans Adı")
                data.update({'book_title': conf_name, 'location': location, 'publisher': publisher})
                
            elif pub_type == "Proje":
                funding_agency = st.text_input("Destekleyen Kurum (Örn: TÜBİTAK)")
                project_status = st.text_input("Proje No / Görev")
                if not funding_agency: missing_fields.append("Destekleyen Kurum")
                data.update({'funding_agency': funding_agency, 'project_status': project_status})

        submitted = st.form_submit_button("Yayını Kaydet")
        
        if submitted:
            if not authors_data:
                st.error("En az 1 yazar girmelisiniz.")
            # Special check for Editors if Book Chapter
            elif pub_type == "Kitap Bölümü" and not editors_data:
                 st.error("En az 1 editör girmelisiniz.")
            elif not title:
                st.error("Başlık girmelisiniz.")
            elif missing_fields:
                st.error(f"Eksik alanlar: {', '.join(missing_fields)}")
            else:
                full_data = {
                    'publication_type': pub_type,
                    'authors': authors_data,
                    'publication_date': publication_date.strftime("%Y-%m-%d"),
                    'title': title,
                    **data
                }
                
                success = db_manager.add_publication(full_data)
                
                if success:
                    apa_citation = apa_formatter.format_apa_6(full_data)
                    st.success(f"{pub_type} başarıyla kaydedildi!")
                    st.info(f"**APA Önizleme:** {apa_citation}")

    # --- Control Buttons (Outside Form to trigger rerun) ---
    # We place them after the form visually or sidebar? 
    # Placed after form is okay but might be below submit button.
    # Better: Place them in columns ABOVE the form or stick them in sidebar?
    # User said "Yazar ekle diye bir buton olsun... Ardından".
    # Since form containers isolate state, we can't easily put buttons inside to add rows dynamically without logic.
    # We will put "Row Controls" just above the form or near sections.
    # However, st.form freezes the layout.
    # We can stick row controls in a expander or just above the relevant section using containers?
    # Streamlit layout: 
    # [ Title ]
    # [ Yazar Ekle ] [ Yazar Çıkar ] (Updates state, reruns)
    # [ Form ]
    #    [ Loop over session_state.num_authors ]
    
    # Let's adjust layout:
    # We need to rerun to show more rows.
    
    # We re-render the controls *before* the form so user can setup the form structure.
    # But for "Kitap Bölümü", we need controls for editors too.
    
    # Let's use columns for controls above the form.
    
    # Redoing layout structure slightly for better UX.
    
    # [End of file logic update in next step - I will rewrite app.py content]

st.warning("Lütfen düğmeleri yeni kurguya göre yukarı taşıyalım.")
