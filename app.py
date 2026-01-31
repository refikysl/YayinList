import streamlit as st
import db_manager
import apa_formatter
import bibtex_helper
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

# --- Pre-fill State Helper ---
def prefill_state(key, value):
    if value:
        st.session_state[key] = value

if page == "Veri Girişi (Hocalar/Asistanlar)":
    st.title("📚 Akademik Yayın Veri Girişi")
    
    # Show success message from previous run if exists
    if 'success_msg' in st.session_state:
        st.success(st.session_state.success_msg)
        del st.session_state.success_msg
    
    # Department Selection
    st.markdown("### 🏛️ Bölüm Seçimi")
    department = st.radio(
        "Bölümünüzü Seçiniz:",
        [
            "Siyaset Bilimi ve Kamu Yönetimi",
            "İktisat",
            "İşletme",
            "Maliye",
            "Ekonometri",
            "Uluslararası İlişkiler"
        ],
        horizontal=False
    )
    
    st.markdown("---")
    
    # --- Session State for Reset (must be before BibTeX) ---
    if 'reset_counter' not in st.session_state:
        st.session_state.reset_counter = 0
    rk = str(st.session_state.reset_counter)
    
    # New Publication Button
    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        if st.button("🆕 Yeni Yayın Ekle", type="secondary", use_container_width=True):
            # Increment reset counter to force widget recreation
            st.session_state.reset_counter += 1
            
            # Clear all form-related session state
            keys_to_delete = []
            for key in list(st.session_state.keys()):
                if any(x in key for x in ['input', 'surname_', 'name_', 'ed_surname_', 'ed_name_', 
                                          'last_bib_file', 'show_date_msg', 'success_msg']):
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                del st.session_state[key]
            
            # Reset counters
            st.session_state.num_authors = 1
            st.session_state.num_editors = 1
            
            st.rerun()
    
    with col_btn2:
        st.info("💡 Yeni bir yayın eklemek için butona basın. Tüm alanlar temizlenecektir.")
    
    st.markdown("---")
    
    # --- BibTeX Upload ---
    with st.expander("📂 BibTeX Dosyası ile Otomatik Doldur", expanded=False):
        uploaded_file = st.file_uploader("BibTeX (.bib) dosyanızı yükleyin", type=['bib'])
        
        if uploaded_file is None:
            # Reset state if file is removed so re-uploading same file works
            if 'last_bib_file' in st.session_state:
                del st.session_state.last_bib_file
        
        else:
             # Prevent infinite loop: Only process if it's a new file
             # We use file.file_id or name+size as signature
             file_signature = f"{uploaded_file.name}_{uploaded_file.size}"
             
             if 'last_bib_file' not in st.session_state or st.session_state.last_bib_file != file_signature:
                 # Read string
                 string_data = uploaded_file.getvalue().decode("utf-8")
                 parsed = bibtex_helper.parse_bibtex(string_data)
                 
                 if parsed:
                     st.session_state.last_bib_file = file_signature
                     
                     st.success("✅ BibTeX dosyası başarıyla okundu! Alanlar otomatik dolduruldu. Lütfen kontrol edip 'Yayını Kaydet' butonuna basın.")
                     
                     # 1. Type
                     if 'publication_type' in parsed:
                         types = ["Makale", "Kitap", "Kitap Bölümü", "Bildiri", "Proje"]
                         if parsed['publication_type'] in types:
                            st.session_state['pub_type_select'] = parsed['publication_type']
                     
                     # 2. Common - Use keys with rk suffix
                     prefill_state(f'title_input_{rk}', parsed.get('title'))
                     
                     if 'publication_date' in parsed:
                         st.session_state[f'pub_date_input_{rk}'] = parsed['publication_date']
                         # Flag to show user-friendly message
                         st.session_state['show_date_msg'] = True
                     
                     # 3. Authors
                     if 'authors' in parsed and parsed['authors']:
                         auths = parsed['authors']
                         st.session_state.num_authors = len(auths)
                         for idx, auth in enumerate(auths, 1):
                             prefill_state(f"surname_{idx}", auth.get('surname'))
                             prefill_state(f"name_{idx}", auth.get('name'))
                     
                     # 4. Editors
                     if 'editors' in parsed and parsed['editors']:
                         eds = parsed['editors']
                         st.session_state.num_editors = len(eds)
                         for idx, ed in enumerate(eds, 1):
                             prefill_state(f"ed_surname_{idx}", ed.get('surname'))
                             prefill_state(f"ed_name_{idx}", ed.get('name'))
                             
                     # 5. Specifics - Use keys with rk suffix
                     prefill_state(f'journal_name_input_{rk}', parsed.get('journal_name'))
                     prefill_state(f'volume_input_{rk}', parsed.get('volume'))
                     prefill_state(f'issue_input_{rk}', parsed.get('issue'))
                     prefill_state(f'pages_input_{rk}', parsed.get('pages'))
                     prefill_state(f'publisher_input_{rk}', parsed.get('publisher'))
                     prefill_state(f'location_input_{rk}', parsed.get('location'))
                     prefill_state(f'book_title_input_{rk}', parsed.get('book_title'))
                     
                     # Trigger Rerun to reflect changes
                     st.rerun()
    
                 else:
                     st.warning("Dosya ayrıştırılamadı veya boş.")


    
    pub_type = st.selectbox(
        "Yayın Türü Seçiniz", 
        ["Makale", "Kitap", "Kitap Bölümü", "Bildiri", "Proje"],
        key='pub_type_select'
    )
    
    st.markdown("---")

    # --- Authors Section ---
    st.subheader("Yazarlar")
    
    authors_data = []
    # Loop over authors
    for i in range(1, st.session_state.num_authors + 1):
        col_auth1, col_auth2 = st.columns(2)
        with col_auth1:
            surname = st.text_input(f"{i}. Yazar Soyadı", key=f"surname_{i}")
        with col_auth2:
            name = st.text_input(f"{i}. Yazar Adı", key=f"name_{i}")
        
        if surname and name:
            authors_data.append({'surname': surname, 'name': name})
            
    # Controls for Authors
    c_btn1, c_btn2, c_spacer = st.columns([1, 1, 5])
    if c_btn1.button("➕ Yazar Ekle", key="add_auth_btn"):
        if st.session_state.num_authors < 5:
            st.session_state.num_authors += 1
            st.rerun()
            
    if st.session_state.num_authors > 1:
        if c_btn2.button("➖ Çıkar", key="del_auth_btn"):
             st.session_state.num_authors -= 1
             st.rerun()

    st.markdown("---")
    
    # --- Common Fields ---
    col1, col2 = st.columns(2)
    with col1:
        # Handling date logic
        # Fix Streamlit Warning by ensuring 'value' matches session_state if present
        default_date = st.session_state.get('pub_date_input', date.today())
        
        publication_date = st.date_input("Yayın Tarihi (Gün/Ay/Yıl)", value=default_date, key=f'pub_date_input_{rk}')
        
        # Show custom warning if triggered by BibTeX
        if st.session_state.get('show_date_msg'):
            st.info("Biptex kaydında yayının tarih bilgisi yalnızca yıl olarak yer aldığından o yılın 1 Ocak tarihi olarak belirlenmiştir. Yukarıda ilgili alandan tarih bilgisini gün ve ayı içerecek şekilde değiştirebilirsiniz")
            # Clear it so it doesn't stick? Or keep it? Keeping it is safer until saved.
        title = st.text_input("Başlık (Makale/Kitap/Bölüm/Proje Adı)", key=f'title_input_{rk}')
    
    # --- Dynamic Fields ---
    data = {}
    missing_fields = []
    editors_data = [] 
    
    with col2:
        if pub_type == "Makale":
            journal_name = st.text_input("Dergi Adı", key=f'journal_name_input_{rk}')
            volume = st.text_input("Cilt (Volume)", key=f'volume_input_{rk}')
            issue = st.text_input("Sayı (Issue)", key=f'issue_input_{rk}')
            pages = st.text_input("Sayfa Aralığı", key=f'pages_input_{rk}')
            
            if not journal_name: missing_fields.append("Dergi Adı")
            data.update({'journal_name': journal_name, 'volume': volume, 'issue': issue, 'pages': pages})
            
        elif pub_type == "Kitap":
            # Note: Using distinct keys if fields mean same thing (e.g. publisher) across types 
            # might conflict if we switch types and persistent key holds value?
            # Streamlit keys map to widgets. If widget disappears (hidden by if), state is normally cleared unless configured?
            # Actually st clears state of disappearing widgets.
            # So safe to re-use generic naming like 'publisher_input' IF it's semantically same. 
            # BUT if we load a Book Bibtex, then switch to Article, publisher_input might vanish? 
            # Yes. That is fine.
            
            publisher = st.text_input("Yayınevi", key=f'publisher_input_{rk}')
            location = st.text_input("Basım Yeri (Şehir)", key=f'location_input_{rk}')
            
            if not publisher: missing_fields.append("Yayınevi")
            if not location: missing_fields.append("Basım Yeri")
            data.update({'publisher': publisher, 'location': location})
            
        elif pub_type == "Kitap Bölümü":
            book_title = st.text_input("Kitap Adı", key=f'book_title_input_{rk}')
            publisher = st.text_input("Yayınevi", key=f'publisher_input_{rk}')
            location = st.text_input("Basım Yeri", key=f'location_input_{rk}')
            pages = st.text_input("Bölüm Sayfa Aralık", key=f'pages_input_{rk}')
            
            st.markdown("---")
            st.markdown("**Editörler**")
            
            # Editors Loop
            for j in range(1, st.session_state.num_editors + 1):
                ce1, ce2 = st.columns(2)
                with ce1:
                    e_surname = st.text_input(f"{j}. Editör Soyadı", key=f"ed_surname_{j}")
                with ce2:
                    e_name = st.text_input(f"{j}. Editör Adı", key=f"ed_name_{j}")
                
                if e_surname and e_name:
                    editors_data.append({'surname': e_surname, 'name': e_name})
            
            ce_btn1, ce_btn2, ce_spacer = st.columns([1, 1, 5])
            if ce_btn1.button("➕ Editör Ekle", key="add_ed_btn"):
                if st.session_state.num_editors < 5:
                    st.session_state.num_editors += 1
                    st.rerun()
            
            if st.session_state.num_editors > 1:
                if ce_btn2.button("➖ Çıkar", key="del_ed_btn"):
                    st.session_state.num_editors -= 1
                    st.rerun()
            
            if not book_title: missing_fields.append("Kitap Adı")
            if not publisher: missing_fields.append("Yayınevi")
            
            data.update({
                'book_title': book_title, 
                'publisher': publisher, 
                'location': location, 
                'pages': pages,
                'editors': editors_data 
            })
            
        elif pub_type == "Bildiri":
            conf_name = st.text_input("Konferans/Sempozyum Adı", key=f'book_title_input_{rk}') # Reusing book_title logic for conf name
            location = st.text_input("Konferans Yeri", key=f'location_input_{rk}')
            publisher = st.text_input("Organizasyon/Yayınlayan", key=f'publisher_input_{rk}')
            
            if not conf_name: missing_fields.append("Konferans Adı")
            data.update({'book_title': conf_name, 'location': location, 'publisher': publisher})
            
        elif pub_type == "Proje":
            funding_agency = st.text_input("Destekleyen Kurum (Örn: TÜBİTAK)", key=f'funding_agency_input_{rk}')
            project_status = st.text_input("Proje No / Görev", key=f'project_status_input_{rk}')
            if not funding_agency: missing_fields.append("Destekleyen Kurum")
            data.update({'funding_agency': funding_agency, 'project_status': project_status})

    st.markdown("---")
    
    # Show success message here too (closer to save button)
    if 'success_msg' in st.session_state:
        st.success(st.session_state.success_msg)
    
    submitted = st.button("💾 Yayını Kaydet", type="primary")
    
    if submitted:
        if not authors_data:
            st.error("En az 1 yazar girmelisiniz.")
        elif pub_type == "Kitap Bölümü" and not editors_data:
             st.error("En az 1 editör girmelisiniz.")
        elif not title:
            st.error("Başlık girmelisiniz.")
        elif missing_fields:
            st.error(f"Eksik alanlar: {', '.join(missing_fields)}")
        else:
            full_data = {
                'department': department,
                'publication_type': pub_type,
                'authors': authors_data,
                'publication_date': publication_date.strftime("%Y-%m-%d"),
                'title': title,
                **data
            }
            
            success = db_manager.add_publication(full_data)
            
            if success:
                # Immediate feedback with toast notification
                st.toast("✅ Yayın başarıyla kaydedildi!", icon="✅")
                
                # Store detailed success message for next run
                apa_citation = apa_formatter.format_apa_6(full_data)
                st.session_state.success_msg = f"**{pub_type} başarıyla veritabanına kaydedildi!**\n\n**APA Formatı:** {apa_citation}"
                
                # Don't auto-clear form - let user decide with "New Publication" button
                # Just show success message
                st.success(st.session_state.success_msg)
                st.info("💡 Yeni bir yayın eklemek için yukarıdaki '🆕 Yeni Yayın Ekle' butonuna basın.")

