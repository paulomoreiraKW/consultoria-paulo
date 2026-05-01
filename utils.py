import re
import unicodedata
import pandas as pd

# 1. CONFIGURAÇÕES GEOGRÁFICAS
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

# --- NOVIDADE: A FUNÇÃO QUE FALTAVA ---
def extrair_capex_do_titulo(titulo):
    nome = normalizar(titulo)
    if "s/capex" in nome or "s/ obra" in nome: return 0
    if any(x in nome for x in ["total", "ruina", "reconstruir"]): return 900
    if any(x in nome for x in ["remodelar", "c/capex", "c/ obra"]): return 450
    if any(x in nome for x in ["pintura", "cosmetica", "ligeiro"]): return 150
    return 0
    
def classificar_estado(capex):
    if capex == 0:
        return "PRONTO"
    if capex <= 200:
        return "LIGEIRO"
    if capex <= 600:
        return "MEDIO"
    return "PESADO"
    
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

# 2. NORMALIZAÇÃO DE ÁREA
def get_area_real(row):
    try:
        area_bruta = float(str(row.get("Area_m2") or 0).replace(",","."))
        area_util = float(str(row.get("Area_Util") or 0).replace(",","."))
        tipo = (str(row.get("Tipologia") or "")).upper()

        if area_bruta > 0: return area_bruta

        if area_util > 0:
            if "APARTAMENTO" in tipo: return area_util * 1.15
            if any(x in tipo for x in ["MORADIA", "INDEPENDENTE", "GEMINADA"]): return area_util * 1.20
            if any(x in tipo for x in ["PAVILHAO", "ARMAZEM", "INDUSTRIAL"]): return area_util * 1.10
            return area_util * 1.20
        return 0
    except: return 0

def get_area_qualidade(row):
    if float(str(row.get("Area_m2") or 0).replace(",",".")) > 0: return "BRUTA"
    if float(str(row.get("Area_Util") or 0).replace(",",".")) > 0: return "ESTIMADA"
    return "SEM_DADOS"

# 3. IDENTIFICAÇÃO DE TIPOLOGIA
def identificar_tipologia(titulo):
    nome = normalizar(titulo)
    if "terreno" in nome or "lote" in nome: return "TERRENO"
    if any(x in nome for x in ["pavilhao", "armazem", "armazens"]): return "INDUSTRIAL"
    if "apartamento" in nome or re.search(r'\bt[0-9]\b', nome): return "APARTAMENTO"
    
    if "terrea" in nome:
        return "TERREA_GEMINADA" if "geminada" in nome else "TERREA_INDEPENDENTE"
    
    if "geminada" in nome:
        return "GEMINADA_PONTA" if "ponta" in nome else "GEMINADA"
    
    if any(x in nome for x in ["independente", "isolada", "4 frentes"]): return "INDEPENDENTE"
    
    return "MORADIA"

# 4. CÁLCULO DO SCORE 5D
def calcular_score(row, df_config):
    try:
        # 1. Limpeza inicial (TEU CÓDIGO)
        preco = float(str(row.get("Preco_Listagem") or 0).replace(",","."))
        area = float(str(row.get("Area_m2") or 0).replace(",","."))
        localidade = row.get("Localidade")
        tipo = row.get("Tipologia")
        titulo = row.get("Titulo", "")

        if preco <= 0 or area <= 0: return 1

        # 2. Configurações de Zona (TEU CÓDIGO)
        zona_id, bonus_mar = identificar_zona_e_ajuste(localidade)
        conf = df_config.set_index('Zona').loc[zona_id]

        ref_venda = float(str(conf['Ref_Venda_Pronto']).replace(",","."))
        custo_obra_base = float(str(conf['Custo_Obra']).replace(",","."))
        
        def clean_pct(val):
            v = str(val).replace("%","").replace(",",".").strip()
            return float(v)/100 if float(v) > 1 else float(v)

        margem_flip = clean_pct(conf['Margem_Flip'])
        margem_venda = clean_pct(conf['Margem_Venda']) if 'Margem_Venda' in conf else 1.0615

        # 3. Ajustes de Tipologia (TEU CÓDIGO)
        if tipo == "INDEPENDENTE": ref_venda *= 1.10
        elif tipo == "GEMINADA": ref_venda *= 0.95
        elif tipo == "TERREA_INDEPENDENTE": ref_venda *= 1.15
        
        if bonus_mar: ref_venda *= 1.15

        # 4. IDENTIFICAÇÃO DO ESTADO (NOVA LÓGICA)
        capex_hint = extrair_capex_do_titulo(titulo)
        estado = classificar_estado(capex_hint)

        fator_estado_venda = {"PRONTO": 1.00, "LIGEIRO": 0.97, "MEDIO": 0.93, "PESADO": 0.88}
        penalizacao_liquidez = {"PRONTO": 1.00, "LIGEIRO": 1.02, "MEDIO": 1.05, "PESADO": 1.10}

        # Aplicar penalização no valor de venda pelo estado do imóvel
        ref_venda *= fator_estado_venda.get(estado, 1.0)
        venda_liquida = ref_venda / margem_venda

        # 5. Ajustes de Custo de Obra (TEU CÓDIGO + NOVO CAPEX)
        if tipo == "TERRENO": custo_incidente = custo_obra_base * 0.15
        elif tipo == "GEMINADA": custo_incidente = custo_obra_base * 0.90
        elif tipo == "GEMINADA_PONTA": custo_incidente = custo_obra_base * 0.95
        elif tipo == "TERREA_GEMINADA": custo_incidente = custo_obra_base * 0.95
        elif tipo == "TERREA_INDEPENDENTE": custo_incidente = custo_obra_base * 1.10
        elif tipo == "INDEPENDENTE": custo_incidente = custo_obra_base * 1.10
        else: custo_incidente = custo_obra_base

        # Somamos o Capex extraído do título ao custo incidente da tipologia
        custo_total_obra = custo_incidente + capex_hint

        # 6. Cálculo do Teto com Penalização de Liquidez (NOVA LÓGICA)
        teto_compra_base = (venda_liquida - custo_total_obra) / (1 + margem_flip)
        teto_final = teto_compra_base / penalizacao_liquidez.get(estado, 1.0)
        
        # 7. Ratio e Estrelas (TEU CÓDIGO)
        ratio = (preco / area) / teto_final

        if ratio <= 1.00: return 5
        if ratio <= 1.15: return 4
        if ratio <= 1.35: return 3
        return 2
    except:
        return 2
