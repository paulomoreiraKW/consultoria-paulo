import re
import unicodedata
import pandas as pd

# Grupos Geográficos para o Radar (Configuração fixa de nomes)
ZONAS_GEO = {
    "ZONA_A_SJM_FEIRA": ["madeira", "feira", "sjm", "sao joao"],
    "ZONA_C_INDUSTRIAL": ["azemeis", "cambra", "cesar", "fajoes", "loureiro"],
    "ZONA_A_PLUS": ["espinho", "aveiro"],
    "LITORAL_BONUS": ["ovar", "esmoriz", "cortegaça", "furadouro", "jacinto"]
}

def normalizar(txt):
    if not txt: return ""
    txt = str(txt).lower()
    txt = unicodedata.normalize("NFD", txt).encode("ascii", "ignore").decode("utf-8")
    return txt

def identificar_zona_e_ajuste(localidade):
    loc = normalizar(localidade)
    zona = "ZONA_B_EXPANSAO" # Default para quem não está nas capitais
    
    for key, lista in ZONAS_GEO.items():
        if any(freg in loc for freg in lista):
            if key != "LITORAL_BONUS":
                zona = key
                break
                
    tem_ajuste_litoral = any(l in loc for l in ZONAS_GEO["LITORAL_BONUS"])
    return zona, tem_ajuste_litoral

def get_zona_label(localidade):
    zona_id, bonus = identificar_zona_e_ajuste(localidade)
    label = zona_id.replace("_", " ")
    return f"{label} (+Litoral)" if bonus else label

def calcular_score(titulo, preco, localidade, area, df_config=None):
    if preco <= 0 or area <= 0: return 1
    if df_config is None or df_config.empty: return 3 
    
    zona_id, bonus_mar = identificar_zona_e_ajuste(localidade)
    
    try:
        conf = df_config.set_index('Zona').loc[zona_id]
        ref_venda = float(conf['Ref_Venda_Pronto'])
        
        if bonus_mar:
            ref_venda *= 1.15 
            
        venda_liquida = ref_venda / 1.0615
        
        # --- FUNDAMENTAÇÃO TÉCNICA DE ATIVOS ---
        # Identificamos se é Terreno para ajustar a incidência do Custo de Obra
        nome_norm = normalizar(titulo)
        is_terreno = any(w in nome_norm for w in ["terreno", "lote", "parcela", "urbanizavel"])
        
        custo_obra_base = float(conf['Custo_Obra'])
        
        if is_terreno:
            # Para terrenos, o "Custo de Obra" na folha CONFIG representa a construção futura.
            # No cálculo de teto de compra imediato, aplicamos apenas custos de infraestrutura/licenciamento (estimados em 15%)
            # para não canibalizar a viabilidade do solo.
            custo_incidente = custo_obra_base * 0.15
        else:
            custo_incidente = custo_obra_base

        # Cálculo do Teto de Compra (Métrica Real de Investimento)
        teto_compra = (venda_liquida - custo_incidente) / (1 + float(conf['Margem_Flip']))
        
        valor_m2_anuncio = preco / area
        ratio = valor_m2_anuncio / teto_compra
        
        # --- ESCALA DE SCORE 5D (ZONAS DETALHADAS) ---
        if ratio <= 1.05: return 5     # Ativo em preço de oportunidade técnica
        if ratio <= 1.25: return 4     # Ativo alinhado com margens de segurança
        if ratio <= 1.50: return 3     # Preço de mercado (Sem margem de Flip imediata)
        return 2                       # Ativo sobrevalorizado perante a métrica 5D
    except:
        return 2
