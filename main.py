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

# ---------------- BACKGROUND ----------------
bg = get_base64("Background.svg")

st.markdown(f"""
<style>

.stApp {{
    background-image: url("data:image/svg+xml;base64,{bg}");
    background-size: cover;
    background-attachment: fixed;
}}

/* CONTAINER PRINCIPAL */
.box {{
    background: rgba(255,255,255,0.92);
    padding: 25px;
    border-radius: 14px;
    margin-bottom: 20px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}}

/* CARDS */
.card {{
    background: white;
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 15px;
    border-bottom: 3px solid #bfa573;
}}

/* PREVIEW CONTROLADO */
.preview {{
    height: 260px;
    overflow: hidden;
    border-radius: 12px;
}}

.preview img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
}}

/* PERFIL */
.profile {{
    width:140px;
    height:140px;
    border-radius:50%;
    overflow:hidden;
    margin:auto;
    border:4px solid #bfa573;
}}

/* SERVIÇOS */
.service {{
    background:white;
    padding:15px;
    border-radius:10px;
    border-bottom:3px solid #bfa573;
    min-height:140px;
}}

.footer {{
    font-size:11px;
    text-align:center;
    margin-top:30px;
}}

</style>
""", unsafe_allow_html=True)

# ---------------- CAROUSEL ----------------
def carousel(df):
    if df.empty:
        return

    if time.time() - st.session_state.last_update > 3:
        st.session_state.idx = (st.session_state.idx + 1) % len(df)
        st.session_state.last_update = time.time()
        st.rerun()

    row = df.iloc[st.session_state.idx]

    st.markdown(f"""
    <div class="preview">
        <img src="{row.get('Capa_Manual')}">
    </div>
    <b>{row.get('Tipo')}</b><br>
    <span>{row.get('Localidade')}</span>
    """, unsafe_allow_html=True)

# ---------------- TOP BUTTONS ----------------
c1, c2, c3 = st.columns(3)
with c1:
    st.link_button("🎯 Avaliar", "https://www.kwportugal.pt/pt/property-valuation")
with c2:
    st.link_button("🏦 Crédito", "https://docs.google.com/forms/d/e/1FAIpQLSfiMOMKqZhnB14I5_DTrPLQrWYgiQdaw-O2HBfQBoLh4Qk5Ow/viewform")
with c3:
    st.link_button("📲 App KW", "https://app.kw.com/KWNVLOD5AW4")

# ---------------- HOME ----------------
if st.session_state.page == "HOME":

    st.markdown('<div class="box">', unsafe_allow_html=True)

    if os.path.exists("paulo_moreira.png"):
        img = get_base64("paulo_moreira.png")
        st.markdown(f'<div class="profile"><img src="data:image/png;base64,{img}" width="100%"></div>', unsafe_allow_html=True)

    st.markdown("### Paulo Moreira")
    st.markdown("Consultoria Imobiliária Premium")

    carousel(df)

    if st.button("Ver Oportunidades"):
        st.session_state.page = "LOJA"
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- LOJA ----------------
elif st.session_state.page == "LOJA":

    st.markdown('<div class="box">', unsafe_allow_html=True)

    if st.button("← Voltar"):
        st.session_state.page = "HOME"
        st.rerun()

    cols = st.columns(2)

    for i, row in df.iterrows():
        with cols[i % 2]:

            preco = safe_float(row.get("Preço"))

            st.markdown(f"""
            <div class="card">
                <div class="preview">
                    <img src="{row.get('Capa_Manual')}">
                </div>
                <b>{row.get('Tipo')}</b><br>
                <span>{row.get('Localidade')}</span><br>
                <b>{preco:,.0f}€</b>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Ver Detalhe", key=i):
                st.session_state.selected_imovel = row.to_dict()
                st.session_state.page = "DETALHE"
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- DETALHE ----------------
elif st.session_state.page == "DETALHE":

    row = st.session_state.selected_imovel

    st.markdown('<div class="box">', unsafe_allow_html=True)

    if st.button("← Voltar"):
        st.session_state.page = "LOJA"
        st.rerun()

    if row:
        preco = safe_float(row.get("Preço"))
        ref = row.get("Referência")

        st.image(row.get("Capa_Manual"))

        st.markdown(f"### {row.get('Tipo')}")
        st.markdown(row.get("Localidade"))
        st.markdown(f"## {preco:,.0f}€")

        st.markdown("""
        <div style="border:2px dashed #bfa573; padding:20px; border-radius:10px; text-align:center;">
        🔒 Relatório Financeiro Premium
        </div>
        """, unsafe_allow_html=True)

        msg = f"Quero o relatório do imóvel {ref}"
        link = f"https://wa.me/351911995695?text={msg.replace(' ','%20')}"

        st.link_button("Desbloquear via WhatsApp", link)

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- SERVIÇOS ----------------
st.markdown('<div class="box">', unsafe_allow_html=True)

st.markdown("### Serviços")

s1, s2 = st.columns(2)

with s1:
    st.markdown('<div class="service">📈 Estudo de Mercado</div>', unsafe_allow_html=True)
    st.markdown('<div class="service">⚖️ Apoio Jurídico</div>', unsafe_allow_html=True)

with s2:
    st.markdown('<div class="service">📣 Marketing Premium</div>', unsafe_allow_html=True)
    st.markdown('<div class="service">🏦 Gestão de Crédito</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.markdown("""
<div class="footer">
Resumo Plural, Lda. | Licença AMI 21331<br>
Cada Market Center é de gestão independente
</div>
""", unsafe_allow_html=True)
