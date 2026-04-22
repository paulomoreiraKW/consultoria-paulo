import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import urllib.parse
import base64
import os

# --- CONFIGURAÇÃO DA PÁGINA (ORIGINAL) ---
st.set_page_config(page_title="Paulo Moreira | Consultoria & Gestão 5D", layout="centered")

# --- FUNÇÕES DE SUPORTE (SCANNER & IMAGEM) ---
def get_base64(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return ""

def get_kw_photo(url):
    try:
        if pd.isna(url) or url == "": return None
        response = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')
        img = soup.find('meta', property='og:image')
        return img['content'] if img else None
    except:
        return None

# --- CSS DE PRECISÃO FINAL (ADN PRESERVADO + AJUSTES 5D) ---
fundo_marmore = get_base64("Background.svg")
st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/svg+xml;base64,{fundo_marmore}");
        background-size: cover; background-attachment: fixed;
    }}
    .main-protection-card {{
        background-color: rgba(253, 250, 245, 0.99);
        padding: 25px 35px 10px 35px;
        border-radius: 15px; border-left: 8px solid #bfa573;
        box-shadow: 0 15px 35px rgba(0,0,0,0.15); margin-bottom: 10px; 
    }}
    .white-solid-box {{
        background-color: #ffffff; padding: 20px; border-radius: 10px;
        border-bottom: 3px solid #bfa573; margin-bottom: 15px;
    }}
    .service-box {{
        background-color: white; padding: 18px; border-radius: 10px;
        border-bottom: 3px solid #bfa573; margin-bottom: 15px; min-height: 155px;
    }}
    .profile-frame {{
        width: 180px; height: 180px; border-radius: 50%; border: 4px solid #bfa573;
        overflow: hidden; margin: 0 auto 15px auto; background: white;
    }}
    .profile-frame img {{ width: 100%; height: 100%; object-fit: cover; }}
    .badge-5d {{
        background: linear-gradient(135deg, #bfa573, #8a7345);
        color: white; padding: 4px 12px; border-radius: 5px; font-weight: bold; font-size: 12px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- CONTEÚDO: O JARDIM (ESTÁTICO) ---
if os.path.exists("Paulo Moreira Consultoria & Gestão.png"):
    st.image("Paulo Moreira Consultoria & Gestão.png", use_container_width=True)

c1, c2, c3 = st.columns(3)
with c1: st.link_button("🎯 Avaliar Imóvel", "https://www.kwportugal.pt/pt/property-valuation")
with c2: st.link_button("🏦 Simular Crédito", "https://docs.google.com/forms/d/e/1FAIpQLSfiMOMKqZhnB14I5_DTrPLQrWYgiQdaw-O2HBfQBoLh4Qk5Ow/viewform")
with c3: st.link_button("📲 App Pessoal KW", "https://app.kw.com/KWNVLOD5AW4")

st.write("<br>", unsafe_allow_html=True)

# --- BLOCO IDENTIDADE + JANELA DINÂMICA (SCANNER) ---
st.markdown('<div class="main-protection-card">', unsafe_allow_html=True)
col_l, col_r = st.columns([1, 1.8])

with col_l:
    if os.path.exists("paulo_moreira.png"):
        img_b64 = get_base64("paulo_moreira.png")
        st.markdown(f'<div class="profile-frame"><img src="data:image/png;base64,{img_b64}"></div>', unsafe_allow_html=True)
    st.link_button("📸 Instagram", "https://www.instagram.com/paulomgmoreira/")
    st.link_button("🔵 Facebook", "https://www.facebook.com/PMMConsultoriaEGestao/")

with col_r:
    st.markdown("""<div class="white-solid-box">
        <div style="color:#1a1a1a; font-weight:700; letter-spacing:2px; text-transform:uppercase; font-size:13px;">Consultor Imobiliário</div>
        <h1 style="color:#1a1a1a; font-size:32px; font-weight:300; margin:5px 0;">Paulo Moreira</h1>
        <div style="font-style:italic; color:#bfa573; font-size:15px; margin:10px 0; border-left:2px solid #bfa573; padding-left:10px;">"O sucesso de uma transação imobiliária depende de estratégia, não de sorte."</div>
        <div style="font-size:14px; color:#333;">Especialista em ativos residenciais e industriais. Através da <b>Metodologia 5D</b>, garanto um acompanhamento técnico de excelência.</div>
    </div>""", unsafe_allow_html=True)

    # --- INTEGRAÇÃO DA JANELA VIVA (O SCANNER) ---
    try:
        SHEET_URL = "https://docs.google.com/spreadsheets/d/1PoK3Gj6mdLVkniIzDgFNhwmOGgpznRAIC0CGzweASag/export?format=csv"
        df = pd.read_csv(SHEET_URL)
        df['Score_PM5D'] = pd.to_numeric(df['Score_PM5D'], errors='coerce').fillna(0)
        validos = df[df['Score_PM5D'] >= 3].copy()
        
        if not validos.empty:
            destaque = validos.iloc[0]
            img_destaque = destaque['Capa_Manual'] if pd.notna(destaque['Capa_Manual']) else get_kw_photo(destaque['Link_Fonte'])
            st.markdown(f"""
                <div style="border: 2px dashed #bfa573; background: white; padding: 15px; border-radius: 12px; text-align: center;">
                    <img src="{img_destaque if img_destaque else 'https://via.placeholder.com/400x250'}" style="width:100%; border-radius:8px; height:180px; object-fit:cover