elif page == "Raporlama (Admin)":
    st.title("📊 Yönetici Rapor Ekranı")
    
    if 'admin_unlocked' not in st.session_state:
        st.session_state.admin_unlocked = False
        
    if not st.session_state.admin_unlocked:
        password = st.text_input("Yönetici Şifresi", type="password")
        if st.button("Giriş Yap"):
            if password == "1379":
                st.session_state.admin_unlocked = True
                st.rerun()
            else:
                st.error("Hatalı Şifre!")
    else:
        if st.button("Çıkış Yap"):
            st.session_state.admin_unlocked = False
            st.rerun()
            
        st.markdown("---")
        st.markdown("### Rapor Filtreleme")
        
        # Department Selection
        st.markdown("#### 🏛️ Bölüm Seçimi")
        selected_department = st.selectbox(
            "Bölüm Seçiniz:",
            [
                "Tümü",
                "Siyaset Bilimi ve Kamu Yönetimi",
                "İktisat",
                "İşletme",
                "Maliye",
                "Ekonometri",
                "Uluslararası İlişkiler"
            ]
        )
        
        st.markdown("---")
        
        # Report Type Selection
        report_type = st.selectbox(
            "Raporlama Türü",
            ["Tüm Yayınlar", "Yayın Türü Bazında", "Kişi Bazında"]
        )
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Başlangıç Tarihi", value=date(2025, 1, 1))
        with col2:
            end_date = st.date_input("Bitiş Tarihi", value=date(2026, 1, 1))
        
        # Additional filters based on report type
        selected_pub_type = None
        selected_person = None
        
        if report_type == "Yayın Türü Bazında":
            selected_pub_type = st.selectbox(
                "Yayın Türü Seçiniz",
                ["Makale", "Kitap", "Kitap Bölümü", "Bildiri", "Proje"]
            )
        elif report_type == "Kişi Bazında":
            st.info("Kişi adını tam olarak yazınız (Örn: Yılmaz)")
            selected_person = st.text_input("Yazar Soyadı")
            
        if st.button("Raporu Getir"):
            s_date_str = start_date.strftime("%Y-%m-%d")
            e_date_str = end_date.strftime("%Y-%m-%d")
            
            with st.spinner("Google Sheets'ten veriler çekiliyor..."):
                publications = db_manager.get_publications(s_date_str, e_date_str)
            
            if not publications:
                st.warning("Bu tarih aralığında yayın bulunamadı.")
            else:
                # Apply department filter first
                if selected_department != "Tümü":
                    publications = [p for p in publications if p.get('department') == selected_department]
                
                if not publications:
                    st.warning(f"{selected_department} bölümünde bu tarih aralığında yayın bulunamadı.")
                else:
                    # Apply additional filters
                    filtered_pubs = publications
                    
                    if report_type == "Yayın Türü Bazında" and selected_pub_type:
                        filtered_pubs = [p for p in publications if p.get('publication_type') == selected_pub_type]
                        
                    elif report_type == "Kişi Bazında" and selected_person:
                        # Filter by author surname
                        person_pubs = []
                        for p in publications:
                            authors = p.get('authors', [])
                            if isinstance(authors, list):
                                for auth in authors:
                                    if isinstance(auth, dict):
                                        surname = auth.get('surname', '').strip().lower()
                                        if selected_person.strip().lower() in surname:
                                            person_pubs.append(p)
                                            break
                        filtered_pubs = person_pubs
                    
                    if not filtered_pubs:
                        st.warning("Seçilen kriterlere uygun yayın bulunamadı.")
                    else:
                        # Group by publication type if "Tüm Yayınlar"
                        if report_type == "Tüm Yayınlar":
                            st.subheader(f"Bulunan Yayınlar ({len(filtered_pubs)})")
                            
                            # Group by type
                            grouped = {}
                            for pub in filtered_pubs:
                                ptype = pub.get('publication_type', 'Diğer')
                                if ptype not in grouped:
                                    grouped[ptype] = []
                                grouped[ptype].append(pub)
                            
                            report_text = ""
                            for ptype in ["Makale", "Kitap", "Kitap Bölümü", "Bildiri", "Proje", "Diğer"]:
                                if ptype in grouped:
                                    st.markdown(f"#### {ptype} ({len(grouped[ptype])})")
                                    report_text += f"\n### {ptype}\n\n"
                                    
                                    for idx, pub in enumerate(grouped[ptype], 1):
                                        citation = apa_formatter.format_apa_6(pub)
                                        st.markdown(f"**{idx}.** {citation}")
                                        
                                        plain = citation.replace("*", "")
                                        report_text += f"{idx}. {plain}\n\n"
                        
                        else:
                            # Simple list for filtered reports
                            if report_type == "Yayın Türü Bazında":
                                st.subheader(f"{selected_pub_type} - {len(filtered_pubs)} Yayın")
                            elif report_type == "Kişi Bazında":
                                st.subheader(f"{selected_person} - {len(filtered_pubs)} Yayın")
                            
                            report_text = ""
                            for idx, pub in enumerate(filtered_pubs, 1):
                                citation = apa_formatter.format_apa_6(pub)
                                ptype = pub.get('publication_type', 'Makale')
                                
                                st.markdown(f"**{idx}. [{ptype}]** {citation}")
                                
                                plain = citation.replace("*", "")
                                report_text += f"[{ptype}] {plain}\n\n"
                        
                        st.markdown("---")
                        st.subheader("Dışa Aktarma")
                        st.text_area("Metin", value=report_text, height=300)


