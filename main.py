import streamlit as st
import base64
import os
import pandas as pd
import time
import requests
import re
import hashlib

from utils import (
    calcular_score, 
    identificar_tipologia, 
    get_area_real, 
    get_area_qualidade,
    identificar_zona_e_ajuste,
    extrair_capex_do_titulo,      
    classificar_estado            
)

# ==========================================
# 1. CONFIGURAÇÕES E ESTADO DA SESSÃO
# ==========================================
if "page" not in st.session_state: st.session_state.page = "HOME"
if "selected_imovel" not in st.session_state: st.session_state.selected_imovel = None
if "idx" not in st.session_state: st.session_state.idx = 0

st.set_page_config(page_title="Paulo Moreira | Consultoria & Gestão", layout="centered")

# --- Funções de Suporte ---
def get_base64(bin_file):
    import os
    import base64
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return ""

def safe_float(value):
    if value is None or value == "":
        return 0.0
    try:
        val_str = str(value).replace("€","").replace("%","").replace(" ","").replace("\xa0","").strip()
        if "." in val_str and "," in val_str:
            val_str = val_str.replace(".", "").replace(",", ".")
        elif "," in val_str:
            val_str = val_str.replace(",", ".")
        return float(val_str)
    except:
        return 0.0
# ==========================================
# 2. CÉREBRO 2026 - CARREGAMENTO E FILTROS
# ==========================================
SHEET_ID = "1PoK3Gj6mdLVkniIzDgFNhwmOGgpznRAIC0CGzweASag"
URL_LEADS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=LEADS"
URL_CONFIG = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=CONFIG_MERCADO"

@st.cache_data(ttl=600)
def carregar_sistema_completo():
    try:
        df_leads = pd.read_csv(URL_LEADS).fillna("")
        df_conf = pd.read_csv(URL_CONFIG).fillna("")
        
        # A. Limpeza básica de preços
        df_leads["Preco_Listagem"] = df_leads["Preco_Listagem"].apply(safe_float)
        
        # B. Identificação de Tipologia (Manual vs Auto)
        df_leads["Tipologia"] = df_leads.apply(
            lambda row: str(row["Tipologia_Manual"]).strip() if str(row.get("Tipologia_Manual", "")).strip() != "" 
            else identificar_tipologia(row.get("Titulo", "")),
            axis=1
        )
        
        # C. Normalização de Área Inteligente e Legenda de Qualidade
        df_leads["Area_m2"] = df_leads.apply(get_area_real, axis=1)
        df_leads["Area_Qualidade"] = df_leads.apply(get_area_qualidade, axis=1)

        # D.1 CAPEX + ESTADO (NOVO - não quebra nada)
        df_leads["CAPEX_Titulo"] = df_leads["Titulo"].apply(extrair_capex_do_titulo)
        df_leads["Estado_Imovel"] = df_leads["CAPEX_Titulo"].apply(classificar_estado)
        
        # D. Cálculo do Score 5D (Agora com motor de custos e ajustes locais)
        df_leads["Score_Calculado"] = df_leads.apply(
            lambda row: calcular_score(row, df_conf), 
            axis=1
        )
        
        # E. Zona Dinâmica (Ouro do Python: identifica e extrai o ID da Zona)
        df_leads["Zona_Dinamica"] = df_leads["Localidade"].apply(
            lambda x: identificar_zona_e_ajuste(x)[0]
        )
        
        # Filtro de Activos para a Galeria Pública
        df_publico = df_leads[df_leads["Decisao"].str.upper().isin(["APROVADO", "SIM", "OK"])].copy()
        
        return df_leads, df_publico.sort_values(by="Score_Calculado", ascending=False).reset_index(drop=True)
    except Exception as e:
        st.error(f"Erro no Cérebro: {e}")
        return pd.DataFrame(), pd.DataFrame()

# Ativação
df_quarentena, df = carregar_sistema_completo()
# O sistema verifica se no URL escreveste /?pmm=2026
query_params = st.query_params

