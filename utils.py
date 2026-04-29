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
    """
    Mantém o nome da função para o main.py não partir, 
    mas usa a nova lógica financeira.
    """
    if preco <= 0 or area <= 0: return 1
    if df_config is None or df_config.empty: return 3 # Fallback se não carregar config
    
    zona_id, bonus_mar = identificar_zona_e_ajuste(localidade)
    
    try:
        # Tenta buscar a linha da zona no Sheets (indexada pela coluna 'Zona')
        conf = df_config.set_index('Zona').loc[zona_id]
        
        ref_venda = float(conf['Ref_Venda_Pronto'])
        if bonus_mar:
            ref_venda *= 1.15 # Bónus Automático Litoral
            
        # Limpeza de Margem de Venda (1.0615)
        venda_liquida = ref_venda / 1.0615
        
        # Teto para Recuperar (SOP MASTER)
        teto_compra = (venda_liquida - float(conf['Custo_Obra'])) / (1 + float(conf['Margem_Flip']))
        
        valor_m2_anuncio = preco / area
        ratio = valor_m2_anuncio / teto_compra
        
        if ratio <= 1.0: return 5
        if ratio <= 1.15: return 4
        if ratio <= 1.30: return 3
        return 2
    except:
        return 2
