import streamlit as st
import pandas as pd
import urllib.parse
import os
import base64

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Paulo Moreira | Consultoria & Gestão", layout="centered")

def get_base64(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return ""

fundo_marmore = get_base64("Background.svg")

# ---------------- CSS ----------------
st.markdown(f"""
<style>
.stApp {{
    background-image: url("data:image/svg+xml;base64,{fundo_marmore}");
    background-size: cover;
}}

.main-card {{
    background-color: rgba(253, 250, 245, 0.98);
    padding: 25px;
    border-radius: 15px;
    border-left: 8px solid #bfa573;
    margin-bottom: 20px;
}}

.card-5d {{
    background: #ffffff;
    padding: 20px;
    border-radius: 12px;
    border-left: 6px solid #bfa573;
    margin-bottom: 15px;
}}

.metric {{
    font-size: 13px;
    color: #666;
}}

.value {{
    font-size: 18px;
    color: #bfa573;
    font-weight: bold;
}}
</style>
""", unsafe_allow_html=True)

# ---------------- FUNÇÕES 5D ----------------

def get_badge(status):
    return {
        "Novo": "🆕 Novo",
        "Validado": "✅ Validado",
        "Destaque": "⭐ Destaque"
    }.get(status, "🔍 Em análise")

def mostrar_alertas(row):
    alertas = []

    if row['Area_Bruta'] == row['Area_Terreno']:
        alertas.append("Áreas coincidem — validar implantação")

    if "recuperar" in str(row['Estado']).lower():
        alertas.append("Activo exige CAPEX")

    if alertas:
        with st.expander("⚠️ Notas Técnicas"):
            for a in alertas:
                st.warning(a)

def carregar_dados():
    SHEET_ID = "1PoK3Gj6mdLVkniIzDgFNhwmOGgpznRAIC0CGzweASag"
    URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
    return pd.read_csv(URL)

# ---------------- MONTRA (TEU CÓDIGO) ----------------

if os.path.exists("Paulo Moreira Consultoria & Gestão.png"):
    st.image("Paulo Moreira Consultoria & Gestão.png", use_container_width=True)

c1, c2, c3 = st.columns(3)
with c1: st.link_button("🎯 Avaliar Imóvel", "https://www.kwportugal.pt/pt/property-valuation")
with c2: st.link_button("🏦 Simular Crédito", "https://docs.google.com/forms/d/e/1FAIpQLSfiMOMKqZhnB14I5_DTrPLQrWYgiQdaw-O2HBfQBoLh4Qk5Ow/viewform")
with c3: st.link_button("📲 App KW", "https://app.kw.com/KWNVLOD5AW4")

# ---------------- BLOCO IDENTIDADE ----------------

st.markdown('<div class="main-card">', unsafe_allow_html=True)

col1, col2 = st.columns([1,2])

with col1:
    if os.path.exists("paulo_moreira.png"):
        st.image("paulo_moreira.png")

with col2:
    st.markdown("""
    **Consultor Imobiliário**

    # Paulo Moreira

    _"O papel aceita tudo, mas o terreno não engana."_

    Especialista em validação de activos com base em dados reais.
    """)

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- SCANNER 5D ----------------

st.markdown("## 🚀 Activos Validados (Filtro 5D+)")

try:
    df = carregar_dados()

    # FILTRO CORE
    df = df[df['Score_PM5D'] >= 3]

    for _, row in df.iterrows():

        st.markdown('<div class="card-5d">', unsafe_allow_html=True)

        c1, c2 = st.columns([2,1])

        with c1:
            st.markdown(f"**{get_badge(row.get('Status'))}**")
            st.markdown(f"### 📍 {row['Localidade']}")
            st.write(f"Ref: {row['Referencia']}")

        with c2:
            st.progress(int(row['Score_PM5D'])/5)

        m1, m2, m3 = st.columns(3)

        m1.markdown(f"<div class='metric'>Investimento</div><div class='value'>{row['Investimento_Total']:,.0f}€</div>", unsafe_allow_html=True)
        m2.markdown(f"<div class='metric'>ROI</div><div class='value'>{row['ROI_Percent']*100:.1f}%</div>", unsafe_allow_html=True)
        m3.markdown(f"<div class='metric'>Yield</div><div class='value'>{row['Yield_Euros_Ano']:,.0f}€</div>", unsafe_allow_html=True)

        mostrar_alertas(row)

        b1, b2 = st.columns(2)

        with b1:
            if pd.notna(row.get("Link_Fonte")):
                st.link_button("🌐 Ver Activo", row['Link_Fonte'], use_container_width=True)

        with b2:
            msg = f"Olá Paulo. Quero análise técnica do activo {row['Referencia']}"
            st.link_button(
                "📄 Pedir Relatório",
                f"https://wa.me/351911995695?text={urllib.parse.quote(msg)}",
                use_container_width=True
            )

        st.markdown('</div>', unsafe_allow_html=True)

except:
    st.info("Base de dados em actualização.")

# ---------------- CONTACTOS ----------------

st.markdown("### Contacto Directo")

c1, c2, c3 = st.columns(3)
with c1: st.link_button("⭐ Reviews", "https://share.google/n4FLZO1p2tYTl2vsG")
with c2: st.link_button("📞 Ligar", "tel:+351911995695")
with c3: st.link_button("🟢 WhatsApp", "https://wa.me/351911995695")
