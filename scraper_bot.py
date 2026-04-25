import requests
import hashlib
import pandas as pd
import os
import re
from playwright.sync_api import sync_playwright
from utils import *
from bridge import enviar_para_sheet

SHEET_ID = os.getenv("SHEET_ID")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SHEET_LEADS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=LEADS"

def enviar_telegram(msg):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg})
    except:
        pass

def carregar_hashes():
    try:
        df = pd.read_csv(SHEET_LEADS)
        return set(df["Hash"].astype(str))
    except:
        return set()

def scraper_idealista():
    items = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.idealista.pt/comprar-casas/aveiro-distrito/")
        page.wait_for_timeout(5000)
        ads = page.locator("article")
        for i in range(min(ads.count(), 20)):
            try:
                ad = ads.nth(i)
                titulo_elem = ad.locator(".item-link")
                texto_completo = ad.inner_text()
                link = "https://www.idealista.pt" + titulo_elem.get_attribute("href")
                area_match = re.search(r'(\d+)\s*m²', texto_completo)
                area = float(area_match.group(1)) if area_match else 0
                items.append({
                    "Titulo": titulo_elem.inner_text().split('\n')[0][:120],
                    "PrecoRaw": ad.locator(".item-price").inner_text(),
                    "Link": link,
                    "Fonte": "Idealista",
                    "Area": area
                })
            except:
                continue
        browser.close()
    return items

def run():
    leads = scraper_idealista()
    hashes = carregar_hashes()
    for item in leads:
        preco = limpar_preco(item["PrecoRaw"])
        area_raw = tratar_area(item["Area"])
        titulo = item["Titulo"]
        if preco == 0:
            continue
        localidade = extrair_localidade(titulo)
        tipologia = detectar_tipologia(titulo)
        h = hashlib.md5(item["Link"].encode()).hexdigest()
        if h in hashes:
            continue
        score, area_final, estimado = calcular_score(titulo, preco, localidade, area_raw)
        if score < 3:
            continue
        lead = {
            "Referência": h[:8],
            "Título": titulo,
            "Localidade": localidade,
            "Tipologia": tipologia,
            "Área_Útil": area_final,
            "Preço": preco,
            "Link_Fonte": item["Link"],
            "Fonte": item["Fonte"],
            "Score_PM5D": score,
            "Prioridade": "ALTA" if score >= 4 else "BAIXA",
            "Hash": h,
            "Notas": "AREA_ESTIMADA" if estimado else ""
        }
        if enviar_para_sheet(lead):
            hashes.add(h)
            msg = f"SCORE {score} | {localidade}\n{preco:,.0f}€\n{item['Link']}"
            if estimado:
                msg += "\n⚠️ Área estimada (100m²)"
            enviar_telegram(msg)

if __name__ == "__main__":
    run()
