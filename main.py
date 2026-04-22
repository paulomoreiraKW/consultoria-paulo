import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import urllib.parse
import base64
import os

# [PBO-PM] - CONFIGURAÇÃO DE ELITE: PAULO MOREIRA 5D
st.set_page_config(page_title="Paulo Moreira | Investimento 5D", layout="wide")

# --- FUNÇÕES DE SUPORTE ---
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
        # Procura a primeira imagem de imóvel no padrão KW
        img = soup.find('meta', property='og:image')
        return img['content'] if img else None
    except:
        return None

# --- ESTILO LUXO (MÁRMORE + BRANCO 0.99) ---
fundo = get_base64("Background.svg")
st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/svg+xml;base64,{fundo}");
        background-size: cover;
        background-attachment: fixed;
    }}
    .main-card {{
        background-color: rgba(255, 255, 255, 0.99);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border-left: 5px solid #bfa573;
    }}
    .property-card {{
        background: white;
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #eee;
        transition: 0.3s;
    }}
    .property-card:hover {{ transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); }}
    .badge-5d {{
        background: linear-gradient(135deg, #bfa573, #8a7345);
        color: white;
        padding: 5px 15px;
        border-radius: 50px;
        font-weight: bold;
        font-size: 12px;
    }}
    .roi-highlight {{ color: #bfa573; font-size: 24px; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

# --- CABEÇALHO (O JARDIM) ---
col_logo, col_kw = st.columns([2, 1])
with col_logo:
    if os.path.exists("Paulo Moreira Consultoria & Gestão.png"):
        st.image("Paulo Moreira Consultoria & Gestão.png", width=400)
with col_kw:
    if os.path.exists("area_feira.png"):
        st.image("area_feira.png", width=180)

st.markdown("<br>", unsafe_allow_html=True)

# --- CARREGAMENTO DE DADOS (CASCATA INTELIGENTE) ---
SHEET_ID = "1PoK3Gj6mdLVkniIzDgFNhwmOGgpznRAIC0CGzweASag"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    df = pd.read_csv(URL)
    # Limpeza e Blindagem (Ignora erros de divisão e scores baixos)
    df['Score_PM5D'] = pd.to_numeric(df['Score_PM5D'], errors='coerce').fillna(0)
    df_validos = df[df['Score_PM5D'] >= 3].copy()
    
    # --- JANELA DINÂMICA (CARROSSEL) ---
    st.markdown("<h2 style='text-align:center; color:#333;'>💎 Oportunidades Seleccionadas 5D</h2>", unsafe_allow_html=True)
    
    with st.container():
        # Lógica de Carrossel Simplificada (Cards em Destaque)
        cols_destaque = st.columns(len(df_validos.head(3)))
        for idx, (_, row) in enumerate(df_validos.head(3).iterrows()):
            with cols_destaque[idx]:
                # Prioridade de Foto: P (Capa_Manual) > Scraping > Placeholder
                foto = row.get('Capa_Manual')
                if pd.isna(foto) or foto == "":
                    foto = get_kw_photo(row['Link_Fonte'])
                if not foto: foto = "https://via.placeholder.com/600x400?text=Paulo+Moreira+5D"
                
                st.markdown(f"""
                <div style="position:relative;">
                    <img src="{foto}" style="width:100%; border-radius:15px; height:250px; object-fit:cover;">
                    <div style="position:absolute; top:10px; right:10px;" class="badge-5d">SCORE {int(row['Score_PM5D'])}</div>
                </div>
                <p style="margin-top:10px; font-weight:bold; color:#bfa573;">{row['Tipo']} em {row['Localidade']}</p>
                """, unsafe_allow_html=True)

    # --- O INTERIOR (CARDS DETALHADOS) ---
    st.markdown("<hr style='border: 0.5px solid #eee;'>", unsafe_allow_html=True)
    
    for _, row in df_validos.iterrows():
        with st.container():
            st.markdown(f'<div class="main-card">', unsafe_allow_html=True)
            c1, c2 = st.columns([1, 2])
            
            with c1:
                foto_card = row.get('Capa_Manual')
                if pd.isna(foto_card) or foto_card == "":
                    foto_card = get_kw_photo(row['Link_Fonte'])
                st.image(foto_card if foto_card else "https://via.placeholder.com/400x300")
            
            with c2:
                st.markdown(f"### {row['Localidade']} | {row['Tipo']}")
                st.markdown(f"<span class='badge-5d'>VALIDAÇÃO TÉCNICA PM5D</span>", unsafe_allow_html=True)
                
                # Métricas em Grelha
                m1, m2, m3 = st.columns(3)
                m1.metric("Investimento Total", f"{row['Investimento_Total']}")
                m2.markdown(f"**ROI Flip**<br><span class='roi-highlight'>{row['ROI_Percent']}</span>", unsafe_allow_html=True)
                m3.metric("Yield Anual", f"{row['Yield_Euros_Ano']}")
                
                st.markdown(f"<p style='font-style:italic; color:#666; font-size:13px;'>\"O papel aceita tudo, mas o terreno não engana.\"</p>", unsafe_allow_html=True)
                
                # Conversão
                msg_wa = f"Olá Paulo, solicito o Deal Pack técnico para o imóvel {row['Referencia']} em {row['Localidade']}."
                wa_url = f"https://wa.me/351911995695?text={urllib.parse.quote(msg_wa)}"
                
                btn_c1, btn_c2 = st.columns(2)
                with btn_c1:
                    st.link_button("🌐 Ver no Portal", str(row['Link_Fonte']), use_container_width=True)
                with btn_c2:
                    st.link_button("📄 Pedir Deal Pack", wa_url, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error("O motor de dados está a ser sincronizado. Por favor, atualize em 10 segundos.")

# --- RODAPÉ (AUTORIDADE) ---
st.markdown("<br><div style='text-align:center; color:#888; font-size:12px;'>Paulo Moreira | Consultoria & Investimento Imobiliário 5D<br>KW Area Feira</div>", unsafe_allow_html=True)
