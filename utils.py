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
    zona = "ZONA_B_EXPANSAO" 
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
    """
    METODOLOGIA: Método Residual Estático (Normas CMVM).
    OBJETIVO: Avaliar a viabilidade do Ativo (Solo ou Edificado) 
    perante o custo de oportunidade e CAPEX operacional.
    """
    if preco <= 0 or area <= 0: return 1
    if df_config is None or df_config.empty: return 3 
    
    zona_id, bonus_mar = identificar_zona_e_ajuste(localidade)
    
    try:
        # 1. PARÂMETROS DE ZONA
        conf = df_config.set_index('Zona').loc[zona_id]
        ref_venda = float(conf['Ref_Venda_Pronto'])
        if bonus_mar: ref_venda *= 1.15 
            
        # 2. LIMPEZA DE GCI (Comissões e Impostos de Saída)
        venda_liquida = ref_venda / 1.0615
        
        # 3. DIFERENCIAÇÃO TÉCNICA (TERRENO vs EDIFICADO)
        nome_norm = normalizar(titulo)
        is_solo = any(w in nome_norm for w in ["terreno", "lote", "parcela", "urbanizavel"])
        
        custo_obra_base = float(conf['Custo_Obra'])
        
        if is_solo:
            # Em solos, o custo incidente foca em Infraestruturas/Licenciamento
            # Fundamento: Padrão 15% do CAPEX de construção integral.
            custo_incidente = custo_obra_base * 0.15
        else:
            # Em edificado, assume-se reabilitação/obra integral (CAPEX 100%)
            custo_incidente = custo_obra_base

        # 4. TETO DE COMPRA (O valor máximo que o investidor pode pagar para lucrar)
        # Fórmula: (Valor de Saída - Custos) / (1 + Margem de Lucro)
        teto_compra = (venda_liquida - custo_incidente) / (1 + float(conf['Margem_Flip']))
        
        # 5. RÁCIO DE VIABILIDADE
        valor_m2_anuncio = preco / area
        ratio = valor_m2_anuncio / teto_compra
        
        # 6. SCORE 5D (RIGOR TÉCNICO)
        if ratio <= 1.00: return 5     # Oportunidade Pura (Abaixo do Teto)
        if ratio <= 1.15: return 4     # Ativo Validado (Margem Segura)
        if ratio <= 1.35: return 3     # Preço de Mercado (Fronteira de Risco)
        return 2                       # Ativo Especulativo (Sem Viabilidade)
        
    except:
        return 2
