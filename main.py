import streamlit as st
import base64
import os
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Paulo Moreira | Consultoria & Gestão", layout="centered")

def get_base64(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return ""

fundo_marmore = get_base64("Background.svg")

# --- CSS ORIGINAL (INTACTO) ---
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
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    box-shadow: inset 0 0 20px rgba(191, 165, 115, 0.08);
}}

.service-box {{
    background-color: white;
    padding: 18px;
    border-radius: 10px;
    border-bottom: 3px solid #bfa573;
    margin-bottom: 15px;
    min-height: 155px;
}}

.service-title {{ color: #1a1a1a; font-weight: 800; font-size: 15px; }}
.service-desc {{ color: #555; font-size: 12.5px; }}

.profile-frame {{
    width: 180px; height: 180px;
    border-radius: 50%; border: 4px solid #bfa573;
    overflow: hidden; margin: 0 auto 15px auto;
}}

.profile-frame img {{ width: 100%; height: 100%; object-fit: cover; }}

.cargo-text {{ font-weight: 700; letter-spacing: 2px; font-size: 13px; }}
.quote-style {{ font-style: italic; color: #bfa573; font-size: 15px; }}
.bio-text {{ font-size: 14px; color: #333; }}

.legal-footer-box {{
    font-size: 11px; text-align: center; padding: 25px;
    background: rgba(253, 250, 245, 0.99);
    border-radius: 10px;
    border: 1px dashed #bfa573;
}}
</style>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
SHEET_ID = "1PoK3Gj6mdLVkniIzDgFNhwmOGgpznRAIC0CGzweASag"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

df = pd.DataFrame()

try:
    df = pd.read_csv(URL)
    df = df.fillna("")
    df = df[df["Score_PM5D"] >= 3]
except:
    pass

def escolher_imagem(row):
    if row.get("Capa_Manual"):
        return row["Capa_Manual"]
    return "https://via.placeholder.com/400x300.png?text=PM+5D"

# --- LOGO ---
if os.path.exists("Paulo Moreira Consultoria & Gestão.png"):
    st.image("Paulo Moreira Consultoria & Gestão.png", use_container_width=True)

# --- BOTÕES ---
c1, c2, c3 = st.columns(3)
with c1: st.link_button("🎯 Avaliar Imóvel", "https://www.kwportugal.pt/pt/property-valuation")
with c2: st.link_button("🏦 Simular Crédito", "https://docs.google.com/forms/d/e/1FAIpQLSfiMOMKqZhnB14I5_DTrPLQrWYgiQdaw-O2HBfQBoLh4Qk5Ow/viewform")
with c3: st.link_button("📲 App Pessoal KW", "https://app.kw.com/KWNVLOD5AW4")

st.write("<br>", unsafe_allow_html=True)

# --- PERFIL ---
st.markdown('<div class="main-protection-card">', unsafe_allow_html=True)
col_l, col_r = st.columns([1, 1.8])

with col_l:
    if os.path.exists("paulo_moreira.png"):
        img_b64 = get_base64("paulo_moreira.png")
        st.markdown(f'<div class="profile-frame"><img src="data:image/png;base64,{img_b64}"></div>', unsafe_allow_html=True)

with col_r:
    st.markdown("""
    <div class="white-solid-box">
        <div class="cargo-text">Consultor Imobiliário</div>
        <h1>Paulo Moreira</h1>
        <div class="quote-style">"O sucesso de uma transação imobiliária depende de estratégia, não de sorte."</div>
        <div class="bio-text">Especialista em ativos residenciais e industriais.</div>
    </div>
    """, unsafe_allow_html=True)

    # --- PREVIEW DINÂMICA ---
    if not df.empty:
        row = df.sort_values(by="Score_PM5D", ascending=False).iloc[0]

        imagem = escolher_imagem(row)

        st.markdown(f"""
        <div class="preview-window">
            <img src="{imagem}" style="width:100%; border-radius:10px;">
            <br><b>{row['Tipo']} | {row['Localidade']}</b><br>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="preview-window">
            <b>Sem dados disponíveis</b>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("""
<div class="legal-footer-box">
Resumo Plural, Lda.
</div>
""", unsafe_allow_html=True)
