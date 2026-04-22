import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import urllib.parse
import base64
import os

# [PBO-PM] - FUSÃO TOTAL: JARDIM + MOTOR 5D
st.set_page_config(page_title="Paulo Moreira | Consultoria & Gestão 5D", layout="centered")

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

fundo_marmore = get_base64("Background.svg")

# --- CSS DE PRECISÃO (FUNDIDO) ---
st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/svg+xml;base64,{fundo_marmore}");
        background-size: cover;
        background-attachment: fixed;
    }}
    .main-protection-card {{
        background-color: rgba(253, 250, 245, 0.99);
        padding: 25px 35px;
        border-radius: 15px;
        border-left: 8px solid #bfa573;
        box-shadow: 0 15px 35px rgba(0,0,0,0.15);
        margin-bottom: 15px;
    }}
    .white-solid-box {{
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border-bottom: 3px solid #bfa573;
        margin-bottom: 15px;
    }}
    .service-box {{
        background-color: white;
        padding: 18px;
        border-radius: 10px;
        border-bottom: 3px solid #bfa573;
        margin-bottom: 15px;
        min-height: 155px;
    }}
    .profile-frame {{
        width: 180px; height: 180px;
        border-radius: 50%; border: 4px solid #bfa573;
        overflow: hidden; margin: 0 auto 15px auto;
        background: white;
    }}
    .profile-frame img {{ width: 100%; height: 100%; object-fit: cover; }}
    .badge-5d {{
        background: linear-gradient(135deg, #bfa573, #8a7345);
        color: white;
        padding: 3px 10px;
        border-radius: 5px;
        font-size: 11px;
        font-weight: bold;
    }}
    .legal-footer-box {{
        font-size: 11px; color: #444; text-align: center; padding: 25px;
        background: rgba(253, 250, 245, 0.99); border-radius: 10px;
        border: 1px dashed #bfa573; margin-top: 30px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- CABEÇALHO ---
if os.path.exists("Paulo Moreira Consultoria & Gestão.png"):
    st.image("Paulo Moreira Consultoria & Gestão.png", use_container_width=True)

c1, c2, c3 = st.columns(3)
with c1: st.link_button("🎯 Avaliar Imóvel", "https://www.kwportugal.pt/pt/property-valuation")
with c2: st.link_button("🏦 Simular Crédito", "https://docs.google.com/forms/d/e/1FAIpQLSfiMOMKqZhnB14I5_DTrPLQrWYgiQdaw-O2HBfQBoLh4Qk5Ow/viewform")
with c3: st.link_button("📲 App Pessoal KW", "https://app.kw.com/KWNVLOD5AW4")

# --- BLOCO IDENTIDADE + JANELA DINÂMICA ---
st.markdown('<div class="main-protection-card">', unsafe_allow_html=True)
col_l, col_r = st.columns([1, 1.8])

with col_l:
    if os.path.exists("paulo_moreira.png"):
        img_b64 = get_base64("paulo_moreira.png")
        st.markdown(f'<div class="profile-frame"><img src="data:image/png;base64,{img_b64}"></div>', unsafe_allow_html=True)
    st.link_button("📸 Instagram", "https://www.instagram.com/paulomgmoreira/")
    st.link_button("🔵 Facebook", "https://www.facebook.com/PMMConsultoriaEGestao/")

with col_r:
    st.markdown(f"""<div class="white-solid-box">
        <div style="color:#1a1a1a; font-weight:700; letter-spacing:2px; text-transform:uppercase; font-size:13px;">Consultor Imobiliário</div>
        <h1 style="color:#1a1a1a; font-size:32px; font-weight:300; margin:5px 0;">Paulo Moreira</h1>
        <div style="font-style:italic; color:#bfa573; font-size:15px; margin:10px 0; border-left:2px solid #bfa573; padding-left:10px;">
            "O papel aceita tudo, mas o terreno não engana."
        </div>
    </div>""", unsafe_allow_html=True)

    # --- JANELA DE VISUALIZAÇÃO DINÂMICA ---
    try:
        SHEET_ID = "1PoK3Gj6mdLVkniIzDgFNhwmOGgpznRAIC0CGzweASag"
        URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
        df = pd.read_csv(URL)
        df['Score_PM5D'] = pd.to_numeric(df['Score_PM5D'], errors='coerce').fillna(0)
        df_validos = df[df['Score_PM5D'] >= 3].copy()

        if not df_validos.empty:
            destaque = df_validos.iloc[0] # Pega o melhor Score para a janela
            foto_janela = destaque.get('Capa_Manual') if pd.notna(destaque.get('Capa_Manual')) else get_kw_photo(destaque['Link_Fonte'])
            if not foto_janela: foto_janela = "https://via.placeholder.com/600x400"
            
            st.markdown(f"""
                <div style="border: 2px dashed #bfa573; background: white; padding: 10px; border-radius: 12px; text-align: center;">
                    <img src="{foto_janela}" style="width:100%; border-radius:8px; height:200px; object-fit:cover;">
                    <div style="margin-top:5px; font-size:12px; color:#bfa573; font-weight:bold;">
                        Destaque 5D: {destaque['Tipo']} em {destaque['Localidade']} | ROI: {destaque['ROI_Percent']}
                    </div>
                </div>
            """, unsafe_allow_html=True)
    except:
        st.markdown('<div style="height:250px;" class="preview-window">Sincronizando Ativos...</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- BLOCO DE SERVIÇOS ---
st.markdown('<div class="main-protection-card" style="border-left:none; border-top:6px solid #1a1a1a;">', unsafe_allow_html=True)
m1, m2 = st.columns(2)
with m1:
    st.markdown("""<div class="service-box">
        <span style="font-weight:800; font-size:15px;">📈 Estudo de Mercado</span><br>
        <span style="color:#555; font-size:12.5px;">Análise profunda baseada em dados reais e comparativos.</span>
    </div>""", unsafe_allow_html=True)
with m2:
    st.markdown("""<div class="service-box">
        <span style="font-weight:800; font-size:15px;">📣 Plano de Marketing</span><br>
        <span style="color:#555; font-size:12.5px;">Exposição premium em mais de 100 portais nacionais e internacionais.</span>
    </div>""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- LISTA DE IMÓVEIS (Abaixo dos Serviços) ---
if 'df_validos' in locals() and not df_validos.empty:
    st.markdown("<h3 style='text-align:center; color:#1a1a1a;'>🚀 Oportunidades Validadas PM5D</h3>", unsafe_allow_html=True)
    for _, row in df_validos.iterrows():
        with st.container():
            st.markdown('<div class="main-protection-card" style="background

except Exception as e:
    st.error("O motor de dados está a ser sincronizado. Por favor, atualize em 10 segundos.")

# --- RODAPÉ (AUTORIDADE) ---
st.markdown("<br><div style='text-align:center; color:#888; font-size:12px;'>Paulo Moreira | Consultoria & Investimento Imobiliário 5D<br>KW Area Feira</div>", unsafe_allow_html=True)
