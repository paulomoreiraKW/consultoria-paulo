import streamlit as st
import pandas as pd
import base64
import os
import time

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Paulo Moreira | Private Real Estate", layout="centered")

if "page" not in st.session_state:
    st.session_state.page = "HOME"

if "selected_imovel" not in st.session_state:
    st.session_state.selected_imovel = None

if "idx" not in st.session_state:
    st.session_state.idx = 0

if "last_update" not in st.session_state:
    st.session_state.last_update = time.time()

# ---------------- UTILS ----------------
def get_base64(file):
    if os.path.exists(file):
        with open(file, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

def safe_float(value):
    try:
        return float(str(value).replace("€","").replace(",","").strip())
    except:
        return 0

# ---------------- BACKGROUND ----------------
bg = get_base64("Background.svg")
perfil = get_base64("paulo_moreira.png")

# ---------------- DATA ----------------
SHEET_ID = "1PoK3Gj6mdLVkniIzDgFNhwmOGgpznRAIC0CGzweASag"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(URL)
        df = df.fillna("")
        df = df[pd.to_numeric(df["Score_PM5D"], errors="coerce").fillna(0) >= 3]
        return df.reset_index(drop=True)
    except:
        return pd.DataFrame()

df = load_data()

# ---------------- STYLE ----------------
st.markdown(f"""
<style>

.stApp {{
    background-image: url("data:image/svg+xml;base64,{bg}");
    background-size: cover;
    background-attachment: fixed;
}}

/* GLASS CARD */
.glass {{
    background: rgba(255,255,255,0.88);
    backdrop-filter: blur(12px);
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    margin-bottom: 15px;
}}

/* PROFILE */
.profile {{
    width:160px;
    height:160px;
    border-radius:50%;
    overflow:hidden;
    margin:auto;
    border:4px solid #bfa573;
}}

.profile img {{
    width:100%;
    height:100%;
    object-fit:cover;
}}

/* BUTTON */
div.stButton > button {{
    background:white;
    border-radius:12px;
    height:48px;
    font-weight:600;
}}

</style>
""", unsafe_allow_html=True)

# ---------------- TOP BUTTONS ----------------
c1, c2, c3 = st.columns(3)
with c1:
    st.link_button("🎯 Avaliar", "https://www.kwportugal.pt/pt/property-valuation")
with c2:
    st.link_button("🏦 Crédito", "https://docs.google.com/forms/d/e/1FAIpQLSfiMOMKqZhnB14I5_DTrPLQrWYgiQdaw-O2HBfQBoLh4Qk5Ow/viewform")
with c3:
    st.link_button("📲 App KW", "https://app.kw.com/KWNVLOD5AW4")

st.write("")

# ---------------- HOME ----------------
if st.session_state.page == "HOME":

    col1, col2 = st.columns([1,2])

    with col1:
        if perfil:
            st.markdown(f'<div class="profile"><img src="data:image/png;base64,{perfil}"></div>', unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="glass">
        <h2>Paulo Moreira</h2>
        <small>Private Real Estate Advisory</small><br><br>
        Estratégia, dados e execução focada em investidores.
        </div>
        """, unsafe_allow_html=True)

    # destaque
    if not df.empty:
        row = df.iloc[0]

        st.markdown(f"""
        <div class="glass">
            <img src="{row.get('Capa_Manual')}" style="width:100%; border-radius:12px;">
            <b>{row.get('Tipo')}</b><br>
            {row.get('Localidade')}
        </div>
        """, unsafe_allow_html=True)

    if st.button("Ver Oportunidades"):
        st.session_state.page = "LOJA"
        st.rerun()

# ---------------- LOJA ----------------
elif st.session_state.page == "LOJA":

    if st.button("← Voltar"):
        st.session_state.page = "HOME"
        st.rerun()

    cols = st.columns(2)

    for i, row in df.iterrows():
        with cols[i % 2]:
            preco = safe_float(row.get("Preço"))

            st.markdown(f"""
            <div class="glass">
                <img src="{row.get('Capa_Manual')}" style="width:100%; border-radius:12px;">
                <b>{row.get('Tipo')}</b><br>
                {row.get('Localidade')}<br><br>
                <b>{preco:,.0f}€</b>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Ver Detalhe", key=i):
                st.session_state.selected_imovel = row.to_dict()
                st.session_state.page = "DETALHE"
                st.rerun()

# ---------------- DETALHE ----------------
elif st.session_state.page == "DETALHE":

    row = st.session_state.selected_imovel

    if st.button("← Voltar"):
        st.session_state.page = "LOJA"
        st.rerun()

    if row:
        preco = safe_float(row.get("Preço"))
        ref = row.get("Referência")

        st.markdown(f"""
        <div class="glass">
            <img src="{row.get('Capa_Manual')}" style="width:100%; border-radius:12px;">
            <h2>{row.get('Tipo')}</h2>
            {row.get('Localidade')}<br>
            <b>{preco:,.0f}€</b>

            <div style="margin-top:20px; border:1px dashed #aaa; padding:15px; border-radius:10px;">
            🔒 Relatório Financeiro Premium<br>
            ROI | Flip | Yield | CAPEX
            </div>
        </div>
        """, unsafe_allow_html=True)

        msg = f"Quero relatório do imóvel {ref}"
        link = f"https://wa.me/351911995695?text={msg.replace(' ','%20')}"
        st.link_button("Desbloquear via WhatsApp", link)

# ---------------- LOGOS ----------------
st.write("")
l1, l2, l3 = st.columns(3)

with l1:
    if os.path.exists("P.M.M..png"):
        st.image("P.M.M..png", width=90)

with l2:
    if os.path.exists("REAL ESTATE.svg"):
        st.image("REAL ESTATE.svg", width=100)

with l3:
    if os.path.exists("area_feira.png"):
        st.image("area_feira.png", width=100)

# ---------------- FOOTER ----------------
st.markdown("""
<div class="glass" style="text-align:center; font-size:12px;">
Resumo Plural, Lda. | Licença AMI 21331<br>
Cada Market Center é de gestão independente
</div>
""", unsafe_allow_html=True)
