import streamlit as st
import base64
import os
import pandas as pd
import time

# ==============================
# ESTADO (NOVO - NÃO ALTERA UI)
# ==============================
if "page" not in st.session_state:
    st.session_state.page = "HOME"

if "selected_imovel" not in st.session_state:
    st.session_state.selected_imovel = None

st.set_page_config(page_title="Paulo Moreira | Consultoria & Gestão", layout="centered")

# ==============================
# FUNÇÕES AUXILIARES
# ==============================
def get_base64(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return ""

def safe_float(value):
    try:
        return float(str(value).replace("%","").replace(",",".").replace("€","").replace(" ","").strip())
    except:
        return 0

# ==============================
# DATA
# ==============================
SHEET_ID = "1PoK3Gj6mdLVkniIzDgFNhwmOGgpznRAIC0CGzweASag"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    df = pd.read_csv(URL)
    df = df.fillna("")

    df = df[pd.to_numeric(df["Score_PM5D"], errors="coerce").fillna(0) >= 3]

    if "Status_Scraping" in df.columns:
        df = df[df["Status_Scraping"].str.upper().isin(["OK", "APROVADO", "PUBLICAR"])]

    if "Decisão" in df.columns:
        df = df[df["Decisão"].str.upper().isin(["APROVADO", "SIM", "OK"])]

    df = df.reset_index(drop=True)
except:
    df = pd.DataFrame()

# ==============================
# ROUTER
# ==============================
if st.session_state.page == "LOJA":
    st.title("📊 Oportunidades disponíveis")

    if st.button("← Voltar"):
        st.session_state.page = "HOME"
        st.rerun()

    if df.empty:
        st.warning("Sem imóveis disponíveis")
    else:
        cols = st.columns(2)

        for i, row in df.iterrows():
            with cols[i % 2]:

                preco = safe_float(row.get("Preço", 0))
                area = safe_float(row.get("Área_Útil", 0))
                valor_m2 = int(preco / area) if area > 0 else 0

                st.markdown(f"""
                <div style="border:1px solid #ddd; padding:10px; border-radius:10px; margin-bottom:10px;">
                    <b>{row.get('Tipo','')}</b><br>
                    {row.get('Localidade','')}<br>
                    <b>{preco:,.0f}€</b><br>
                    <small>{valor_m2} €/m²</small>
                </div>
                """, unsafe_allow_html=True)

                if st.button("Ver detalhe", key=f"det_{i}"):
                    st.session_state.selected_imovel = row.to_dict()
                    st.session_state.page = "DETALHE"
                    st.rerun()

    st.stop()

if st.session_state.page == "DETALHE":
    row = st.session_state.selected_imovel

    if st.button("← Voltar à loja"):
        st.session_state.page = "LOJA"
        st.rerun()

    if row:
        preco = safe_float(row.get("Preço", 0))
        area = safe_float(row.get("Área_Útil", 0))
        valor_m2 = int(preco / area) if area > 0 else 0

        st.title(f"{row.get('Tipo','')} - {row.get('Localidade','')}")

        st.markdown(f"""
        **Preço:** {preco:,.0f}€  
        **Área:** {area} m²  
        **Preço/m²:** {valor_m2}
        """)

        msg = f"Olá, tenho interesse no imóvel Ref {row.get('Referência','')}"
        link = f"https://wa.me/351911995695?text={msg}"

        st.link_button("📲 Falar no WhatsApp", link)

    st.stop()

# ==============================
# HOME (100% IGUAL)
# ==============================

fundo_marmore = get_base64("Background.svg")

st.markdown(f"""
<style>
.stApp {{
    background-image: url("data:image/svg+xml;base64,{fundo_marmore}");
    background-size: cover;
    background-attachment: fixed;
}}
.preview-window {{
    border: 2px dashed #bfa573;
    background-color: #ffffff;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    min-height: 250px;
}}
.badge-estimado {{
    background-color: #fff3cd;
    color: #856404;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 10px;
}}
</style>
""", unsafe_allow_html=True)

if "idx" not in st.session_state:
    st.session_state.idx = 0

if not df.empty:

    if (time.time() - st.session_state.get("last_update", 0)) > 3:
        st.session_state.idx = (st.session_state.idx + 1) % len(df)
        st.session_state.last_update = time.time()
        st.rerun()

    row = df.iloc[st.session_state.idx]

    preco = safe_float(row.get("Preço", 0))
    area = safe_float(row.get("Área_Útil", 0))
    valor_m2 = int(preco / area) if area > 0 else 0
    notas = str(row.get("Notas", ""))

    badge_html = ""
    if "AREA_ESTIMADA" in notas.upper():
        badge_html = '<div class="badge-estimado">⚠️ Área Estimada</div>'

    st.markdown(f"""
    <div class="preview-window">
        <b>{row.get('Tipo','')} | {row.get('Localidade','')}</b><br>
        <span style="font-size:24px;">{preco:,.0f}€</span><br>
        <small>{valor_m2} €/m²</small>
        {badge_html}
    </div>
    """, unsafe_allow_html=True)

    # 👇 BOTÃO NOVO (ÚNICA ALTERAÇÃO REAL)
    if st.button("🔎 Ver todos os imóveis"):
        st.session_state.page = "LOJA"
        st.rerun()

else:
    st.markdown('<div class="preview-window">Sincronizando Ativos...</div>', unsafe_allow_html=True)
