import pandas as pd

def identificar_zona_e_ajuste(localidade):
    loc = normalizar(localidade)
    
    if "madeira" in loc or "feira" in loc:
        zona = "ZONA_A_SJM_FEIRA"
    elif "azemeis" in loc or "cambra" in loc:
        zona = "ZONA_C_INDUSTRIAL"
    elif "espinho" in loc or "aveiro" in loc:
        zona = "ZONA_A_PLUS"
    else:
        zona = "ZONA_B_EXPANSAO"

    litoral_check = ["ovar", "esmoriz", "cortegaça", "furadouro", "jacinto"]
    tem_ajuste_litoral = any(x in loc for x in litoral_check)
    
    return zona, tem_ajuste_litoral

def calcular_score_inteligente(row, df_config):
    zona_id, bonus_mar = identificar_zona_e_ajuste(row['Localidade'])
    
    conf = df_config.loc[zona_id]
    
    ref_venda = float(conf['Ref_Venda_Pronto'])
    
    if bonus_mar:
        ref_venda = ref_venda * 1.15
        
    venda_liquida = ref_venda / 1.0615
    
    teto_compra = (venda_liquida - float(conf['Custo_Obra'])) / (1 + float(conf['Margem_Flip']))
    
    preco_m2_anuncio = row['Preco_Listagem'] / row['Area_m2']
    
    ratio = preco_m2_anuncio / teto_compra
    
    if ratio <= 1.0: return 5  
    if ratio <= 1.15: return 4 
    return 3                   

