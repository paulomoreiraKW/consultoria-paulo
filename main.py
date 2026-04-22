import streamlit as st
import base64
import os
import pandas as pd
import requests

# --- CONFIG ---
st.set_page_config(page_title="Paulo Moreira | Consultoria & Gestão", layout="centered")

# --- BASE64 ---
def get_base64(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return ""

fundo_marmore = get_base64("Background.svg")

# --- CSS (FIXED ESCAPE) ---
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
    box-shadow: inset 0 0 20px rgba(191,165,115,0.08);
}}
</style>
""", unsafe_allow_html=True)

# --- LOAD GOOGLE SHEET ---
SHEET_ID = "1PoK3Gj6mdLVkniIzDgFNhwmOGgpznRAIC0CGzweASag"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    df = pd.read_csv(CSV_URL)
    df = df.fillna("")
    df = df[df["Score_PM5D"] >= 3]
except:
    df = pd.DataFrame()

# --- HEADER ---
if os.path.exists("Paulo Moreira Consultoria & Gestão.png"):
    st.image("Paulo Moreira Consultoria & Gestão.png", use_container_width=True)

c1, c2, c3 = st.columns(3)
with c1: st.link_button("🎯 Avaliar Imóvel", "https://www.kwportugal.pt/pt/property-valuation")
with c2: st.link_button("🏦 Simular Crédito", "https://docs.google.com/forms/d/e/1FAIpQLSfiMOMKqZhnB14I5_DTrPLQrWYgiQdaw-O2HBfQBoLh4Qk5Ow/viewform")
with c3: st.link_button("📲 App Pessoal KW", "https://app.kw.com/KWNVLOD5AW4")

st.write("<br>", unsafe_allow_html=True)

# --- MAIN CARD ---
col_container = st.container()

with col_container:
    st.markdown('<div class="main-protection-card">', unsafe_allow_html=True)

    col_l, col_r = st.columns([1, 1.8])

    with col_l:
        if os.path.exists("paulo_moreira.png"):
            img_b64 = get_base64("paulo_moreira.png")
            st.markdown(f'<div class="profile-frame"><img src="data:image/png;base64,{img_b64}"></div>', unsafe_allow_html=True)

    with col_r:

        # 👇 AQUI ENTRA O CARROSSEL (sem alterar mais nada)
        if not df.empty:
            row = df.iloc[0]

            imagem = row.get("Capa_Manual", "") or "https://via.placeholder.com/400x300.png?text=PM+5D"

            try:
                roi = float(row.get("ROI_Percent", 0))
                destaque = f"ROI {roi*100:.1f}%" if roi > 0 else "Sob Análise"
            except:
                destaque = "Sob Análise"

            st.markdown(f"""
            <div class="preview-window">
                <img src="{imagem}" style="width:100%; border-radius:10px; margin-bottom:10px;">
                <b>{row.get('Tipo','')} | {row.get('Localidade','')}</b>
                <span>{destaque}</span>
            </div>
            """, unsafe_allow_html=True)

        else:
            st.markdown("""
            <div class="preview-window">
                <span style="font-size:40px;">🖼️</span>
                <b>Visualização Estratégica do Imóvel</b>
                <span style="font-size:11px;">Sem dados disponíveis</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

with col_l:
    if os.path.exists("paulo_moreira.png"):
        img_b64 = get_base64("paulo_moreira.png")
        st.markdown(f'<div class="profile-frame"><img src="data:image/png;base64,{img_b64}"></div>', unsafe_allow_html=True)

# --- CARROSSEL (FASE 1 + BASE FASE 2) ---
with col_r:

    if "idx" not in st.session_state:
        st.session_state.idx = 0

    if not df.empty:
        row = df.iloc[st.session_state.idx % len(df)]

        # prioridade imagem (FASE 2 preparada)
        imagem = row.get("Capa_Manual", "")
        if not imagem:
            imagem = "https://via.placeholder.com/400x300.png?text=PM+5D"

        # destaque inteligente
        try:
            roi = float(row.get("ROI_Percent", 0))
            if roi > 0.25:
                destaque = f"ROI {roi*100:.1f}%"
            else:
                destaque = "Sob Análise"
        except:
            destaque = "Sob Análise"

        st.markdown(f"""
        <div class="preview-window">
            <img src="{imagem}" style="width:100%; border-radius:10px; margin-bottom:10px;">
            <b>{row.get('Tipo','')} | {row.get('Localidade','')}</b>
            <span>{destaque}</span>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔄 Ver próximo ativo"):
            st.session_state.idx += 1
            st.rerun()

    else:
        st.markdown("""
        <div class="preview-window">
            <span style="font-size:40px;">🖼️</span>
            <b>Visualização Estratégica do Imóvel</b>
            <span style="font-size:11px;">A carregar dados...</span>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- MONTRA 5D ---
st.markdown("<br>", unsafe_allow_html=True)

for _, row in df.iterrows():

    img = row.get("Capa_Manual", "")
    if not img:
        img = "https://via.placeholder.com/400x300.png?text=PM+5D"

    st.markdown(f"""
    <div class="white-solid-box">
        <img src="{img}" style="width:100%; border-radius:8px;">
        <br><br>
        <b>{row.get('Localidade','')} | {row.get('Tipo','')}</b><br>
        ROI: <b>{row.get('ROI_Percent','')}</b>
    </div>
    """, unsafe_allow_html=True)
