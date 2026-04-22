"""
╔══════════════════════════════════════════════════════════════════╗
║   HUB PANDORA — APP.PY UNIFICADO                                 ║
║   Paulo Moreira | KW Área Feira | AMI 21331                      ║
║   Fase 1: Montra & Identidade                                    ║
║   Fase 2: Metodologia PM 5D · Análise de Activos KW              ║
╚══════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import base64
import os
import requests
import re
import urllib.parse
from bs4 import BeautifulSoup

# ════════════════════════════════════════════════════════════════
# 0. CONFIGURAÇÃO GLOBAL DA PÁGINA
# ════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Paulo Moreira | KW Área Feira",
    layout="centered",
    page_icon="🏠",
    initial_sidebar_state="collapsed",
)

# ════════════════════════════════════════════════════════════════
# 1. CONSTANTES & SHEET
# ════════════════════════════════════════════════════════════════
SHEET_ID  = "1PoK3Gj6mdLVkniIzDgFNhwmOGgpznRAIC0CGzweASag"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# Colunas do Super_Sheet_PM5D
C_REF        = "Referencia"
C_LOCAL      = "Localidade"
C_TIPO       = "Tipo"
C_PRECO      = "Preco_Listagem"
C_CAPEX      = "CAPEX_Estimado"
C_IMT        = "IMT_2024"
C_SELO       = "Selo"
C_INV_TOT    = "Investimento_Total"
C_PRECO_EXIT = "Preco_Exit"
C_RENDA      = "Renda_Mensal"
C_SCORE      = "Score_PM5D"
C_LUCRO      = "Lucro_Flip"
C_ROI        = "ROI_Percent"
C_YIELD      = "Yield_Euros_Ano"
C_LINK       = "Link_Fonte"
C_CAPA       = "Capa_Manual"
C_STATUS     = "Status_Scraping"

# ════════════════════════════════════════════════════════════════
# 2. UTILITÁRIOS
# ════════════════════════════════════════════════════════════════
def get_base64(bin_file: str) -> str:
    if os.path.exists(bin_file):
        with open(bin_file, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

def fmt_eur(val) -> str:
    try:
        v = float(str(val).replace("€","").replace(" ","").replace(".","").replace(",",".").strip())
        return f"{v:,.0f} €".replace(",",".")
    except (ValueError, TypeError):
        return "—"

def fmt_pct(val) -> str:
    try:
        v = float(str(val).replace("%","").replace(",",".").strip())
        return f"{v:.2f}%"
    except (ValueError, TypeError):
        return "—"

def to_float(val) -> float:
    try:
        return float(str(val).replace("€","").replace("%","").replace(" ","").replace(".","").replace(",",".").strip())
    except (ValueError, TypeError):
        return 0.0

def score_classe(s: float) -> str:
    if s >= 4: return "s-alto"
    if s >= 2.5: return "s-medio"
    return "s-baixo"

def veredito(s: float) -> str:
    if s >= 4: return "✅ ACTIVO ESTRATÉGICO — Elegível para Dossier Alpha"
    if s >= 2.5: return "⚠️ CONFORMIDADE PARCIAL — Requer Saneamento Técnico"
    return "🚫 INVIABILIDADE TÉCNICA — Fora dos Critérios PM 5D"

# ════════════════════════════════════════════════════════════════
# 3. CARREGAR DADOS DO SHEET (cache 5 min)
# ════════════════════════════════════════════════════════════════
@st.cache_data(ttl=300, show_spinner=False)
def carregar_sheet() -> pd.DataFrame:
    try:
        df = pd.read_csv(SHEET_URL)
        return df.fillna("")
    except Exception:
        return pd.DataFrame()

# ════════════════════════════════════════════════════════════════
# 4. SCRAPING KW PORTUGAL (cache 1h)
# ════════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600, show_spinner=False)
def scrape_kw(url: str) -> dict:
    try:
        r = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        titulo = ""
        t = soup.find("h1")
        if t: titulo = t.get_text(strip=True)
        preco_str = ""
        for tag in soup.find_all(True):
            txt = tag.get_text(strip=True)
            if "€" in txt and 4 < len(txt) < 30:
                preco_str = txt
                break
        area_str = ""
        m = re.search(r"(\d[\d\s\.]*)\s*m²", r.text)
        if m: area_str = m.group(0)
        img = ""
        og = soup.find("meta", property="og:image")
        if og: img = og.get("content", "")
        return {"ok": True, "titulo": titulo, "preco": preco_str, "area": area_str, "img": img}
    except Exception as e:
        return {"ok": False, "erro": str(e)}

# ════════════════════════════════════════════════════════════════
# 5. CSS GLOBAL — DNA visual Paulo Moreira
# ════════════════════════════════════════════════════════════════
fundo_marmore = get_base64("Background.svg")

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;600;700&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── FUNDO ── */
.stApp {{
    background-image: url("data:image/svg+xml;base64,{fundo_marmore}");
    background-size: cover;
    background-attachment: fixed;
    font-family: 'DM Sans', sans-serif;
}}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {{
    gap: 8px;
    background: rgba(253,250,245,0.95);
    border-radius: 12px;
    padding: 6px;
    border: 1px solid #e8dfc8;
    margin-bottom: 20px;
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent;
    border-radius: 8px;
    color: #555;
    font-weight: 600;
    font-size: 14px;
    padding: 8px 20px;
    font-family: 'DM Sans', sans-serif;
}}
.stTabs [aria-selected="true"] {{
    background: #1a1a1a !important;
    color: #bfa573 !important;
}}

/* ── CARDS FASE 1 ── */
.main-protection-card {{
    background-color: rgba(253, 250, 245, 0.99);
    padding: 25px 35px 20px 35px;
    border-radius: 15px;
    border-left: 8px solid #bfa573;
    box-shadow: 0 15px 35px rgba(0,0,0,0.12);
    margin-bottom: 16px;
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
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: inset 0 0 20px rgba(191,165,115,0.08);
}}
.service-box {{
    background-color: white;
    padding: 18px;
    border-radius: 10px;
    border-bottom: 3px solid #bfa573;
    margin-bottom: 15px;
    min-height: 155px;
    transition: transform 0.3s ease;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}}
.service-box:hover {{ transform: translateY(-5px); box-shadow: 0 8px 20px rgba(0,0,0,0.1); }}
.service-title {{ color: #1a1a1a; font-weight: 800; font-size: 15px; margin-bottom: 5px; display: block; }}
.service-desc {{ color: #555; font-size: 12.5px; line-height: 1.4; }}

.profile-frame {{
    width: 175px; height: 175px;
    border-radius: 50%;
    border: 4px solid #bfa573;
    overflow: hidden;
    margin: 0 auto 15px auto;
    background: white;
    box-shadow: 0 8px 20px rgba(191,165,115,0.3);
}}
.profile-frame img {{ width: 100%; height: 100%; object-fit: cover; }}

.cargo-text {{
    color: #1a1a1a !important;
    font-weight: 700 !important;
    letter-spacing: 2px;
    text-transform: uppercase;
    font-size: 12px;
    font-family: 'DM Sans', sans-serif;
}}
.quote-style {{
    font-style: italic;
    color: #bfa573;
    font-size: 15px;
    margin: 10px 0;
    border-left: 3px solid #bfa573;
    padding-left: 12px;
    font-family: 'Cormorant Garamond', serif;
}}
.bio-text {{ font-size: 14px; color: #333; line-height: 1.6; }}
.hero-name {{
    font-family: 'Cormorant Garamond', serif;
    font-size: 34px;
    font-weight: 300;
    color: #1a1a1a;
    margin: 5px 0;
    letter-spacing: 1px;
}}

/* ── BOTÕES STREAMLIT ── */
div.stButton > button {{
    width: 100% !important;
    height: 50px !important;
    background-color: white !important;
    color: #1a1a1a !important;
    border: 1px solid #1a1a1a !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    border-radius: 6px !important;
    margin-top: 5px;
    font-family: 'DM Sans', sans-serif !important;
    transition: all 0.2s ease !important;
}}
div.stButton > button:hover {{
    background-color: #1a1a1a !important;
    color: white !important;
}}
.action-link {{
    display: inline-block;
    padding: 8px 16px;
    background: #1a1a1a;
    color: white !important;
    text-decoration: none !important;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 700;
    margin-top: 10px;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-family: 'DM Sans', sans-serif;
}}
.action-link:hover {{ background: #bfa573; }}

/* ── MONTRA — JANELA DINÂMICA ── */
.montra-card {{
    background: white;
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #e8dfc8;
    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
    margin-bottom: 8px;
}}
.montra-card img {{ width: 100%; border-radius: 10px 10px 0 0; }}
.montra-info {{
    padding: 14px 16px;
    border-top: 3px solid #bfa573;
}}
.montra-tipo {{ font-size: 10px; color: #bfa573; letter-spacing: 2px; text-transform: uppercase; }}
.montra-local {{
    font-family: 'Cormorant Garamond', serif;
    font-size: 18px;
    font-weight: 700;
    color: #1a1a1a;
    margin: 2px 0;
}}
.montra-roi {{ font-size: 13px; font-weight: 700; color: #1a7a4a; }}

/* ── FASE 2 ── */
.f2-header {{
    background: linear-gradient(135deg, #1a1a1a 0%, #252525 100%);
    padding: 22px 30px;
    border-radius: 14px;
    border-left: 6px solid #bfa573;
    margin-bottom: 22px;
}}
.f2-header h2 {{
    color: #bfa573;
    margin: 0 0 4px 0;
    font-family: 'Cormorant Garamond', serif;
    font-size: 20px;
    letter-spacing: 2px;
    text-transform: uppercase;
}}
.f2-header p {{ color: #999; margin: 0; font-size: 12px; }}

.stat-card {{
    background: white;
    border-radius: 10px;
    padding: 14px 12px;
    text-align: center;
    border-bottom: 3px solid #bfa573;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06);
    margin-bottom: 8px;
}}
.stat-card .num {{
    font-family: 'Cormorant Garamond', serif;
    font-size: 26px;
    font-weight: 700;
    color: #1a1a1a;
    line-height: 1;
}}
.stat-card .lbl {{
    font-size: 10px;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin-top: 5px;
}}

.dossier-card {{
    background: #ffffff;
    border-radius: 14px;
    border-left: 5px solid #bfa573;
    padding: 18px 20px 14px 20px;
    margin-bottom: 16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.07);
}}
.dossier-ref {{
    font-size: 10px;
    color: #bfa573;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 2px;
}}
.dossier-titulo {{
    font-family: 'Cormorant Garamond', serif;
    font-size: 20px;
    font-weight: 700;
    color: #1a1a1a;
    margin: 0 0 3px 0;
}}
.dossier-preco {{
    font-family: 'Cormorant Garamond', serif;
    font-size: 21px;
    font-weight: 600;
    color: #bfa573;
}}

.score-badge {{
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 12px;
    margin-bottom: 10px;
}}
.s-alto   {{ background: #1a1a1a; color: #bfa573; }}
.s-medio  {{ background: #fdf6e3; color: #8b6914; border: 1px solid #d4a843; }}
.s-baixo  {{ background: #fdf0f0; color: #c0392b; border: 1px solid #e74c3c; }}

.fin-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin: 12px 0;
}}
.fin-item {{
    background: #fdfaf5;
    border-radius: 8px;
    padding: 10px 12px;
    border-bottom: 2px solid #e8dfc8;
}}
.fin-lbl {{ font-size: 10px; color: #999; text-transform: uppercase; letter-spacing: 1px; }}
.fin-val {{ font-size: 15px; font-weight: 700; color: #1a1a1a; margin-top: 2px; }}
.fin-val.positivo {{ color: #1a7a4a; }}
.fin-val.neutro   {{ color: #bfa573; }}

.bar-out {{ background: #f0ece4; border-radius: 4px; height: 7px; margin-top: 4px; }}
.bar-in  {{ height: 7px; border-radius: 4px; background: linear-gradient(90deg, #bfa573, #d4b896); }}

.relatorio {{
    background: #fdfaf5;
    border: 1px dashed #bfa573;
    border-radius: 10px;
    padding: 18px 20px;
    font-size: 13px;
    color: #333;
    line-height: 1.75;
    margin-top: 12px;
}}
.relatorio .rel-titulo {{
    font-family: 'Cormorant Garamond', serif;
    font-size: 17px;
    font-weight: 700;
    color: #1a1a1a;
    margin-bottom: 10px;
    border-bottom: 1px solid #e8dfc8;
    padding-bottom: 6px;
}}
.relatorio .veredito {{ font-weight: 700; font-size: 14px; margin-bottom: 10px; }}
.relatorio .secao {{ margin: 8px 0; }}

/* ── RODAPÉ LEGAL ── */
.legal-footer-box {{
    font-size: 11px;
    color: #444;
    text-align: center;
    padding: 22px;
    background: rgba(253, 250, 245, 0.99);
    border-radius: 10px;
    border: 1px dashed #bfa573;
    margin-top: 28px;
    line-height: 1.9;
    font-family: 'DM Sans', sans-serif;
}}
.footer-fase2 {{
    font-size: 11px;
    color: #aaa;
    text-align: center;
    padding: 16px 0;
    border-top: 1px solid #f0ece4;
    margin-top: 16px;
}}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# 6. GERADOR DE RELATÓRIO PM 5D (PT-PT · 1ª pessoa · DNA Paulo)
# ════════════════════════════════════════════════════════════════
def gerar_relatorio(row: pd.Series) -> str:
    ref     = row.get(C_REF, "—")
    tipo    = row.get(C_TIPO, "Activo")
    local   = row.get(C_LOCAL, "—")
    score   = to_float(row.get(C_SCORE, 0))
    lucro_v = to_float(row.get(C_LUCRO, 0))
    renda_v = to_float(row.get(C_RENDA, 0))
    roi_v   = to_float(row.get(C_ROI, 0))

    if renda_v > 0 and roi_v < 15:
        estrategia = "Yield / Arrendamento"
        desc_est = (
            f"Renda mensal potencial de <b>{fmt_eur(renda_v)}</b>, "
            f"com yield anual de <b>{fmt_eur(row.get(C_YIELD, 0))}</b>. "
            "Estratégia recomendada: retenção e arrendamento de médio/longo prazo."
        )
    elif lucro_v > 0:
        estrategia = "Flip / Valorização"
        desc_est = (
            f"Lucro potencial em flip de <b>{fmt_eur(lucro_v)}</b>, "
            f"com preço de saída estimado em <b>{fmt_eur(row.get(C_PRECO_EXIT, 0))}</b>. "
            "Estratégia recomendada: reabilitação e revenda."
        )
    else:
        estrategia = "Sob Avaliação"
        desc_est = "Dados financeiros incompletos. Aguarda confirmação dos valores de saída antes de avançar."

    if score >= 4:
        risco = "Baixo — Activo validado em todas as dimensões técnicas."
    elif score >= 2.5:
        risco = "Médio — Existem dimensões que requerem saneamento antes da comercialização."
    else:
        risco = "Alto — Activo fora dos critérios PM 5D. Recomendo suspender o avanço comercial."

    return f"""<div class="rel-titulo">
    Dossier De Conformidade Técnica PM 5D<br>
    <span style="font-size:13px;font-weight:400;color:#888;">{ref} · {tipo} · {local}</span>