if query_params.get("ppkmor") == "7":
    with st.expander("🔬 Radar de Metodologia 5D (Tabela de Auditoria)", expanded=True):
        if not df_quarentena.empty:
            df_view = df_quarentena.copy()
            
            # 1. STATUS E CÁLCULO DE M2 REAL (Agora com Proteção)
            df_view["Status"] = df_view["Decisao"].apply(
                lambda x: "✅ LOJA" if str(x).upper() in ["APROVADO", "SIM", "OK"] else "⏳ QUARENTENA"
            )
            
            # Cálculo protegido para evitar erro de divisão por zero
            df_view["€/m2"] = df_view.apply(
                lambda x: (x["Preco_Listagem"] / x["Area_m2"]) if x["Area_m2"] > 0 else 0, 
                axis=1
            ).round(0)
            
            # 2. COLUNAS QUE ESTAVAM "ESCONDIDAS" (Ouro do Python)
            # Adicionamos "Zona_Dinamica" e "Area_Qualidade" para auditoria técnica
            colunas_foco = [
                "Status", "Score_Calculado", "Tipologia", "Localidade", "Zona_Dinamica",
                "Preco_Listagem", "Area_m2", "€/m2", "Area_Qualidade","Estado_Imovel", 
                "CAPEX_Titulo", "Referencia"
                ]
            
            # Adiciona colunas de simulação se elas existirem no teu processamento
            for col in ["Preco_Exit", "CAPEX_Estimado", "Investimento_Total"]:
                if col in df_view.columns:
                    colunas_foco.append(col)

            st.dataframe(
                df_view[colunas_foco].sort_values(by="Score_Calculado", ascending=False),
                column_config={
                    "Score_Calculado": st.column_config.NumberColumn("⭐ Score", format="%d/5"),
                    "Preco_Listagem": st.column_config.NumberColumn("Preço (€)", format="%d €"),
                    "Area_m2": st.column_config.NumberColumn("Área Final", format="%.0f m²"),
                    "Preco_Exit": st.column_config.NumberColumn("Venda Alvo", format="%d €"),
                    "CAPEX_Estimado": st.column_config.NumberColumn("Obra Est.", format="%d €"),
                    "Area_Qualidade": st.column_config.TextColumn("Fonte"),
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Seletor para abrires a ficha técnica de qualquer lead (mesmo as em quarentena)
            escolha = st.selectbox("Analise específica:", 
                                  options=df_view["Referencia"].unique(), 
                                  index=None, 
                                  placeholder="Escolha a Referência...")
            
            if escolha:
                # Busca no df_view para garantir que encontras qualquer uma
                lead_selecionada = df_view[df_view["Referencia"] == escolha].iloc[0]
                if st.button(f"🚀 Abrir Ficha de {escolha}"):
                    st.session_state.selected_imovel = lead_selecionada.to_dict()
                    st.session_state.page = "DETALHE"
                    st.rerun()
else:
    # Se o URL não tiver o código, o Python não processa nada disto. 
    # Para o cliente, esta parte do site nem sequer existe.
    pass
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

# --- TUDO DENTRO DE UM ÚNICO BLOCO PARA NÃO DAR ERRO ---
st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/svg+xml;base64,{fundo_marmore}");
        background-size: cover;
        background-attachment: fixed;
        z-index: 0;
    }}

    /* Camada de Blur Leve - Abertura */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        backdrop-filter: blur(2px);
        -webkit-backdrop-filter: blur(2px);
        z-index: -1;
    }}
    
    /* Botões e Links - A porta continua aberta aqui */
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

    /* Estrutura de Cards - Continua a correr... */
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
                    <b style="font-size:18px; color:#bfa573;">{f"{preco:,.0f}".replace(",", " ")}€</b>
                    <span style="font-size:13px; color:#333;">📐 {row.get('Area_m2')} m²</span>
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
        # --- LIGAÇÃO AO CÉREBRO (Processado no início do main) ---
        ref = row.get("Referencia", "N/A")
        preco_lista = safe_float(row.get("Preco_Listagem", 0))
        capex_base = safe_float(row.get("CAPEX_Titulo", 0))
        exit_base = safe_float(row.get("Preco_Exit", 0))
        invest_total = safe_float(row.get("Investimento_Total", 0))

        # --- RESTAURO DO TEU DESIGN ORIGINAL ---
        st.markdown(f"""
            <div class="white-solid-box" style="margin-top:15px; border-bottom: 2px solid #1a1a1a;">
                <h2 style="color:#1a1a1a; margin:0; font-weight:300; font-size:22px;">{row.get('Tipo')} em {row.get('Localidade')}</h2>
                <small style="color:#bfa573; font-weight:bold; letter-spacing:1px;">REFERÊNCIA: {ref}</small>
            </div>
            <div style="width:100%; height:300px; background-color:#ffffff; overflow:hidden; border-radius:12px; margin-bottom:10px; display:flex; align-items:center; justify-content:center; box-shadow: inset 0 0 10px rgba(0,0,0,0.05);">
                <img src="{row.get('Capa_Manual','')}" style="max-width:100%; max-height:100%; object-fit:contain;">
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <style>
                .titulo-simulador {
                    text-align: center; font-size: 16px; color: #1a1a1a; font-weight: bold;
                    letter-spacing: 1px; border-bottom: 1px solid #eee; padding-bottom: 5px;
                    margin-bottom: 10px; text-transform: uppercase;
                }
            </style>
            <div style="background-color: #ffffff; padding: 10px 25px; border-radius: 12px; border: 1px solid #bfa573; 
                        margin: 5px auto; max-width: 600px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                <p class="titulo-simulador">🛠️ Simulador de Investimento</p>
        """, unsafe_allow_html=True)
        
        col_sim1, col_sim2 = st.columns(2)
        with col_sim1:
            novo_capex = st.number_input("**Estimativa de Obra (€)**", value=float(capex_base), step=1000.0, format="%.2f")
        
        with col_sim2:
            valor_sugerido = float(exit_base) if exit_base > 0 else 0.0
            novo_exit = st.number_input("**Preço de Venda Alvo (€)**", value=valor_sugerido, step=1000.0, format="%.2f")
        
        st.markdown("</div>", unsafe_allow_html=True)

        # Alerta de Análise (Apenas se não houver Exit Price na Sheet)
        if exit_base == 0:
            st.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.6); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
                    border: 1px solid #bfa573; border-radius: 12px; padding: 15px; margin: 15px auto; max-width: 600px; 
                    text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
                    <span style="color: #1a1a1a; font-size: 13px; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase;">
                        🔍 Análise de Viabilidade em Curso
                    </span><br>
                    <div style="width: 30px; height: 1px; background: #bfa573; margin: 8px auto;"></div>
                    <span style="color: #555; font-size: 11px; font-family: 'Inter', sans-serif;">
                        Imóvel sob análise técnica. Os valores de projecção serão actualizados após validação de mercado e métricas 5D.
                    </span>
                </div>
            """, unsafe_allow_html=True)

        # --- LÓGICA DE CÁLCULO ---
        foi_simulado = (novo_capex != capex_base) or (novo_exit != valor_sugerido)
        if novo_exit == 0:
            lucro_estimado = 0.0
        else:
            # Lucro = Venda - (Investimento Total atualizado pela nova estimativa de obra)
            lucro_estimado = novo_exit - (invest_total - capex_base + novo_capex)
        
        # --- O TEU CARTÃO DE EFEITO VIDRO (RESTURADO) ---
        st.markdown(f"""
            <div style="max-width: 600px; margin: 10px auto; display: flex; justify-content: center;">
                <div style="text-align:center; padding: 25px; 
                            background-color: rgba(255, 255, 255, 0.4); 
                            -webkit-backdrop-filter: blur(10px); 
                            backdrop-filter: blur(10px); 
                            border-radius: 12px; 
                            border: 1px solid rgba(255, 255, 255, 0.2); 
                            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05), inset 0 0 20px rgba(255,255,255,0.1); 
                            width: 100%; position: relative; overflow: hidden;">
                    <span style="color:#1a1a1a; font-size:12px; text-transform: uppercase; letter-spacing: 1.5px; opacity: 0.8; font-weight: bold;">
                        Projeção de Lucro Flip
                    </span><br>
                    <span style="color:#bfa573; font-size:42px; font-weight:bold; letter-spacing: -1px; text-shadow: 0px 0px 5px rgba(255,255,255,0.8);">
                        {f"{lucro_estimado:,.0f}".replace(",", " ")}€
                    </span>
                    <div style="width:40px; height:1px; background: rgba(0, 0, 0, 0.4); margin:15px auto;"></div>
                    <p style="color:#000; font-size:10px; margin:0; font-family: 'Courier New', Courier, monospace; font-weight: bold; opacity: 0.9;">
                        Cálculo baseado na Metodologia 5D P.M.M.
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        lead_contacto = st.text_input("Para mais detalhes, preencha com:", placeholder="Seu Nome ou Email...")
        # [Daqui para baixo continua o teu st.button de desbloquear relatório...]
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

