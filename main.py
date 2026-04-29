import streamlit as st
import base64
import os
import pandas as pd
import time
import requests
import re
import hashlib
from utils import calcular_score, get_zona_label

# ==========================================
# 1. CONFIGURAÇÕES E ESTADO DA SESSÃO
# ==========================================
if "page" not in st.session_state: st.session_state.page = "HOME"
if "selected_imovel" not in st.session_state: st.session_state.selected_imovel = None
if "idx" not in st.session_state: st.session_state.idx = 0

st.set_page_config(page_title="Paulo Moreira | Consultoria & Gestão", layout="centered")

# --- Funções de Suporte ---
def get_base64(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return ""

def safe_float(value):
    if value is None or value == "": return 0.0
    try:
        val_str = str(value).replace("€","").replace("%","").replace(" ","").replace("\xa0","").strip()
        if "." in val_str and "," in val_str: val_str = val_str.replace(".", "").replace(",", ".")
        elif "," in val_str: val_str = val_str.replace(",", ".")
        return float(val_str)
    except: return 0.0

# ==========================================
# 2. CÉREBRO 2026 - CARREGAMENTO E FILTROS
# ==========================================
SHEET_ID = "1PoK3Gj6mdLVkniIzDgFNhwmOGgpznRAIC0CGzweASag"
URL_LEADS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=LEADS"
URL_CONFIG = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=CONFIG_MERCADO"

@st.cache_data(ttl=600) # Atualiza a cada 10 min
def load_and_process_brain():
    try:
        df_bruto = pd.read_csv(URL_LEADS).fillna("")
        df_conf = pd.read_csv(URL_CONFIG).fillna("")
        
        # Cálculos de Inteligência
        df_bruto["Area_m2"] = df_bruto["Area_m2"].apply(safe_float)
        df_bruto["Preco_Listagem"] = df_bruto["Preco_Listagem"].apply(safe_float)
        
        df_bruto["Score_Calculado"] = df_bruto.apply(
            lambda row: calcular_score(
                row.get("Titulo") or "", 
                row["Preco_Listagem"], 
                row.get("Localidade", ""), 
                row["Area_m2"], 
                df_conf
            ), axis=1
        )
        
        # Filtro de Qualidade: Apenas Score >= 1 (ou o que definires como mínimo para público)
        df_final = df_bruto[df_bruto["Score_Calculado"] >= 1].copy()
        
        # Se houver coluna de Decisão manual, respeitá-la
        if "Decisao" in df_final.columns:
            df_final = df_final[df_final["Decisao"].str.upper().isin(["APROVADO", "SIM", "OK", ""])]
            
        return df_final.sort_values(by="Score_Calculado", ascending=False).reset_index(drop=True)
    except:
        return pd.DataFrame()

df = load_and_process_brain()

# ==========================================
# 3. COMPONENTES VISUAIS (CARROSSEL)
# ==========================================
@st.fragment(run_every=3)
def render_carousel_fragment(df_data):
    if not df_data.empty:
        # Garante que o índice não ultrapassa o tamanho atual do DF
        current_idx = st.session_state.idx % len(df_data)
        row = df_data.iloc[current_idx]
        
        st.markdown(f"""
        <div class="preview-window">
            <img src="{row.get('Capa_Manual','')}" style="width:100%; height:120px; object-fit:cover; border-radius:8px; margin-bottom:5px;">
            <div style="font-size:12px; color:#1a1a1a;"><b>{row.get('Tipo')} | {row.get('Localidade')}</b></div>
            <div style="font-size:11px; color:#bfa573;">Score Metodologia 5D: {row.get('Score_Calculado')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.session_state.idx = (current_idx + 1) % len(df_data)
    else:
        st.markdown('<div class="preview-window">Sincronizando Ativos...</div>', unsafe_allow_html=True)

# ==========================================
# 4. ESTILIZAÇÃO E LAYOUT (CSS CONSOLIDADO)
# ==========================================
fundo_marmore = get_base64("Background.svg")

st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/svg+xml;base64,{fundo_marmore}");
        background-size: cover;
        background-attachment: fixed;
    }}
    
    /* Botões e Links */
    div.stButton > button, div.stDownloadButton > button, .stLinkButton > a {{
        width: 100% !important;
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 12px !important;
        font-weight: 500 !important;
        padding: 10px 20px !important;
        transition: all 0.3s ease-in-out !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
        text-decoration: none !important;
        display: flex !important;
        justify-content: center !important;
    }}
    
    div.stButton > button:hover, div.stDownloadButton > button:hover, .stLinkButton > a:hover {{
        background-color: transparent !important;
        color: #1a1a1a !important;
        border-color: #bfa573 !important;
        transform: translateY(-1px) !important;
    }}

    /* Estrutura de Cards */
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
        padding: 10px;
        border-radius: 12px;
        text-align: center;
        color: #bfa573;
        font-weight: 600;
        min-height: 120px;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
    }}

    /* Serviços e Perfil */
    .service-box {{
        background-color: white;
        padding: 18px;
        border-radius: 10px;
        border-bottom: 3px solid #bfa573;
        margin-bottom: 15px;
        min-height: 155px;
    }}

    .service-title {{ color: #1a1a1a; font-weight: 800; font-size: 15px; margin-bottom: 5px; display: block; }}
    .service-desc {{ color: #555; font-size: 12.5px; line-height: 1.4; }}
    
    .profile-frame {{
        width: 180px; height: 180px;
        border-radius: 50%; border: 4px solid #bfa573;
        overflow: hidden; margin: 0 auto 15px auto;
        background: white;
    }}
    .profile-frame img {{ width: 100%; height: 100%; object-fit: cover; }}
    
    .legal-footer-box {{
        font-size: 11px; color: #444; text-align: center; padding: 25px;
        background: rgba(253, 250, 245, 0.99); border-radius: 10px;
        border: 1px dashed #bfa573; margin-top: 30px; line-height: 1.8;
    }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 6. DINÂMICA DE PÁGINAS E CARROSSEL
# ==========================================

@st.fragment(run_every=3)  
def render_carousel_fragment(df_data):
    if not df_data.empty:
        if "idx" not in st.session_state:
            st.session_state.idx = 0
            
        row = df_data.iloc[st.session_state.idx]
        
        st.markdown(f"""
        <div class="preview-window">
            <img src="{row.get('Capa_Manual','')}" style="width:100%; height:120px; object-fit:cover; border-radius:8px; margin-bottom:5px;">
            <div style="font-size:12px;"><b>{row.get('Tipo')} | {row.get('Localidade')}</b></div>
        </div>
        """, unsafe_allow_html=True)

        st.session_state.idx = (st.session_state.idx + 1) % len(df_data)

# Banner Principal e Botões de Topo
if os.path.exists("Paulo Moreira Consultoria & Gestão.png"):
    st.image("Paulo Moreira Consultoria & Gestão.png", use_container_width=True)

c1, c2, c3 = st.columns(3)
with c1: st.link_button("🎯 Avaliar Imóvel", "https://www.kwportugal.pt/pt/property-valuation")
with c2: st.link_button("🏦 Simular Crédito", "https://docs.google.com/forms/d/e/1FAIpQLSfiMOMKqZhnB14I5_DTrPLQrWYgiQdaw-O2HBfQBoLh4Qk5Ow/viewform")
with c3: st.link_button("📲 App Pessoal KW", "https://app.kw.com/KWNVLOD5AW4")

st.write("<br>", unsafe_allow_html=True)

# --- LÓGICA DE NAVEGAÇÃO ---

if st.session_state.page == "LOJA":
    st.markdown('<div class="main-protection-card">', unsafe_allow_html=True)
    if st.button("← Voltar ao Perfil"):
        st.session_state.page = "HOME"
        st.rerun()
    
    if df.empty:
        st.warning("A carregar ativos...")
    else:
        cols = st.columns(2)
        for i, row in df.iterrows():
            with cols[i % 2]:
                preco = safe_float(row.get("Preco_Listagem", 0))
                st.markdown(f"""
                <div class="white-solid-box" style="min-height:350px;">
                    <img src="{row.get('Capa_Manual', '')}" style="width:100%; border-radius:10px; margin-bottom:10px;">
                    <b style="font-size:16px;">{row.get('Tipo')}</b><br>
                    <span style="color:#666; font-size:13px;">{row.get('Localidade')}</span><br>
                    <b style="font-size:18px; color:#bfa573;">{preco:,.0f}€</b>
                    <div style="margin-top: 15px;">
                        <a href="{row.get('Link_Fonte', '')}" target="_blank" style="text-decoration: none;">
                            <span style="color: #bfa573; font-size: 10px; font-weight: bold; text-transform: uppercase; border-bottom: 1px solid #bfa573; padding-bottom: 2px;">
                                🔗 Consultar Fonte KW
                            </span>
                        </a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Ficha Técnica Ref: {row.get('Referencia')}", key=f"gal_{i}"):
                    st.session_state.selected_imovel = row.to_dict()
                    st.session_state.page = "DETALHE"
                    st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "DETALHE":
    row = st.session_state.selected_imovel
    st.markdown('<div class="main-protection-card">', unsafe_allow_html=True)
    if st.button("← Voltar à Galeria"):
        st.session_state.page = "LOJA"
        st.rerun()
    
    if row:
        ref = row.get("Referencia", "N/A")
        invest_total = safe_float(row.get("Investimento_Total", 0))
        capex_base = safe_float(row.get("CAPEX_Estimado", 0))
        exit_base = safe_float(row.get("Preco_Exit", 0))

        st.markdown(f"""
            <div class="white-solid-box" style="margin-top:15px; border-bottom: 2px solid #1a1a1a;">
                <h2 style="color:#1a1a1a; margin:0; font-weight:300; font-size:22px;">{row.get('Tipo')} em {row.get('Localidade')}</h2>
                <small style="color:#bfa573; font-weight:bold; letter-spacing:1px;">REFERÊNCIA: {ref}</small>
            </div>
            <div style="width:100%; height:300px; background-color:#ffffff; overflow:hidden; border-radius:12px; margin-bottom:10px; display:flex; align-items:center; justify-content:center; box-shadow: inset 0 0 10px rgba(0,0,0,0.05);">
                <img src="{row.get('Capa_Manual','')}" style="max-width:100%; max-height:100%; object-fit:contain;">
            </div>
        """, unsafe_allow_html=True)

        # Bloco do Simulador
        st.markdown('<div style="background-color: #ffffff; padding: 10px 25px; border-radius: 12px; border: 1px solid #bfa573; margin: 5px auto; max-width: 600px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);"><p class="titulo-simulador">🛠️ Simulador de Investimento</p>', unsafe_allow_html=True)
        col_sim1, col_sim2 = st.columns(2)
        with col_sim1:
            novo_capex = st.number_input("**Estimativa de Obra (€)**", value=capex_base, step=1000.0)
        with col_sim2:
            novo_exit = st.number_input("**Preço de Venda Alvo (€)**", value=exit_base if exit_base > 0 else 0.0, step=1000.0)
        st.markdown("</div>", unsafe_allow_html=True)

        # Lógica de cálculo de lucro e envio de Lead (conforme o teu código original)
        lucro_estimado = novo_exit - invest_total - (novo_capex - capex_base) if novo_exit > 0 else 0.0
        
        st.markdown(f"""
            <div style="max-width: 600px; margin: 10px auto; text-align:center; padding: 25px; background: rgba(255, 255, 255, 0.4); backdrop-filter: blur(10px); border-radius: 12px; border: 1px solid rgba(255,255,255,0.2);">
                <span style="color:#1a1a1a; font-size:12px; text-transform: uppercase; font-weight: bold;">Projeção de Lucro Flip</span><br>
                <span style="color:#bfa573; font-size:42px; font-weight:bold;">{lucro_estimado:,.2f}€</span>
            </div>
        """, unsafe_allow_html=True)

        lead_contacto = st.text_input("Identifique-se para o relatório:", placeholder="Nome ou Email...")
        if st.button("🔓 Solicitar Relatório Completo"):
            # Aqui corre a tua função enviar_para_sheet e lógica WhatsApp
            st.info("A processar pedido...") 

    st.markdown('</div>', unsafe_allow_html=True)

else: # HOME PAGE
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
            <div class="bio-text">Especialista em ativos residenciais e industriais. Através da <b>Metodologia 5D</b>, garanto um acompanhamento técnico.</div>
        </div>""", unsafe_allow_html=True)

        if not df.empty:
            render_carousel_fragment(df)
            if st.button("📂 VER TODOS OS IMÓVEIS DISPONÍVEIS", use_container_width=True):
                st.session_state.page = "LOJA"
                st.rerun()
        else:
            st.markdown('<div class="preview-window">Sincronizando Ativos...</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# NOVO BLOCO CONSOLIDADO (SERVIÇOS + CONTACTOS + RODAPÉ)
# ==========================================

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

st.write("<br>", unsafe_allow_html=True)

# Botões de Ação Rápida
ba, bb, bc = st.columns(3)
with ba: st.link_button("⭐ Google Reviews", "https://share.google/n4FLZO1p2tYTl2vsG")
with bb: st.link_button("📞 Ligar Agora", "tel:+351911995695")
with bc: st.link_button("🟢 Whatsapp", "https://wa.me/351911995695")

st.write("<br>", unsafe_allow_html=True)

# Logótipos de Parceiros/Empresa
f1, f2, f3 = st.columns([1, 1, 1])
with f1:
    if os.path.exists("P.M.M..png"): st.image("P.M.M..png", width=100)
with f2:
    if os.path.exists("REAL ESTATE.svg"): st.image("REAL ESTATE.svg", width=110)
with f3:
    if os.path.exists("area_feira.png"): st.image("area_feira.png", width=110)

# Rodapé Legal
st.markdown("""<div class="legal-footer-box">
    <b>Resumo Plural, Lda.</b> - Licença AMI 21331 - Pessoa Coletiva 517 033 224 <br>
    Morada comercial: Rua Estrada Nacional, nº 1190, 1200 – Zona Ind. do Roligo, 4520-115 Espargo <br>
    Tel.: 256 313 054 | kwareafeira@kwportugal.pt | www.kwportugal.pt | <br>
    <b>Cada Market Center é de gestão independente</b>
</div>""", unsafe_allow_html=True)
