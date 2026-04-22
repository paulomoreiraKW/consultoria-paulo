import streamlit as st
import base64
import os
import pandas as pd
import time

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Paulo Moreira | Consultoria & Gestão", layout="centered")

def get_base64(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return ""

fundo_marmore = get_base64("Background.svg")

# --- CSS ORIGINAL (INALTERADO) ---
st.markdown(f"""
<style>
.stApp {{
    background-image: url("data:image/svg+xml;base64,{fundo_marmore}");
    background-size: cover;
    background-attachment: fixed;
}}

.main-protection-card {{
    background-color: rgba(253, 250, 245, 0.99);
    padding: 25px 35px 10px 35px;
    border-radius: 15px;
    border-left: 8px solid #bfa573;
    box-shadow: 0 15px 35px rgba(0,0,0,0.15);
    margin-bottom: 10px; 
}}

.white-solid-box {{
    background-color: #ffffff;
    padding: 20px;
    border-radius: 10px;
    border-bottom: 3px solid #bfa573;
    margin-bottom: 15px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.05);
}}

.preview-window {{
    border: 2px dashed #bfa573;
    background-color: #ffffff;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    color: #bfa573;
    font-weight: 600;
    min-height: 250px;
    display: flex; 
    flex-direction: column; 
    align-items: center; 
    justify-content: center;
    box-shadow: inset 0 0 20px rgba(191, 165, 115, 0.08);
}}
</style>
""", unsafe_allow_html=True)

# --- GOOGLE SHEET ---
SHEET_ID = "1PoK3Gj6mdLVkniIzDgFNhwmOGgpznRAIC0CGzweASag"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    df = pd.read_csv(URL)
    df = df.fillna("")
    df = df[pd.to_numeric(df["Score_PM5D"], errors="coerce").fillna(0) >= 3]
except:
    df = pd.DataFrame()

# --- STATE ---
if "idx" not in st.session_state:
    st.session_state.idx = 0

if "last_update" not in st.session_state:
    st.session_state.last_update = time.time()

# --- HEADER ---
if os.path.exists("Paulo Moreira Consultoria & Gestão.png"):
    st.image("Paulo Moreira Consultoria & Gestão.png", use_container_width=True)

c1, c2, c3 = st.columns(3)
with c1: st.link_button("🎯 Avaliar Imóvel", "https://www.kwportugal.pt/pt/property-valuation")
with c2: st.link_button("🏦 Simular Crédito", "https://docs.google.com/forms/d/e/1FAIpQLSfiMOMKqZhnB14I5_DTrPLQrWYgiQdaw-O2HBfQBoLh4Qk5Ow/viewform")
with c3: st.link_button("📲 App Pessoal KW", "https://app.kw.com/KWNVLOD5AW4")

st.write("<br>", unsafe_allow_html=True)

# --- BLOCO PRINCIPAL ---
st.markdown('<div class="main-protection-card">', unsafe_allow_html=True)
col_l, col_r = st.columns([1, 1.8])

with col_l:
    if os.path.exists("paulo_moreira.png"):
        img_b64 = get_base64("paulo_moreira.png")
        st.markdown(f'<div class="profile-frame"><img src="data:image/png;base64,{img_b64}"></div>', unsafe_allow_html=True)

# --- 🔥 CARROSSEL AUTOMÁTICO ---
with col_r:

    intervalo = 3

    if not df.empty:

        agora = time.time()

        if agora - st.session_state.last_update > intervalo:
            st.session_state.idx = (st.session_state.idx + 1) % len(df)
            st.session_state.last_update = agora
            st.rerun()

        row = df.iloc[st.session_state.idx]

        # imagem
        imagem = row.get("Capa_Manual", "")
        if not imagem or not str(imagem).startswith("http"):
            imagem = "https://via.placeholder.com/400x300.png?text=PM+5D"

        # destaque inteligente
        try:
            roi = float(str(row.get("ROI_Percent", 0)).replace("%","").replace(",","."))
        except:
            roi = 0

        try:
            yield_val = float(str(row.get("Yield_Euros_Ano", 0)).replace(",",""))
        except:
            yield_val = 0

        if roi > 20:
            destaque = f"ROI {roi:.1f}%"
        elif yield_val > 0:
            destaque = f"Yield {yield_val:,.0f}€"
        else:
            destaque = "Sob Análise"

        st.markdown(f"""
        <div class="preview-window">
            <img src="{imagem}" style="width:100%; border-radius:10px;">
            <br><b>{row.get('Tipo','')} | {row.get('Localidade','')}</b><br>
            <span style="color:#bfa573;">{destaque}</span>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class="preview-window">
            <span style="font-size:40px;">🖼️</span>
            <b style="font-size:18px;">Visualização Estratégica do Imóvel</b>
            <span style="font-size:11px; color:#999;">A carregar dados...</span>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