</div>
<div class="veredito">{veredito(score)}</div>
<div class="secao"><b>Score PM 5D:</b> {score}/5</div>
<div class="secao"><b>Estrutura Financeira:</b><br>
• Preço de Listagem: {fmt_eur(row.get(C_PRECO, 0))}<br>
• CAPEX Estimado: {fmt_eur(row.get(C_CAPEX, 0))}<br>
• IMT 2024: {fmt_eur(row.get(C_IMT, 0))}<br>
• Selo: {fmt_eur(row.get(C_SELO, 0))}<br>
• Investimento Total: {fmt_eur(row.get(C_INV_TOT, 0))}
</div>
<div class="secao"><b>Estratégia Dominante:</b> {estrategia}<br>{desc_est}</div>
<div class="secao"><b>ROI Estimado:</b> {fmt_pct(row.get(C_ROI, 0))}</div>
<div class="secao"><b>Perfil de Risco:</b> {risco}</div>
<div style="margin-top:14px;font-size:11px;color:#bfa573;font-style:italic;">
Análise PM 5D · Hub Pandora · KW Área Feira · AMI 21331<br>
<i>«O papel aceita tudo, mas o terreno não engana.»</i>
</div>"""

# ════════════════════════════════════════════════════════════════
# 7. FASE 1 — MONTRA & IDENTIDADE
# ════════════════════════════════════════════════════════════════
def render_fase1(df: pd.DataFrame):

    # ── Logo topo ──
    if os.path.exists("Paulo Moreira Consultoria & Gestão.png"):
        st.image("Paulo Moreira Consultoria & Gestão.png", use_container_width=True)

    # ── 3 CTAs rápidos ──
    c1, c2, c3 = st.columns(3)
    with c1: st.link_button("🎯 Avaliar Imóvel",  "https://www.kwportugal.pt/pt/property-valuation")
    with c2: st.link_button("🏦 Simular Crédito", "https://docs.google.com/forms/d/e/1FAIpQLSfiMOMKqZhnB14I5_DTrPLQrWYgiQdaw-O2HBfQBoLh4Qk5Ow/viewform")
    with c3: st.link_button("📲 App KW",          "https://app.kw.com/KWNVLOD5AW4")

    st.write("<br>", unsafe_allow_html=True)

    # ── Card Perfil + Janela Dinâmica ──
    st.markdown('<div class="main-protection-card">', unsafe_allow_html=True)
    col_l, col_r = st.columns([1, 1.8])

    with col_l:
        if os.path.exists("paulo_moreira.png"):
            img_b64 = get_base64("paulo_moreira.png")
            st.markdown(
                f'<div class="profile-frame"><img src="data:image/png;base64,{img_b64}"></div>',
                unsafe_allow_html=True,
            )
        st.link_button("📸 Instagram", "https://www.instagram.com/paulomgmoreira/")
        st.link_button("🔵 Facebook",  "https://www.facebook.com/PMMConsultoriaEGestao/")

    with col_r:
        st.markdown("""<div class="white-solid-box">
            <div class="cargo-text">Consultor Imobiliário · KW Área Feira</div>
            <div class="hero-name">Paulo Moreira</div>
            <div class="quote-style">«O sucesso de uma transacção imobiliária depende de estratégia, não de sorte.»</div>
            <div class="bio-text">Especialista em activos residenciais e industriais.
            Através da <b>Metodologia PM 5D</b>, garanto um acompanhamento técnico,
            jurídico e comercial de excelência.</div>
        </div>""", unsafe_allow_html=True)

        # ── Janela Dinâmica de Activos (rotação do Sheet) ──
        if not df.empty and C_SCORE in df.columns:
            df_montra = df[df[C_SCORE].apply(to_float) >= 3].copy()
        else:
            df_montra = pd.DataFrame()

        if "idx_montra" not in st.session_state:
            st.session_state.idx_montra = 0

        if not df_montra.empty:
            row = df_montra.iloc[st.session_state.idx_montra % len(df_montra)]
            capa  = row.get(C_CAPA, "")
            tipo  = row.get(C_TIPO, "")
            local = row.get(C_LOCAL, "")
            roi   = to_float(row.get(C_ROI, 0))
            score = to_float(row.get(C_SCORE, 0))
            destaque = f"ROI {roi:.1f}%" if roi > 0 else f"Score PM 5D: {score}/5"

            if capa and str(capa).startswith("http"):
                st.markdown(f"""<div class="montra-card">
                    <img src="{capa}" style="width:100%;max-height:200px;object-fit:cover;border-radius:10px 10px 0 0;">
                    <div class="montra-info">
                        <div class="montra-tipo">{tipo}</div>
                        <div class="montra-local">{local}</div>
                        <div class="montra-roi">{destaque}</div>
                    </div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""<div class="preview-window">
                    <span style="font-size:36px;">🏠</span>
                    <b style="font-size:16px;">{tipo} · {local}</b>
                    <span style="color:#bfa573;font-size:14px;">{destaque}</span>
                </div>""", unsafe_allow_html=True)

            if st.button("🔄 Ver próximo activo"):
                st.session_state.idx_montra += 1
                st.rerun()
        else:
            st.markdown("""<div class="preview-window">
                <span style="font-size:40px;">🖼️</span>
                <b style="font-size:16px;">Visualização Estratégica do Imóvel</b>
                <span style="font-size:11px;color:#999;">Exemplo de Análise PM 5D</span>
            </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # fecha main-protection-card

    # ── Serviços ──
    st.markdown('<div class="main-protection-card" style="border-left:none;border-top:6px solid #1a1a1a;padding-top:20px;">', unsafe_allow_html=True)
    m1, m2 = st.columns(2)
    with m1:
        st.markdown("""<div class="service-box">
            <span class="service-title">📈 Estudo De Mercado</span>
            <span class="service-desc">Análise profunda baseada em dados reais e comparativos para definir o valor certo de venda.</span><br>
            <a href="https://www.kwportugal.pt/pt/property-valuation" class="action-link">Avaliar Imóvel</a>
        </div>""", unsafe_allow_html=True)
        st.markdown("""<div class="service-box">
            <span class="service-title">⚖️ Apoio Jurídico</span>
            <span class="service-desc">Segurança total na documentação, elaboração de CPCV e acompanhamento rigoroso até à escritura.</span>
        </div>""", unsafe_allow_html=True)
    with m2:
        st.markdown("""<div class="service-box">
            <span class="service-title">📣 Plano De Marketing</span>
            <span class="service-desc">Exposição premium em mais de 100 portais nacionais e internacionais com fotografia profissional.</span>
        </div>""", unsafe_allow_html=True)
        st.markdown("""<div class="service-box">
            <span class="service-title">🏦 Gestão De Crédito</span>
            <span class="service-desc">Intermediação de crédito certificada para encontrar as melhores condições de financiamento.</span><br>
            <a href="https://docs.google.com/forms/d/e/1FAIpQLSfiMOMKqZhnB14I5_DTrPLQrWYgiQdaw-O2HBfQBoLh4Qk5Ow/viewform" class="action-link">Simular Crédito</a>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Contactos ──
    st.write("<br>", unsafe_allow_html=True)
    ba, bb, bc = st.columns(3)
    with ba: st.link_button("⭐ Google Reviews", "https://share.google/n4FLZO1p2tYTl2vsG")
    with bb: st.link_button("📞 Ligar Agora",    "tel:+351911995695")
    with bc: st.link_button("🟢 Whatsapp",       "https://wa.me/351911995695")

    st.write("<br>", unsafe_allow_html=True)
    f1, f2, f3 = st.columns([1, 1, 1])
    with f1:
        if os.path.exists("P.M.M..png"):      st.image("P.M.M..png",       width=100)
    with f2:
        if os.path.exists("REAL ESTATE.svg"): st.image("REAL ESTATE.svg",  width=110)
    with f3:
        if os.path.exists("area_feira.png"):  st.image("area_feira.png",   width=110)

    st.markdown("""<div class="legal-footer-box">
        <b>Resumo Plural, Lda.</b> — Licença AMI 21331 — Pessoa Colectiva 517 033 224<br>
        Rua Estrada Nacional, nº 1190, 1200 – Zona Ind. do Roligo, 4520-115 Espargo<br>
        Tel.: 256 313 054 | kwareafeira@kwportugal.pt | www.kwportugal.pt<br>
        <b>Cada Market Center é de gestão independente</b>
    </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# 8. FASE 2 — ANÁLISE PM 5D · ANGARIAÇÕES KW
# ════════════════════════════════════════════════════════════════
def render_fase2(df: pd.DataFrame):

    st.markdown("""
    <div class="f2-header">
        <h2>⚙️ Fase 2 — Metodologia PM 5D · Angariações KW</h2>
        <p>Super_Sheet_PM5D · Validação técnica e financeira de activos · Hub Pandora</p>
    </div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.error("❌ Não foi possível carregar o Super_Sheet_PM5D. Verifica se está partilhado como público (apenas leitura).")
        return

    if C_LINK not in df.columns:
        st.warning(f"⚠️ Coluna `{C_LINK}` não encontrada. Colunas detectadas: {list(df.columns)}")
        return

    # Filtrar activos com link válido
    df_kw = df[df[C_LINK].str.startswith("http", na=False)].copy()

    if df_kw.empty:
        st.info("📋 Ainda não existem activos com link KW no Super_Sheet_PM5D.")
        return

    # Converter colunas numéricas
    num_cols = [C_PRECO, C_CAPEX, C_IMT, C_SELO, C_INV_TOT,
                C_PRECO_EXIT, C_RENDA, C_SCORE, C_LUCRO, C_ROI, C_YIELD]
    for col in num_cols:
        df_kw[f"_n_{col}"] = df_kw[col].apply(to_float) if col in df_kw.columns else 0.0

    sc = f"_n_{C_SCORE}"

    # ── Estatísticas de topo ──
    total    = len(df_kw)
    media_sc = round(df_kw[sc].mean(), 1)
    alpha_n  = int((df_kw[sc] >= 4).sum())
    inv_tot  = df_kw[f"_n_{C_INV_TOT}"].sum()

    c1, c2, c3, c4 = st.columns(4)
    for col_st, num, lbl in [
        (c1, total, "Activos em Análise"),
        (c2, f"{media_sc}/5", "Score Médio PM 5D"),
        (c3, alpha_n, "Dossiers Alpha ≥4"),
        (c4, fmt_eur(inv_tot), "Investimento Total"),
    ]:
        with col_st:
            st.markdown(f'<div class="stat-card"><div class="num">{num}</div><div class="lbl">{lbl}</div></div>', unsafe_allow_html=True)

    st.write("")

    # ── Filtros ──
    st.markdown('<div style="background:#f8f5ef;border:1px solid #e8dfc8;border-radius:10px;padding:14px 18px;margin-bottom:20px;">', unsafe_allow_html=True)
    f1, f2, f3 = st.columns([2, 2, 2])
    with f1:
        score_min = st.slider("Score PM 5D mínimo", 0.0, 5.0, 0.0, 0.5)
    with f2:
        tipos = ["Todos"] + (sorted(df_kw[C_TIPO].dropna().unique().tolist()) if C_TIPO in df_kw.columns else [])
        filtro_tipo = st.selectbox("Tipo de Activo", tipos)
    with f3:
        ordem = st.selectbox("Ordenar por", [
            "Score PM 5D (↓)", "Preço Listagem (↑)", "ROI (↓)", "Lucro Flip (↓)"
        ])
    st.markdown('</div>', unsafe_allow_html=True)

    # Aplicar filtros
    df_f = df_kw[df_kw[sc] >= score_min].copy()
    if filtro_tipo != "Todos" and C_TIPO in df_f.columns:
        df_f = df_f[df_f[C_TIPO] == filtro_tipo]

    if ordem == "Score PM 5D (↓)":
        df_f = df_f.sort_values(sc, ascending=False)
    elif ordem == "Preço Listagem (↑)":
        df_f = df_f.sort_values(f"_n_{C_PRECO}", ascending=True)
    elif ordem == "ROI (↓)":
        df_f = df_f.sort_values(f"_n_{C_ROI}", ascending=False)
    elif ordem == "Lucro Flip (↓)":
        df_f = df_f.sort_values(f"_n_{C_LUCRO}", ascending=False)

    st.markdown(f"**{len(df_f)} activo(s)** correspondem aos critérios seleccionados.")
    st.divider()

    # ── Cards por activo ──
    for i, (_, row) in enumerate(df_f.iterrows()):
        score  = to_float(row.get(C_SCORE, 0))
        ref    = row.get(C_REF, f"KW-{i+1:04d}")
        tipo   = row.get(C_TIPO, "Activo")
        local  = row.get(C_LOCAL, "—")
        link   = row.get(C_LINK, "")
        capa   = row.get(C_CAPA, "") if C_CAPA in row.index else ""
        status = row.get(C_STATUS, "") if C_STATUS in row.index else ""
        pct    = int(score / 5 * 100)

        st.markdown('<div class="dossier-card">', unsafe_allow_html=True)
        col_img, col_dados = st.columns([1, 2.2])

        with col_img:
            if capa and str(capa).startswith("http"):
                st.image(capa, use_container_width=True)
            else:
                st.markdown("""<div style="background:#f5f0e8;border-radius:10px;height:160px;
                display:flex;align-items:center;justify-content:center;
                color:#bfa573;font-size:36px;">🏠</div>""", unsafe_allow_html=True)
            if status:
                st.markdown(f'<div style="font-size:10px;color:#999;text-align:center;margin-top:4px;">{status}</div>', unsafe_allow_html=True)

        with col_dados:
            st.markdown(f"""
            <div class="dossier-ref">{ref}</div>
            <div class="dossier-titulo">{tipo} · {local}</div>
            <div class="dossier-preco">{fmt_eur(row.get(C_PRECO, 0))}</div><br>
            <span class="score-badge {score_classe(score)}">PM 5D: {score}/5</span>
            <div style="font-size:11px;color:#666;margin-bottom:4px;">Score Global</div>
            <div class="bar-out"><div class="bar-in" style="width:{pct}%"></div></div>
            <div class="fin-grid">
                <div class="fin-item"><div class="fin-lbl">Investimento Total</div>
                    <div class="fin-val neutro">{fmt_eur(row.get(C_INV_TOT, 0))}</div></div>
                <div class="fin-item"><div class="fin-lbl">Lucro Flip</div>
                    <div class="fin-val positivo">{fmt_eur(row.get(C_LUCRO, 0))}</div></div>
                <div class="fin-item"><div class="fin-lbl">ROI</div>
                    <div class="fin-val positivo">{fmt_pct(row.get(C_ROI, 0))}</div></div>
                <div class="fin-item"><div class="fin-lbl">Renda Mensal</div>
                    <div class="fin-val">{fmt_eur(row.get(C_RENDA, 0))}</div></div>
                <div class="fin-item"><div class="fin-lbl">Yield / Ano</div>
                    <div class="fin-val neutro">{fmt_eur(row.get(C_YIELD, 0))}</div></div>
                <div class="fin-item"><div class="fin-lbl">Preço Exit</div>
                    <div class="fin-val">{fmt_eur(row.get(C_PRECO_EXIT, 0))}</div></div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # ── Relatório + Deal Pack ──
        with st.expander(f"📋 Relatório Técnico PM 5D — {ref} · {tipo} · {local}"):
            st.markdown(f'<div class="relatorio">{gerar_relatorio(row)}</div>', unsafe_allow_html=True)

            b1, b2, b3 = st.columns([1, 1, 1])
            with b1:
                if link:
                    st.markdown(f"""<a href="{link}" target="_blank" style="
                        display:inline-block;margin-top:12px;padding:9px 18px;
                        background:#1a1a1a;color:white;text-decoration:none;
                        border-radius:4px;font-size:11px;font-weight:700;
                        letter-spacing:1.5px;text-transform:uppercase;">
                        🔗 Abrir Ficha KW Portugal
                    </a>""", unsafe_allow_html=True)
            with b2:
                msg = f"Olá Paulo! Quero o Deal Pack da Ref {ref}. O meu email é: "
                st.markdown(f"""<a href="https://wa.me/351911995695?text={urllib.parse.quote(msg)}" target="_blank" style="
                    display:inline-block;margin-top:12px;padding:9px 18px;
                    background:#25D366;color:white;text-decoration:none;
                    border-radius:4px;font-size:11px;font-weight:700;
                    letter-spacing:1.5px;text-transform:uppercase;">
                    📄 Pedir Deal Pack
                </a>""", unsafe_allow_html=True)
            with b3:
                if link and st.button("🔍 Validar online KW", key=f"scr_{i}"):
                    with st.spinner("A consultar KW Portugal..."):
                        d = scrape_kw(link)
                    if d["ok"]:
                        if d["titulo"]: st.success(d["titulo"])
                        if d["preco"]:  st.write(f"💶 Preço online: `{d['preco']}`")
                        if d["area"]:   st.write(f"📐 Área: `{d['area']}`")
                        if d["img"]:    st.image(d["img"], width=260)
                    else:
                        st.warning(f"Não foi possível validar: {d.get('erro', '—')}")

        st.write("")

    st.markdown("""
    <div class="footer-fase2">
        Metodologia PM 5D · Hub Pandora · KW Área Feira · AMI 21331<br>
        <i>«Rigor técnico sobre especulação — O papel aceita tudo, mas o terreno não engana.»</i>
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# 9. PONTO DE ENTRADA — TABS DE NAVEGAÇÃO
# ════════════════════════════════════════════════════════════════
def main():
    # Carregar dados uma única vez — partilhado entre as duas fases
    with st.spinner("A sincronizar com o Super_Sheet_PM5D..."):
        df = carregar_sheet()

    tab1, tab2 = st.tabs(["🏠 Montra & Identidade", "⚙️ Análise PM 5D · Angariações KW"])

    with tab1:
        render_fase1(df)

    with tab2:
        render_fase2(df)

if __name__ == "__main__":
    main()


