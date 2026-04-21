import streamlit as st
import pandas as pd
import urllib.parse
import os
import base64

# --- 1. CONFIGURAÇÃO DE ELITE ---
st.set_page_config(page_title="PM 5D+ | Asset Intelligence", layout="wide")

def get_base64(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return ""

# Assets (Garante que os nomes dos ficheiros no GitHub são estes)
fundo_marmore = get_base64("Background.svg")
logo_paulo = "Paulo Moreira Consultoria & Gestão.png"

# --- 2. CSS SOBERANO (Design de Decisão) ---
st.markdown(f"""
    <style>
    .stApp {{ background-image: url("data:image/svg+xml;base64,{fundo_marmore}"); background-size: cover; background-attachment: fixed; }}
    .card-5d {{
        background: rgba(255, 255, 255, 0.95); padding: 25px; border-radius: 15px;
        border-left: 10px solid #bfa573; box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin-bottom: 25px; color: #1a1a1a;
    }}
    .badge-status {{ background: #bfa573; color: white; padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; }}
    .metric-title {{ font-size: 12px; color: #666; font-weight: bold; text-transform: uppercase; }}
    .metric-value {{ font-size: 20px; color: #bfa573; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGICA DE NEGÓCIO (Funções do Solo Agent) ---
def get_badge(status):
    mapping = {
        "Novo": "🆕 Novo no mercado",
        "Em Analise": "🔍 Em análise 5D",
        "Validado": "✅ Oportunidade Validada",
        "Destaque": "⭐ Destaque Investidor"
    }
    return mapping.get(status, "🔍 Sob Análise")

def mostrar_alertas(row):
    alertas = []
    if row['Area_Bruta'] == row['Area_Terreno']:
        alertas.append("Verificar coerência entre área bruta e terreno (Nota Técnica)")
    if "recuperar" in str(row['Estado']).lower():
        alertas.append("Ponto de Validação: Necessário orçamento de CAPEX")
    
    if alertas:
        with st.expander("⚠️ Notas de Inteligência Técnica"):
            for a in alertas:
                st.info(a)

# --- 4. ENGINE DE DADOS ---
def main():
    if os.path.exists(logo_paulo):
        st.image(logo_paulo, use_container_width=True)

    # Link da tua Sheet Blindada
    SHEET_ID = "1PoK3Gj6mdLVkniIzDgFNhwmOGgpznRAIC0CGzweASag"
    URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

    try:
        df = pd.read_csv(URL)
    except:
        st.error("Erro na ligação à Base de Dados. Verifica a partilha da Sheet.")
        return

    st.title("🚀 Intelligence Scanner 5D+")
    
    # Filtro de Escassez (Só mostra Score >= 3)
    df = df[df['Score_PM5D'] >= 3]

    for index, row in df.iterrows():
        with st.container():
            st.markdown(f'<div class="card-5d">', unsafe_allow_html=True)
            
            # Cabeçalho do Card
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown(f"<span class='badge-status'>{get_badge(row.get('Status', 'Novo'))}</span>", unsafe_allow_html=True)
                st.subheader(f"📍 {row['Localidade']} | Ref: {row['Referencia']}")
            
            with c2:
                score = int(row['Score_PM5D'])
                st.write(f"**Score de Investimento**")
                st.progress(score / 5)
                if score >= 4: st.success("Potencial Elevado")

            # Conteúdo Central
            col_img, col_metrics = st.columns([1, 2])
            with col_img:
                st.image("https://via.placeholder.com/400x300.png?text=IMÓVEL+IDENTIFICADO", use_container_width=True)
                st.write(f"**Tipo:** {row['Tipo']}")
            
            with col_metrics:
                # Dashboard de Resultados
                m1, m2, m3 = st.columns(3)
                m1.markdown(f"<span class='metric-title'>Inv. Total</span><br><span class='metric-value'>{row['Investimento_Total']:,.0f}€</span>", unsafe_allow_html=True)
                m2.markdown(f"<span class='metric-title'>ROI Est. (Flip)</span><br><span class='metric-value'>{row['ROI_Percent']*100:.1f}%</span>", unsafe_allow_html=True)
                m3.markdown(f"<span class='metric-title'>Rend. Anual</span><br><span class='metric-value'>{row['Yield_Euros_Ano']:,.0f}€</span>", unsafe_allow_html=True)
                
                # Alertas Técnicos (O teu diferencial)
                mostrar_alertas(row)

                # CTAs (Call to Actions)
                st.write("---")
                bt1, bt2 = st.columns(2)
                
                # Link para o anúncio original (KW) - Respeito ao colega
                if 'Link_Fonte' in row:
                    bt1.link_button("🌐 Ver Fonte Original", row['Link_Fonte'], use_container_width=True)
                
                # Lead Gen: O Botão do Relatório
                msg = f"Olá Paulo! Quero o Relatório 5D da Ref {row['Referencia']}. O meu email é: "
                bt2.link_button("📄 Receber Deal Pack PDF", f"https://wa.me/351911995695?text={urllib.parse.quote(msg)}", type="primary", use_container_width=True)

            st.markdown('</div>', unsafe_allow_html=True)

    # Rodapé VIP
    st.sidebar.title("💎 Área VIP")
    st.sidebar.write("Receba as oportunidades 48h antes do mercado.")
    if st.sidebar.button("Pedir Acesso Exclusivo"):
        st.sidebar.success("Solicitação enviada para Paulo Moreira.")

if __name__ == "__main__":
    main()
