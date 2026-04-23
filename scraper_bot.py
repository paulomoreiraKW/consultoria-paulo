import requests
import xml.etree.ElementTree as ET
import hashlib
import pandas as pd
from bridge import enviar_para_sheet

SHEET_ID = "1PoK3Gj6mdLVkniIzDgFNhwmOGgpznRAIC0CGzweASag"
SHEET_LEADS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=LEADS"

TELEGRAM_TOKEN = "8788076131:AAGwzFhxzD_H4iV2J0BmAP9k4rzEvcEoDSE"
TELEGRAM_CHAT_ID = "477875361"

ZONAS_ALVO = ["madeira", "azeméis", "feira", "ovar", "cambra", "arouca", "aveiro"]

def enviar_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=10)
    except:
        pass

def limpar_preco(preco_raw):
    try:
        p = str(preco_raw)
        p = p.replace("€", "").replace(" ", "").replace(".", "").replace(",", "")
        return float(p)
    except:
        return 0

def titulo_valido(titulo):
    t = titulo.lower()
    lixo = ["reservado", "arrendado", "promoção", "vendido"]
    return not any(w in t for w in lixo)

def calcular_score_pm5d(titulo, preco):
    try:
        p = float(preco)
        t = titulo.lower()
        if any(w in t for w in ["armazém", "industrial"]): ref = 450000
        elif any(w in t for w in ["terreno", "lote"]): ref = 80000
        elif any(w in t for w in ["apartamento", "t1", "t2"]): ref = 225000
        else: ref = 456890 
        ratio = p / ref
        if ratio < 0.75: return 5
        if ratio < 0.90: return 4
        if ratio <= 1.10: return 3
        return 2
    except:
        return 1

def carregar_hashes_existentes():
    try:
        df = pd.read_csv(SHEET_LEADS)
        if "Hash" in df.columns:
            return set(df["Hash"].astype(str))
    except:
        pass
    return set()

def processar_imovirtual_rss():
    url = "https://www.imovirtual.com/comprar/moradia/aveiro/?search%5Bfilter_float_price%3Ato%5D=600000&format=xml"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code != 200: return []
        root = ET.fromstring(r.content)
        items = []
        for entry in root.findall(".//item"):
            titulo = entry.findtext("title", "")
            link = entry.findtext("link", "")
            preco_raw = entry.findtext("price", "0") 
            local = entry.findtext("location", "Aveiro")
            if any(z in local.lower() for z in ZONAS_ALVO):
                items.append({
                    "Titulo": titulo, "Preco": preco_raw, "Local": local, "Link": link, "Fonte": "Imovirtual_RSS"
                })
        return items
    except:
        return []

def run():
    novos_items = processar_imovirtual_rss()
    hashes_existentes = carregar_hashes_existentes()
    for item in novos_items:
        if not titulo_valido(item["Titulo"]): continue
        preco = limpar_preco(item["Preco"])
        h = hashlib.md5(f"{item['Link']}".encode()).hexdigest()
        if h in hashes_existentes: continue
        score = calcular_score_pm5d(item["Titulo"], preco)
        if score < 3: continue
        lead = {
            "Referencia": h[:8],
            "Titulo": item["Titulo"],
            "Localidade": item["Local"],
            "Preco": preco,
            "Link_Fonte": item["Link"],
            "Fonte": item["Fonte"],
            "Score_PM5D": score,
            "Prioridade": "ALTA" if score >= 4 else "MEDIA",
            "Hash": h,
            "Estado": "NOVO",
            "Decisao": "",
            "Notas": ""
        }
        if enviar_para_sheet(lead):
            if lead["Prioridade"] == "ALTA":
                enviar_telegram(f"💎 NOVA LEAD {lead['Prioridade']}\n{lead['Titulo']}\n{preco}€\n{lead['Link']}")
            hashes_existentes.add(h)

if __name__ == "__main__":
    run()