# --- CSS REFINADO: EFEITO VIDRO ANTRACITE (OPEN SPECTRUM) ---
st.markdown("""
    <style>
        .action-link {
            display: inline-block !important;
            margin-top: 15px !important;
            padding: 10px 25px !important;
            /* Fundo Antracite Transparente (Efeito Vidro) */
            background: rgba(43, 43, 43, 0.85) !important;
            backdrop-filter: blur(5px) !important;
            -webkit-backdrop-filter: blur(5px) !important;
            
            color: #bfa573 !important; /* Texto Dourado */
            text-decoration: none !important;
            border-radius: 4px !important;
            font-size: 10px !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 1.5px !important;
            transition: all 0.4s ease !important;
            border: 1px solid rgba(191, 165, 115, 0.6) !important; /* Borda dourada suave */
            text-align: center !important;
        }

        .action-link:hover {
            /* No hover, o vidro torna-se mais sólido e brilhante */
            background: rgba(191, 165, 115, 0.9) !important;
            color: #1a1a1a !important;
            border: 1px solid #bfa573 !important;
            box-shadow: 0 5px 15px rgba(191, 165, 115, 0.3) !important;
            transform: translateY(-2px) !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- BLOCO DE SERVIÇOS (IGUAL AO TEU, MAS AGORA COM O CSS ATIVO) ---
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
