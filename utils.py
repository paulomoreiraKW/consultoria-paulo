import re
import unicodedata
from config import REFERENCIAIS_MERCADO_2026

def normalizar(txt):
    if not txt:
        return ""
    txt = txt.lower()
    txt = unicodedata.normalize("NFD", txt)
    txt = txt.encode("ascii", "ignore").decode("utf-8")
    return txt

def limpar_preco(texto):
    if not texto:
        return 0
    nums = re.findall(r'\d+', str(texto).replace(".", "").replace(",", ""))
    return float("".join(nums)) if nums else 0

def tratar_area(area):
    try:
        a = float(area)
        return a if a >= 20 else 0
    except:
        return 0

def extrair_localidade(texto):
    texto = normalizar(texto)
    zonas = {
        "Fornos": ["fornos"],
        "São João de Ver": ["sao joao de ver"],
        "Lourosa": ["lourosa"],
        "Argoncilhe": ["argoncilhe"],
        "Canedo": ["canedo"],
        "Travanca": ["travanca"],
        "Oliveira de Azeméis": ["oliveira de azemeis", "oaz"],
        "São João da Madeira": ["sao joao da madeira", "sjm"]
    }
    for nome, keys in zonas.items():
        if any(k in texto for k in keys):
            return nome
    return "UNKNOWN"

def get_zona(localidade):
    loc = normalizar(localidade)
    for zona, dados in REFERENCIAIS_MERCADO_2026.items():
        if zona == "DEFAULT":
            continue
        if any(normalizar(f) in loc for f in dados["freguesias"]):
            return dados
    return REFERENCIAIS_MERCADO_2026["DEFAULT"]

def detectar_tipologia(titulo):
    t = normalizar(titulo)
    if "moradia" in t:
        return "Moradia"
    elif "terreno" in t:
        return "Terreno"
    elif any(w in t for w in ["pavilhao", "armazem", "industrial"]):
        return "Industrial"
    else:
        return "Apartamento"

def calcular_score(titulo, preco, localidade, area):
    if preco <= 0:
        return 1
    
    area_calculo = area if area > 0 else 100
    valor_m2 = preco / area_calculo
    zona = get_zona(localidade)
    t = normalizar(titulo)
    
    if any(w in t for w in ["novo", "nova", "construcao"]):
        meta = zona["novo"]
    elif any(w in t for w in ["industrial", "pavilhao", "armazem"]):
        meta = zona["industrial"]
    else:
        meta = zona["usado"]
    
    ratio = valor_m2 / meta
    
    if ratio <= 0.90: return 5
    elif ratio <= 1.05: return 4
    elif ratio <= 1.20: return 3
    elif ratio <= 1.35: return 2
    else: return 1
