import streamlit as st
import base64
import os
import pandas as pd
import time
import requests
from bs4 import BeautifulSoup
import urllib.parse

# --- CONFIGURAÇÃO BASE (INTACTA) ---
st.set_page_config(page_title="Paulo Moreira | Consultoria & Gestão", layout="centered")

def get_base64(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return ""

fundo_marmore = get_base64("Background.svg")

# --- CSS ORIGINAL (NÃO ALTERADO) ---
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
}}

</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES INTELIGENTES ---

# Scraping imagem KW
def extrair_imagem(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")

        img = soup.find("img")
        if img and img.get("src"):
            return img["src"]
    except:
        return None

    return None

# Escolha de imagem (prioridade)
def escolher_imagem(row):
    if row.get("Capa_Manual"):
        return row["Capa_Manual"]

    if row.get("Link_Fonte"):
        img = extrair_imagem(row["Link_Fonte"])
        if img:
            return img

    return "https://via.placeholder.com/400x300.png?text=PM+5D"

# Destaque inteligente
def highlight(row):
    if row["ROI_Percent"] > 0.25:
        return f"ROI {row['ROI_Percent']*100:.1f}%"
    elif row["Yield_Euros_Ano"] > 0:
        return f"Yield {row['Yield_Euros_Ano']:,.0f}€"
    return "Sob Análise"

# Telegram alerta
def enviar_telegram(msg):
    TOKEN = "COLOCA_AQUI"
    CHAT_ID = "COLOCA_AQUI"

    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

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

# --- HEADER ORIGINAL ---
if os.path.exists("Paulo Moreira Consultoria & Gestão.png"):
    st.image("Paulo Moreira Consultoria & Gestão.png", use_container_width=True)

c1, c2, c3 = st.columns(3)
with c1: st.link_button("🎯 Avaliar Imóvel", "https://www.kwportugal.pt/pt/property-valuation")
with c2: st.link_button("🏦 Simular Crédito", "https://docs.google.com/forms/d/e/1FAIpQLSfiMOMKqZhnB14I5_DTrPLQrWYgiQdaw-O2HBfQBoLh4Qk5Ow/viewform")
with c3: st.link_button("📲 App Pessoal KW", "https://app.kw.com/KWNVLOD5AW4")

st.write("<br>", unsafe_allow_html=True)

# --- BLOCO PERFIL ---
st.markdown('<div class="main-protection-card">', unsafe_allow_html=True)
col_l, col_r = st.columns([1, 1.8])

with col_l:
    if os.path.exists("paulo_moreira.png"):
        img_b64 = get_base64("paulo_moreira.png")
        st.markdown(f'<img src="data:image/png;base64,{img_b64}" width="100%">', unsafe_allow_html=True)

# --- 🔥 JANELA DINÂMICA (CARROSSEL REAL) ---
with col_r:

    if not df.empty:
        placeholder = st.empty()

        for i in range(len(df)):
            row = df.iloc[i]

            imagem = escolher_imagem(row)
            texto = highlight(row)

            placeholder.markdown(f"""
            <div class="preview-window">
                <img src="{imagem}" style="width:100%; border-radius:10px;">
                <br><b>{row['Tipo']} | {row['Localidade']}</b><br>
                <span style="color:#bfa573;">{texto}</span>
            </div>
            """, unsafe_allow_html=True)

            time.sleep(2)

# --- FIM BLOCO ---
st.markdown('</div>', unsafe_allow_html=True)

# --- MONTRA 5D ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<h3 style='color:#1a1a1a;'>Activos Validados 5D</h3>", unsafe_allow_html=True)

for _, row in df.iterrows():

    img = escolher_imagem(row)

    st.markdown(f"""
    <div class="white-solid-box">
        <img src="{img}" style="width:100%; border-radius:8px;">
        <br><br>
        <b>{row['Localidade']} | {row['Tipo']}</b><br>
        Investimento: {row['Investimento_Total']:,.0f}€<br>
        ROI: <span style="color:#bfa573;"><b>{row['ROI_Percent']*100:.1f}%</b></span><br>
        Yield: {row['Yield_Euros_Ano']:,.0f}€
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        if row["Link_Fonte"]:
            st.link_button("Ver Activo", row["Link_Fonte"], use_container_width=True)

    with c2:
        msg = f"Olá Paulo, quero análise do activo {row['Referencia']}"
        st.link_button(
            "Pedir Deal Pack",
            f"https://wa.me/351911995695?text={urllib.parse.quote(msg)}",
            use_container_width=True
        )

    # alerta automático
    if row.get("Status_Scraping") == "novo":
        enviar_telegram(f"Novo activo detectado: {row['Referencia']} - {row['Localidade']}")
