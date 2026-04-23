import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import hashlib
import random
import os
from bridge import enviar_para_sheet

SHEET_ID = "1PoK3Gj6mdLVkniIzDgFNhwmOGgpznRAIC0CGzweASag"
SHEET_ACTIVOS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=ACTIVOS"
TELEGRAM_TOKEN = "8788076131:AAGwzFhxzD_H4iV2J0BmAP9k4rzEvcEoDSE"
TELEGRAM_CHAT_ID = "477875361"
ZONAS_ALVO = ["madeira", "azeméis", "feira", "ovar", "cambra", "arouca", "aveiro"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Connection": "keep-alive"
}

def enviar_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=10)
    except: pass

def gerar_hash(titulo, preco, local):
    base = f"{titulo}_{preco}_{local}"
    return hashlib.md5(base.encode()).hexdigest()

def calcular_score(titulo, preco):
    try:
        preco = float(preco)
        t = titulo.lower()
        
        if any(w in t for w in ["armazém", "pavilhão", "industrial", "nave"]):
            media_ref = 450000 
        elif any(w in t for w in ["terreno", "lote"]):
            media_ref = 80000
        elif any(w in t for w in ["quinta", "rural", "rústico"]):
            media_ref = 425000
        elif any(w in t for w in ["apartamento", "t1", "t2", "t3", "t4"]):
            media_ref = 225000
        else:
            media_ref = 456890

        if preco < media_ref * 0.75: return 5
        elif preco < media_ref * 0.9: return 4
        elif preco <= media_ref * 1.1: return 3
        else: return 2
    except: return 1

def scrape_olx():
    url = "https://www.olx.pt/imoveis/"
    results = []
    print(f"🌐 Acedendo a: {url}")
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            print(f"❌ Status {r.status_code}")
            return []
        
        soup = BeautifulSoup(r.text, "lxml")
        listings = soup.find_all("div", {"data-cy": "l-card"})
        print(f"🔎 Cards brutos: {len(listings)}")

        for item in listings[:25]:
            try:
                title_el = item.select_one("h6")
                price_el = item.select_one("p[data-testid='ad-price']")
                location_el = item.select_one("p[data-testid='location-date']")
                link_el = item.select_one("a")

                if title_el and price_el:
                    titulo = title_el.get_text(strip=True)
                    local = location_el.get_text(strip=True) if location_el else "N/A"
                    p_raw = price_el.get_text(strip=True).replace("€", "").replace(" ", "").replace(".", "").split(",")[0]
                    preco_int = int(p_raw) if p_raw.isdigit() else 0
                    
                    if not any(zona in local.lower() for zona in ZONAS_ALVO): continue
                    if preco_int < 15000 or preco_int > 4000000: continue

                    print(f"✅ Detetado: {titulo[:30]} | {preco_int}€")

                    results.append({
                        "Titulo": titulo,
                        "Preco": str(preco_int),
                        "Local": local,
                        "Link": "https://www.olx.pt" + link_el['href'] if link_el['href'].startswith("/") else link_el['href'],
                        "Fonte": "OLX"
                    })
            except: continue
        return results
    except Exception as e:
        print(f"❌ Erro: {e}")
        return []

def carregar_existente():
    try:
        df = pd.read_csv(SHEET_ACTIVOS)
        return df
    except: return pd.DataFrame()

def run():
    print("🚀 Run iniciado")
    existentes = carregar_existente()
    hashes_existentes = set(existentes["Hash"].astype(str)) if not existentes.empty and "Hash" in existentes.columns else set()
    
    dados = scrape_olx()
    for item in dados:
        hash_id = gerar_hash(item["Titulo"], item["Preco"], item["Local"])
        if hash_id in hashes_existentes: continue

        score = calcular_score(item["Titulo"], item["Preco"])
        prioridade = "ALTA" if score >= 4 else "MEDIA" if score == 3 else "BAIXA"

        novo = {
            "Referencia": hash_id[:8],
            "Titulo": item["Titulo"],
            "Localidade": item["Local"],
            "Preco": item["Preco"],
            "Link_Fonte": item["Link"],
            "Fonte": item["Fonte"],
            "Score_PM5D": score,
            "Prioridade": prioridade,
            "Hash": hash_id
        }

        if enviar_para_sheet(novo):
            if prioridade == "ALTA":
                enviar_telegram(f"🔥 OPORTUNIDADE {prioridade}\n{item['Titulo']}\n{item['Preco']}€\n{item['Local']}")
            hashes_existentes.add(hash_id)
            print(f"💾 Guardado: {item['Titulo'][:20]}")

if __name__ == "__main__":
    run()
