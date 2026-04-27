import streamlit as st
import base64
import os
import pandas as pd
import time

if "page" not in st.session_state:
    st.session_state.page = "HOME"

if "selected_imovel" not in st.session_state:
    st.session_state.selected_imovel = None

if "idx" not in st.session_state:
    st.session_state.idx = 0

if "last_update" not in st.session_state:
    st.session_state.last_update = time.time()

st.set_page_config(page_title="Paulo Moreira | Consultoria & Gestão", layout="centered")

def get_base64(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return ""

def safe_float(value):
    try:
        return float(str(value).replace("%","").replace(",",".").replace("€","").replace(" ","").replace("\xa0","").strip())
    except:
        return 0

SHEET_ID = "1PoK3Gj6mdLVkniIzDgFNhwmOGgpznRAIC0CGzweASag"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=3600)
def load_data(url):
    try:
        data = pd.read_csv(url)
        data = data.fillna("")
        if "Score_PM5D" in data.columns:
            data = data[pd.to_numeric(data["Score_PM5D"], errors="coerce").fillna(0) >= 3]
        if "Status_Scraping" in data.columns:
            data = data[data["Status_Scraping"].str.upper().isin(["OK", "APROVADO", "PUBLICAR"])]
        if "Decisao" in data.columns:
            data = data[data["Decisao"].str.upper().isin(["APROVADO", "SIM", "OK"])]
        return data.reset_index(drop=True)
    except Exception:
        return pd.DataFrame()

df = load_data(URL)

fundo_marmore = get_base64("Background.svg")

st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/svg+xml;base64,{fundo_marmore}");
        background-size: cover;
        background-attachment: fixed;
    }}
    
    /* --- 1. BOTÕES PRINCIPAIS: BRANCO -> TRANSPARENTE NO HOVER --- */
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
        background-image: none !important;
        color: #1a1a1a !important;
        border-color: #bfa573 !important;
        transform: translateY(-1px) !important;
    }}

    /* --- 2. BOTÕES DENTRO DAS CAIXAS DE SERVIÇO (Dourado sobre Cinza Neutro) --- */
    .service-box .action-link {{
        display: inline-block; 
        padding: 8px 16px; 
        background-color: #eeeeee !important; /* Cinza Neutro */
        color: #bfa573 !important;           /* Texto Dourado */
        border: 1px solid #d0d0d0;
        text-decoration: none !important; 
        border-radius: 8px; 
        font-size: 11px; 
        font-weight: bold;
        margin-top: 10px; 
        text-transform: uppercase; 
        text-align: center;
        transition: 0.3s;
    }}

    .service-box .action-link:hover {{
        background-color: transparent !important;
        border-color: #bfa573 !important;
    }}

    /* Restantes estilos de proteção de layout */
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
    .cargo-text {{ color: #1a1a1a !important; font-weight: 700 !important; letter-spacing: 2px; text-transform: uppercase; font-size: 13px; }}
    .quote-style {{ font-style: italic; color: #bfa573; font-size: 15px; margin: 10px 0; border-left: 2px solid #bfa573; padding-left: 10px; }}
    .bio-text {{ font-size: 14px; color: #333; line-height: 1.5; }}
    .legal-footer-box {{
        font-size: 11px; color: #444; text-align: center; padding: 25px;
        background: rgba(253, 250, 245, 0.99); border-radius: 10px;
        border: 1px dashed #bfa573; margin-top: 30px; line-height: 1.8;
    }}
    </style>
""", unsafe_allow_html=True)

@st.fragment
def render_carousel_fragment(df_data):
    if not df_data.empty:
        if (time.time() - st.session_state.last_update) > 3:
            st.session_state.idx = (st.session_state.idx + 1) % len(df_data)
            st.session_state.last_update = time.time()
            st.rerun()
        
        row = df_data.iloc[st.session_state.idx]
        st.markdown(f"""
        <div class="preview-window">
            <img src="{row.get('Capa_Manual','')}" style="width:100%; height:120px; object-fit:cover; border-radius:8px; margin-bottom:5px;">
            <div style="font-size:12px;"><b>{row.get('Tipo')} | {row.get('Localidade')}</b></div>
        </div>
        """, unsafe_allow_html=True)

if os.path.exists("Paulo Moreira Consultoria & Gestão.png"):
    st.image("Paulo Moreira Consultoria & Gestão.png", use_container_width=True)

c1, c2, c3 = st.columns(3)
with c1: st.link_button("🎯 Avaliar Imóvel", "https://www.kwportugal.pt/pt/property-valuation")
with c2: st.link_button("🏦 Simular Crédito", "https://docs.google.com/forms/d/e/1FAIpQLSfiMOMKqZhnB14I5_DTrPLQrWYgiQdaw-O2HBfQBoLh4Qk5Ow/viewform")
with c3: st.link_button("📲 App Pessoal KW", "https://app.kw.com/KWNVLOD5AW4")

st.write("<br>", unsafe_allow_html=True)

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
        preco = safe_float(row.get("Preco_Listagem", 0))
        area = safe_float(row.get("Area_m2", 0))
        ref = row.get("Referencia", "N/A")
        
        st.markdown(f"""
            <div class="white-solid-box" style="margin-top:15px;">
                <h2 style="color:#1a1a1a; margin:0; font-weight:300;">{row.get('Tipo')} em {row.get('Localidade')}</h2>
                <small style="color:#888;">Referência Técnica: {ref}</small>
            </div>
            <div style="width:100%; height:280px; background-color:#ffffff; overflow:hidden; border-radius:12px; margin-bottom:20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); display:flex; align-items:center; justify-content:center;">
                <img src="{row.get('Capa_Manual','')}" style="max-width:100%; max-height:100%; object-fit:contain; border-radius:8px;">
            </div>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px; margin-bottom:20px;">
                <div class="white-solid-box" style="margin-bottom:0;">
                    <small style="color:#888;">PREÇO</small><br><b style="font-size:22px;">{preco:,.0f}€</b>
                </div>
                <div class="white-solid-box" style="margin-bottom:0;">
                    <small style="color:#888;">ÁREA ÚTIL</small><br><b style="font-size:22px;">{area} m²</b>
                </div>
            </div>
            <div style="background:#f0f0f0; padding:25px; border-radius:12px; border:2px dashed #bfa573; text-align:center;">
                <h4 style="margin:0; color:#1a1a1a;">📊 Relatório Financeiro</h4>
                <p style="font-size:13px; color:#666; font-weight:700; margin:10px 0;">
                    ROI Estimado, Plano de CAPEX e Projeção de Lucro Flip.
                </p>
                <div style="font-size:18px; color:#a6894a; font-weight:600; letter-spacing:1px;">
                    Exclusivo para Investidores
                </div>
            </div>
        """, unsafe_allow_html=True)
        url_whatsapp = f"https://wa.me/351912555122?text=Olá%20Paulo,%20gostaria%20de%20receber%20o%20Relatório%20Financeiro%20do%20imóvel%20Ref:%20{ref}"
        
        if st.button("🔓 Desbloquear Dados", key="btn_desbloquear"):
            js = f"window.open('{url_whatsapp}')"
            st.components.v1.html(f"<script>{js}</script>", height=0)
    st.markdown('</div>', unsafe_allow_html=True)

else:
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

        if not df.empty:
            render_carousel_fragment(df)
            st.write("")
            if st.button("📂 VER TODOS OS IMÓVEIS DISPONÍVEIS", use_container_width=True):
                st.session_state.page = "LOJA"
                st.session_state.idx = 0
                st.rerun()
        else:
            st.markdown('<div class="preview-window">Sincronizando Ativos...</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

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
