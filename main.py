import streamlit as st
import base64
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Paulo Moreira | Consultoria & Gestão", layout="centered")

def get_base64(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return ""

fundo_marmore = get_base64("Background.svg")

# --- CSS DE PRECISÃO FINAL ---
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
        transition: transform 0.3s ease;
    }}
    .service-box:hover {{ transform: translateY(-5px); }}
    .service-title {{ color: #1a1a1a; font-weight: 800; font-size: 15px; margin-bottom: 5px; display: block; }}
    .service-desc {{ color: #555; font-size: 12.5px; line-height: 1.4; }}

    .profile-frame {{
        width: 180px; height: 180px;
        border-radius: 50%; border: 4px solid #bfa573;
        overflow: hidden; margin: 0 auto 15px auto;
        background: white;
    }}
    .profile-frame img {{ width: 100%; height: 100%; object-fit: cover; }}

    .cargo-text {{ color: #1a1a1a !important; font-weight: 700 !important; letter-spacing: 2px; text-transform: uppercase; font-size: 13px; }}
    .quote-style {{ font-style: italic; color: #bfa573; font-size: 15px; margin: 10px 0; border-left: 2px solid #bfa573; padding-left: 10px; }}
    .bio-text {{ font-size: 14px; color: #333; line-height: 1.5; }}

    div.stButton > button {{
        width: 100% !important;
        height: 52px !important;
        background-color: white !important;
        color: #1a1a1a !important;
        border: 1px solid #1a1a1a !important;
        font-weight: 600 !important;
        text-transform: none !important;
        font-size: 14px !important;
        margin-top: 5px;
    }}
    div.stButton > button:hover {{ background-color: #1a1a1a !important; color: white !important; }}

    .action-link {{
        display: inline-block;
        padding: 8px 15px;
        background: #1a1a1a;
        color: white !important;
        text-decoration: none !important;
        border-radius: 2px;
        font-size: 11px;
        font-weight: bold;
        margin-top: 10px;
        text-transform: uppercase;
    }}

    .legal-footer-box {{
        font-size: 11px; color: #444; text-align: center; padding: 25px;
        background: rgba(253, 250, 245, 0.99); border-radius: 10px;
        border: 1px dashed #bfa573; margin-top: 30px; line-height: 1.8;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- CONTEÚDO ---

if os.path.exists("Paulo Moreira Consultoria & Gestão.png"):
    st.image("Paulo Moreira Consultoria & Gestão.png", use_container_width=True)

c1, c2, c3 = st.columns(3)
with c1: st.link_button("🎯 Avaliar Imóvel", "https://www.kwportugal.pt/pt/property-valuation")
with c2: st.link_button("🏦 Simular Crédito", "https://docs.google.com/forms/d/e/1FAIpQLSfiMOMKqZhnB14I5_DTrPLQrWYgiQdaw-O2HBfQBoLh4Qk5Ow/viewform")
with c3: st.link_button("📲 App Pessoal KW", "https://app.kw.com/KWNVLOD5AW4")

st.write("<br>", unsafe_allow_html=True)

st.markdown('<div class="main-protection-card">', unsafe_allow_html=True)
col_l, col_r = st.columns([1, 1.8])

with col_l:
    if os.path.exists("paulo_moreira.png"):
        img_b64 = get_base64("paulo_moreira.png")
        st.markdown(f'<div class="profile-frame"><img src="data:image/png;base64,{img_b64}"></div>', unsafe_allow_html=True)
    st.link_button("📸 Instagram", "https://www.instagram.com/paulomgmoreira/")
    st.link_button("🔵 Facebook", "https://www.facebook.com/PMMConsultoriaEGestao/")

with col_r:
    st.markdown("""<div class="white-solid-box">
        <div class="cargo-text">Consultor Imobiliário</div>
        <h1 style="color:#1a1a1a; font-size:32px; font-weight:300; margin:5px 0;">Paulo Moreira</h1>
        <div class="quote-style">"O sucesso de uma transação imobiliária depende de estratégia, não de sorte."</div>
        <div class="bio-text">Especialista em ativos residenciais e industriais. Através da <b>Metodologia 5D</b>, garanto um acompanhamento técnico, jurídico e comercial de excelência.</div>
    </div>""", unsafe_allow_html=True)

# --- JANELA DINÂMICA ESTÁVEL (SEM BLOQUEIO) ---

import pandas as pd

SHEET_ID = "1PoK3Gj6mdLVkniIzDgFNhwmOGgpznRAIC0CGzweASag"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    df = pd.read_csv(URL)
    df = df.fillna("")
    df = df[df["Score_PM5D"] >= 3]
except:
    df = pd.DataFrame()

# índice de rotação (não bloqueia UI)
if "idx" not in st.session_state:
    st.session_state.idx = 0

if not df.empty:
    row = df.iloc[st.session_state.idx % len(df)]

    # prioridade imagem
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
        <img src="{imagem}" style="width:100%; border-radius:10px;">
        <br><b>{row.get('Tipo','')} | {row.get('Localidade','')}</b><br>
        <span style="color:#bfa573;">{destaque}</span>
    </div>
    """, unsafe_allow_html=True)

    # botão para rodar manualmente (fase 1 estável)
    if st.button("🔄 Ver próximo ativo"):
        st.session_state.idx += 1
        st.rerun()

else:
    # fallback (NUNCA deixa vazio)
    st.markdown("""
    <div class="preview-window">
        <span style="font-size:40px;">🖼️</span>
        <b style="font-size:18px;">Visualização Estratégica do Imóvel</b>
        <span style="font-size:11px; color:#999;">
            A carregar dados...
        </span>
    </div>
    """, unsafe_allow_html=True)
st.markdown('<div class="main-protection-card" style="border-left:none; border-top:6px solid #1a1a1a; padding-top:20px;">', unsafe_allow_html=True)
m1, m2 = st.columns(2)
with m1:
    st.markdown(f"""<div class="service-box">
        <span class="service-title">📈 Estudo de Mercado</span>
        <span class="service-desc">Análise profunda baseada em dados reais e comparativos para definir o valor certo de venda.</span><br>
        <a href="https://www.kwportugal.pt/pt/property-valuation" class="action-link">Avaliar Imóvel</a>
    </div>""", unsafe_allow_html=True)

    st.markdown("""<div class="service-box">
        <span class="service-title">⚖️ Apoio Jurídico</span>
        <span class="service-desc">Segurança total na documentação, elaboração de CPCV e acompanhamento rigoroso até à escritura.</span>
    </div>""", unsafe_allow_html=True)

with m2:
    st.markdown("""<div class="service-box">
        <span class="service-title">📣 Plano de Marketing</span>
        <span class="service-desc">Exposição premium em mais de 100 portais nacionais e internacionais com fotografia profissional.</span>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""<div class="service-box">
        <span class="service-title">🏦 Gestão de Crédito</span>
        <span class="service-desc">Intermediação de crédito certificada para encontrar as melhores condições de financiamento.</span><br>
        <a href="https://docs.google.com/forms/d/e/1FAIpQLSfiMOMKqZhnB14I5_DTrPLQrWYgiQdaw-O2HBfQBoLh4Qk5Ow/viewform" class="action-link">Simular Crédito</a>
    </div>""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# 5. CONTACTOS (ALINHADOS EM 3 COLUNAS)
st.write("<br>", unsafe_allow_html=True)
ba, bb, bc = st.columns(3)
with ba: st.link_button("⭐ Google Reviews", "https://share.google/n4FLZO1p2tYTl2vsG")
with bb: st.link_button("📞 Ligar Agora", "tel:+351911995695")
with bc: st.link_button("🟢 Whatsapp", "https://wa.me/351911995695")

st.write("<br>", unsafe_allow_html=True)
f1, f2, f3 = st.columns([1, 1, 1])
with f1: 
    if os.path.exists("P.M.M..png"): st.image("P.M.M..png", width=100)
with f2: 
    if os.path.exists("REAL ESTATE.svg"): st.image("REAL ESTATE.svg", width=110)
with f3: 
    if os.path.exists("area_feira.png"): st.image("area_feira.png", width=110)

st.markdown("""<div class="legal-footer-box">
    <b>Resumo Plural, Lda.</b> - Licença AMI 21331 - Pessoa Coletiva 517 033 224 <br>
    Morada comercial: Rua Estrada Nacional, nº 1190, 1200 – Zona Ind. do Roligo, 4520-115 Espargo <br>
    Tel.: 256 313 054 | kwareafeira@kwportugal.pt | www.kwportugal.pt | <br>
    <b>Cada Market Center é de gestão independente</b>
</div>""", unsafe_allow_html=True)


