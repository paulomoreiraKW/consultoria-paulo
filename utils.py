import re
import unicodedata
from config import REFERENCIAIS_MERCADO_2026

def normalizar(txt):
    if not txt:
        return ""
    txt = str(txt).lower()
    txt = unicodedata.normalize("NFD", txt).encode("ascii", "ignore").decode("utf-8")
    return txt

def get_zona_data(localidade):
    loc = normalizar(localidade)
    for zona, dados in REFERENCIAIS_MERCADO_2026.items():
        if zona == "DEFAULT":
            continue
        if any(normalizar(f) in loc for f in dados["freguesias"]):
            return dados
    return REFERENCIAIS_MERCADO_2026["DEFAULT"]

def get_zona_label(localidade):
    loc = normalizar(localidade)
    for zona, dados in REFERENCIAIS_MERCADO_2026.items():
        if zona == "DEFAULT":
            continue
        if any(normalizar(f) in loc for f in dados["freguesias"]):
            return zona.replace("_", " ")
    return "ZONA C"

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
    
    zona = get_zona_data(localidade)
    t = normalizar(titulo)
    
    if any(w in t for w in ["novo", "nova", "construcao"]):
        meta = zona["novo"]
    elif any(w in t for w in ["usado", "usada"]):
        meta = zona["usado"]
    else:
        meta = zona["recuperar"]
        
    if valor_m2 <= meta * 0.7: return 5
    if valor_m2 <= meta * 0.85: return 4
    if valor_m2 <= meta * 1.05: return 3
    if valor_m2 <= meta * 1.25: return 2
    return 1
