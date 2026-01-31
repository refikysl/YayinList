import requests
import json
from datetime import datetime
import os
import streamlit as st

# API URL Management
def get_api_url():
    # 1. Secrets (Cloud)
    try:
        if "api_url" in st.secrets:
            return st.secrets["api_url"]
    except Exception:
        pass
    
    # 2. Local File
    if os.path.exists("api_url.txt"):
        with open("api_url.txt", "r") as f:
            return f.read().strip()
            
    return None

def init_db():
    pass

def add_publication(data):
    """
    Sends publication data to Google Sheet via Web API.
    """
    url = get_api_url()
    if not url:
        st.error("API Bağlantı hatası: 'api_url.txt' dosyası bulunamadı.")
        return False
        
    try:
        # Prepare data for API
        # DB expects 'authors_json' logic implicitly handled by Python dict -> JSON
        # But 'editors' is now a LIST of dicts, similar to authors.
        # Apps Script expects 'editors' column.
        # Ideally, we should serialize it to string if Apps Script expects string,
        # OR send it as object and let Apps Script stringify it?
        # Apps Script code: `JSON.stringify(data.authors) || "[]"`
        # Apps Script code for editors: `data.editors || ""` -> Just takes it.
        # If we send a List, it might show [object Object].
        # Let's manual serialize editors to be safe, like authors_json logic in DBManager history.
        # Actually, Apps Script doesn't auto-stringify 'editors'.
        # So we should stringify IT here if we want clean string in Sheet.
        
        # Clone data to avoid mutating original for display
        payload = data.copy()
        
        # Serialize editors if present and is list
        if 'editors' in payload and isinstance(payload['editors'], list):
            payload['editors'] = json.dumps(payload['editors'])
            
        # Serialize authors? Apps Script does: `JSON.stringify(data.authors)`
        # So we can send raw list for authors.
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("result") == "success":
                return True
            else:
                st.error(f"Kayıt Hatası: {result.get('error')}")
                return False
        else:
            st.error(f"Sunucu Hatası: {response.status_code}")
            return False
            
    except Exception as e:
        st.error(f"Bağlantı Hatası: {str(e)}")
        return False

def get_publications(start_date=None, end_date=None):
    """
    Fetches all publications from Web API.
    """
    url = get_api_url()
    if not url:
        return []
        
    try:
        response = requests.get(url)
        if response.status_code == 200:
            all_data = response.json()
            
            if isinstance(all_data, dict) and all_data.get("result") == "error":
                st.error(f"Veri Okuma Hatası: {all_data.get('error')}")
                return []
                
            if not isinstance(all_data, list):
                return []
            
            # Post-Process Data
            processed_data = []
            for item in all_data:
                # 'authors' is already parsed by Apps Script `doGet` into object/list
                
                # Parse 'editors' if it is a JSON string
                if 'editors' in item and isinstance(item['editors'], str):
                    if item['editors'].startswith('[') or item['editors'].startswith('{'):
                         try:
                             item['editors'] = json.loads(item['editors'])
                         except:
                             pass
                
                processed_data.append(item)
                
            # Filter by Date
            if start_date and end_date:
                filtered = []
                for item in processed_data:
                    p_date = item.get('publication_date', '')
                    if p_date >= start_date and p_date <= end_date:
                        filtered.append(item)
                return filtered
            
            return processed_data
            
        else:
            st.error(f"Sunucu Hatası: {response.status_code}")
            return []
            
    except Exception as e:
        st.error(f"Bağlantı Hatası: {str(e)}")
        return []
