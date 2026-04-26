import streamlit as st
import pandas as pd
import base64
import os
import time

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Paulo Moreira | Private Real Estate", layout="centered")

# ---------------- SESSION ----------------
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
fundo = get_base64("Background.svg")

st.markdown(f"""
<style>

.stApp {{
    background-image: url("data:image/svg+xml;base64,{fundo}");
    background-size: cover;
    background-attachment: fixed;
    background-position: center;
}}

/* OVERLAY DARK */
.stApp::before {{
    content: "";
    position: fixed;
    top:0; left:0;
    width:100%; height:100%;
    background: rgba(10,10,10,0.75);
    z-index: -1;
}}

/* TEXT */
.title {{
    text-align:center;
    font-size:30px;
    font-weight:300;
    color:white;
}}

.sub {{
    text-align:center;
    color:#aaa;
    margin-bottom:20px;
}}

/* PROFILE */
.profile {{
    width:140px;
    height:140px;
    border-radius:50%;
    overflow:hidden;
    margin:auto;
    border:3px solid rgba(255,255,255,0.2);
}}

.profile img {{
    width:100%;
    height:100%;
    object-fit:cover;
}}

/* CARD */
.card {{
    background: rgba(255,255,255,0.05);
    padding:15px;
    border-radius:18px;
    backdrop-filter: blur(10px);
    border:1px solid rgba(255,255,255,0.08);
    margin-bottom:15px;
}}

/* IMAGE */
.img {{
    width:100%;
    border-radius:12px;
}}

/* BUTTON */
div.stButton > button {{
    background:white;
    color:black;
    border-radius:12px;
    height:48px;
    border:none;
    font-weight:600;
}}

/* LOCK */
.lock {{
    border:1px dashed #666;
    padding:20px;
    border-radius:12px;
    text-align:center;
    margin-top:20px;
    color:#bbb;
}}

/* FOOTER */
.footer {{
    font-size:11px;
    text-align:center;
    color:#888;
    margin-top:40px;
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
    <div class="card">
        <img src="{row.get('Capa_Manual')}" class="img">
        <b>{row.get('Tipo')}</b><br>
        <span style="color:#aaa">{row.get('Localidade')}</span>
    </div>
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

    if os.path.exists("paulo_moreira.png"):
        img = get_base64("paulo_moreira.png")
        st.markdown(f"""
        <div class="profile">
            <img src="data:image/png;base64,{img}">
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="title">Paulo Moreira</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub">Private Real Estate Advisory</div>', unsafe_allow_html=True)

    carousel(df)

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
            <div class="card">
                <img src="{row.get('Capa_Manual')}" class="img">
                <b>{row.get('Tipo')}</b><br>
                <span style="color:#aaa">{row.get('Localidade')}</span><br>
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

        st.image(row.get("Capa_Manual"))

        st.markdown(f"""
        <h2>{row.get('Tipo')}</h2>
        <span style="color:#aaa">{row.get('Localidade')}</span>
        <h3>{preco:,.0f}€</h3>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="lock">
        🔒 Relatório Financeiro Premium<br><br>
        ROI | Flip | Yield | CAPEX
        </div>
        """, unsafe_allow_html=True)

        msg = f"Quero o relatório do imóvel {ref}"
        link = f"https://wa.me/351911995695?text={msg.replace(' ','%20')}"

        st.link_button("Desbloquear via WhatsApp", link)

# ---------------- SERVIÇOS ----------------
st.write("")
st.markdown("### Serviços")

s1, s2 = st.columns(2)

with s1:
    st.markdown("📈 **Estudo de Mercado**")
    st.markdown("Definição estratégica de preço com base em dados reais.")

    st.markdown("⚖️ **Apoio Jurídico**")
    st.markdown("Acompanhamento completo até escritura.")

with s2:
    st.markdown("📣 **Marketing Premium**")
    st.markdown("Exposição em +100 portais.")

    st.markdown("🏦 **Gestão de Crédito**")
    st.markdown("Soluções financeiras otimizadas.")

# ---------------- CONTACTOS ----------------
st.write("")
c1, c2, c3 = st.columns(3)

with c1:
    st.link_button("⭐ Reviews", "https://share.google/n4FLZO1p2tYTl2vsG")
with c2:
    st.link_button("📞 Ligar", "tel:+351911995695")
with c3:
    st.link_button("🟢 WhatsApp", "https://wa.me/351911995695")

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
<div class="footer">
Resumo Plural, Lda. | Licença AMI 21331<br>
Cada Market Center é de gestão independente
</div>
""", unsafe_allow_html=True)
