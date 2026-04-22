import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import base64
import os

# --- 1. CONFIGURAÇÃO (ORIGINAL) ---
st.set_page_config(page_title="Paulo Moreira | Consultoria & Gestão", layout="centered")

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

# --- 2. CARREGAMENTO SILENCIOSO (LÓGICA 5D) ---
try:
    SHEET_ID = "1PoK3Gj6mdLVkniIzDgFNhwmOGgpznRAIC0CGzweASag"
    URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
    df = pd.read_csv(URL)
    df['Score_PM5D'] = pd.to_numeric(df['Score_PM5D'], errors='coerce').fillna(0)
    validos = df[df['Score_PM5D'] >= 3].copy()
except:
    validos = pd.DataFrame()

fundo_marmore = get_base64("Background.svg")

# --- 3. CSS (ADN PRESERVADO - LINHAS 1 A 100) ---
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
    .preview-window {{
        border: 2px dashed #bfa573; background-color: #ffffff;
        border-radius: 12px; text-align: center; color: #bfa573;
        min-height: 250px; display: flex; flex-direction: column; 
        align-items: center; justify-content: center; position: relative; overflow: hidden;
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
    .cargo-text {{ color: #1a1a1a !important; font-weight: 700 !important; letter-spacing: 2px; text-transform: uppercase; font-size: 13px; }}
    .quote-style {{ font-style: italic; color: #bfa573; font-size: 15px; margin: 10px 0; border-left: 2px solid #bfa573; padding-left: 10px; }}
    .bio-text {{ font-size: 14px; color: #333; line-height: 1.5; }}
    .legal-footer-box {{
        font-size: 11px; color: #444; text-align: center; padding: 25px;
        background: rgba(253, 250, 245, 0.99); border-radius: 10px;
        border: 1px dashed #bfa573; margin-top: 30px; line-height: 1.8;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. TOPO E BOTÕES ---
if os.path.exists("Paulo Moreira Consultoria & Gestão.png"):
    st.image("Paulo Moreira Consultoria & Gestão.png", use_container_width=True)

c1, c2, c3 = st.columns(3)
with c1: st.link_button("🎯 Avaliar Imóvel", "https://www.kwportugal.pt/pt/property-valuation")
with c2: st.link_button("🏦 Simular Crédito", "https://docs.google.com/forms/d/e/1FAIpQLSfiMOMKqZhnB14I5_DTrPLQrWYgiQdaw-O2HBfQBoLh4Qk5Ow/viewform")
with c3: st.link_button("📲 App Pessoal KW", "https://app.kw.com/KWNVLOD5AW4")

st.write("<br>", unsafe_allow_html=True)

# --- 5. BLOCO IDENTIDADE + JANELA DINÂMICA ---
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
        <div class="cargo-text">Consultor Imobiliário</div>
        <h1 style="color:#1a1a1a; font-size:32px; font-weight:300; margin:5px 0;">Paulo Moreira</h1>
        <div class="quote-style">"O sucesso de uma transação imobiliária depende de estratégia, não de sorte."</div>
        <div class="bio-text">Especialista em ativos residenciais e industriais. Através da <b>Metodologia 5D</b>, garanto um acompanhamento técnico de excelência.</div>
    </div>""", unsafe_allow_html=True)

    # SUBSTUIÇÃO DA PREVIEW-WINDOW (SCANNER 5D)
    if not validos.empty:
        item = validos.iloc[0]
        foto = item['Capa_Manual'] if pd.notna(item['Capa_Manual']) else get_kw_photo(item['Link_Fonte'])
        st.markdown(f"""
            <div class="preview-window">
                <img src="{foto}" style="width:100%; height:100%; object-fit:cover; position:absolute; top:0; left:0;">
                <div style="position:relative; background:rgba(255,255,255,0.9); width:100%; margin-top:170px; padding:15px; border-top:2px solid #bfa573;">
                    <b style="color:#1a1a1a; font-size:14px;">{item['Localidade']} | ROI {item['ROI_Percent']}</b><br>
                    <span style="font-size:11px; color:#bfa573;">Destaque 5D Identificado</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="preview-window"><span>🖼️</span><br>Sincronizando Ativos 5D</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 6. SERVIÇOS E RODAPÉ (INTACTOS) ---
st.markdown('<div class="main-protection-card" style="border-left:none; border-top:6px solid #1a1a1a; padding-top:20px;">', unsafe_allow_html=True)
m1, m2 = st.columns(2)
with m1:
    st.markdown('<div class="service-box"><span style="font-weight:800;">📈 Estudo de Mercado</span><br><span style="font-size:12.5px; color:#555;">Análise profunda baseada em dados reais.</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="service-box"><span style="font-weight:800;">⚖️ Apoio Jurídico</span><br><span style="font-size:12.5px; color:#555;">Segurança total na documentação.</span></div>', unsafe_allow_html=True)
with m2:
    st.markdown('<div class="service-box"><span style="font-weight:800;">📣 Plano de Marketing</span><br><span style="font-size:12.5px; color:#555;">Exposição premium em mais de 100 portais.</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="service-box"><span style="font-weight:800;">🏦 Gestão de Crédito</span><br><span style="font-size:12.5px; color:#555;">Intermediação certificada.</span></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.write("<br>", unsafe_allow_html=True)
f1, f2, f3 = st.columns(3)
with f1: 
    if os.path.exists("P.M.M..png"): st.image("P.M.M..png", width=100)
with f2: 
    if os.path.exists("REAL ESTATE.svg"): st.image("REAL ESTATE.svg", width=110)
with f3: 
    if os.path.exists("area_feira.png"): st.image("area_feira.png", width=110)

st.markdown('<div class="legal-footer-box"><b>Resumo Plural, Lda.</b> - AMI 21331<br>Cada Market Center é de gestão independente</div>', unsafe_allow_html=True)
