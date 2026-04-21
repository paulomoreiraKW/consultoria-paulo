import streamlit as st
import pandas as pd
import urllib.parse
import os
import base64

# --- CONFIGURAÇÃO (Mantendo o teu padrão) ---
st.set_page_config(page_title="Paulo Moreira | Consultoria & Gestão", layout="centered")

def get_base64(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return ""

fundo_marmore = get_base64("Background.svg")

# --- CSS (Preservando a tua Identidade Visual) ---
st.markdown(f"""
    <style>
    .stApp {{ background-image: url("data:image/svg+xml;base64,{fundo_marmore}"); background-size: cover; background-attachment: fixed; }}
    .main-protection-card {{
        background-color: rgba(253, 250, 245, 0.99); padding: 25px 35px;
        border-radius: 15px; border-left: 8px solid #bfa573;
        box-shadow: 0 15px 35px rgba(0,0,0,0.15); margin-bottom: 15px;
    }}
    .white-solid-box {{
        background-color: #ffffff; padding: 20px; border-radius: 10px;
        border-bottom: 3px solid #bfa573; margin-bottom: 15px;
    }}
    /* Estilo para os novos cards de imóveis */
    .card-5d {{
        background: #ffffff; padding: 20px; border-radius: 12px;
        border-left: 10px solid #bfa573; box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px; color: #1a1a1a;
    }}
    </style>
    """, unsafe_allow_html=True)

# 1. LOGO E CABEÇALHO ORIGINAIS
if os.path.exists("Paulo Moreira Consultoria & Gestão.png"):
    st.image("Paulo Moreira Consultoria & Gestão.png", use_container_width=True)

# 2. OS TEUS FORMULÁRIOS E LINKS (INTACTOS)
st.markdown('<div class="main-protection-card">', unsafe_allow_html=True)
col_app, col_cred = st.columns(2)

with col_app:
    st.markdown(f"""<div class="white-solid-box">
        <span style="font-weight:bold;">📱 KW App</span><br>
        <span style="font-size:13px;">Aceda ao mercado imobiliário em tempo real.</span><br><br>
        <a href="https://app.kwportugal.pt/KW2S9I4P" style="color:#bfa573; font-weight:bold; text-decoration:none;">Descarregar App</a>
    </div>""", unsafe_allow_html=True)

with col_cred:
    st.markdown(f"""<div class="white-solid-box">
        <span style="font-weight:bold;">🏦 Gestão de Crédito</span><br>
        <span style="font-size:13px;">Intermediação certificada para financiamento.</span><br><br>
        <a href="https://docs.google.com/forms/d/e/1FAIpQLSfiMOMKqZhnB14I5_DTrPLQrWYgiQdaw-O2HBfQBoLh4Qk5Ow/viewform" style="color:#bfa573; font-weight:bold; text-decoration:none;">Simular Crédito</a>
    </div>""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# 3. O MÓDULO DE DADOS (SCANNER 5D) - A ADIÇÃO "8K"
st.markdown("<h3 style='text-align:center; color:#1a1a1a;'>🚀 Ativos Selecionados 5D+</h3>", unsafe_allow_html=True)

try:
    SHEET_ID = "1PoK3Gj6mdLVkniIzDgFNhwmOGgpznRAIC0CGzweASag"
    URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
    df = pd.read_csv(URL)
    
    # Filtro: Apenas o que decidires na Sheet (Score >= 3)
    df_filtered = df[df['Score_PM5D'] >= 3]
    
    for _, row in df_filtered.iterrows():
        with st.container():
            st.markdown(f'''
            <div class="card-5d">
                <h4 style="margin:0;">📍 {row['Localidade']} | Ref: {row['Referencia']}</h4>
                <p style="font-size:14px; margin:5px 0;">Investimento Total: <b>{row['Investimento_Total']:,.0f}€</b> | ROI Est.: <b style="color:#bfa573;">{row['ROI_Percent']*100:.1f}%</b></p>
            </div>
            ''', unsafe_allow_html=True)
            
            b1, b2 = st.columns(2)
            with b1:
                if pd.notna(row['Link_Fonte']):
                    st.link_button("🌐 Ver na KW", row['Link_Fonte'], use_container_width=True)
            with b2:
                msg = f"Olá Paulo, quero o Deal Pack da Ref {row['Referencia']}"
                st.link_button("📄 Pedir Deal Pack", f"https://wa.me/351911995695?text={urllib.parse.quote(msg)}", use_container_width=True)

except Exception:
    st.info("A atualizar listagem de ativos...")

# 4. RODAPÉ E CONTACTOS ORIGINAIS (INTACTOS)
st.write("<br>", unsafe_allow_html=True)
ba, bb, bc = st.columns(3)
with ba: st.link_button("⭐ Reviews", "https://share.google/n4FLZO1p2tYTl2vsG")
with bb: st.link_button("📞 Ligar", "tel:+351911995695")
with bc: st.link_button("🟢 Whatsapp", "https://wa.me/351911995695")

if os.path.exists("P.M.M..png"):
    st.image("P.M.M..png", width=80)
