import requests
import hashlib
import pandas as pd
import os
import re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from bridge import enviar_para_sheet

SHEET_ID = os.getenv("SHEET_ID") or "1PoK3Gj6mdLVkniIzDgFNhwmOGgpznRAIC0CGzweASag"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") or ""
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or ""

SHEET_LEADS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=LEADS"

def debug_config():
    print("🔐 CONFIG:")
    print("SHEET_ID:", "OK" if SHEET_ID else "MISSING")
    print("TELEGRAM_TOKEN:", "OK" if TELEGRAM_TOKEN else "MISSING")
    print("TELEGRAM_CHAT_ID:", "OK" if TELEGRAM_CHAT_ID else "MISSING")

def enviar_telegram(msg):
    print("📲 A tentar enviar Telegram...")
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram não configurado")
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        r = requests.post(url, data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": msg
        }, timeout=10)
        print("📲 Telegram status:", r.status_code)
    except Exception as e:
        print("❌ Erro Telegram:", e)

def limpar_preco(texto):
    if not texto:
        return 0
    nums = re.findall(r'\d+', str(texto))
    return float("".join(nums)) if nums else 0

def calcular_score(titulo, preco):
    if preco <= 0:
        return 2
    if preco < 5000:
        return 1
    t = titulo.lower()
    if any(w in t for w in ["terreno", "lote"]):
        ref = 80000
    elif any(w in t for w in ["apartamento", "t1", "t2"]):
        ref = 220000
    else:
        ref = 450000
    ratio = preco / ref
    if ratio < 0.7: return 5
    if ratio < 0.85: return 4
    if ratio <= 1.1: return 3
    return 2

def carregar_hashes():
    try:
        df = pd.read_csv(SHEET_LEADS)
        return set(df["Hash"].astype(str))
    except:
        return set()

def scraper_custojusto():
    print("🔎 CustoJusto...")
    url = "https://www.custojusto.pt/aveiro/imobiliario"
    headers = {"User-Agent": "Mozilla/5.0"}
    items = []
    try:
        r = requests.get(url, headers=headers, timeout=15)
        html = r.text
        links = re.findall(r'href="(https://www\.custojusto\.pt/[^"]+\.htm)"', html)
        for link in set(links):
            items.append({
                "Titulo": "CustoJusto",
                "PrecoRaw": "",
                "Link": link,
                "Fonte": "CustoJusto"
            })
    except Exception as e:
        print("❌ CJ erro:", e)
    return items

def scraper_idealista():
    print("🔎 Idealista...")
    items = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://www.idealista.pt/comprar-casas/aveiro-distrito/")
            page.wait_for_timeout(5000)
            ads = page.query_selector_all("article")
            for ad in ads[:20]:
                try:
                    texto = ad.inner_text()
                    link_el = ad.query_selector("a")
                    link = link_el.get_attribute("href")
                    items.append({
                        "Titulo": texto[:100],
                        "PrecoRaw": texto,
                        "Link": "https://www.idealista.pt" + link,
                        "Fonte": "Idealista"
                    })
                except:
                    continue
            browser.close()
    except Exception as e:
        print("❌ Idealista erro:", e)
    return items

def run():
    print("🚀 START")
    debug_config()
    leads = scraper_custojusto() + scraper_idealista()
    print(f"📡 Leads captadas: {len(leads)}")
    if len(leads) == 0:
        leads = [{
            "Titulo": "TESTE",
            "PrecoRaw": "250000",
            "Link": "https://teste.pt",
            "Fonte": "DEBUG"
        }]
    hashes = carregar_hashes()
    for item in leads:
        preco = limpar_preco(item["PrecoRaw"])
        score = calcular_score(item["Titulo"], preco)
        h = hashlib.md5(item["Link"].encode()).hexdigest()
        if h in hashes:
            continue
        lead = {
            "Referencia": h[:8],
            "Titulo": item["Titulo"],
            "Localidade": "Aveiro",
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
        ok = enviar_para_sheet(lead)
        print("📤 Sheet:", ok)
        if ok:
            hashes.add(h)
            enviar_telegram(
                f"🏠 {item['Fonte']}\n{item['Titulo'][:80]}\n💰 {preco}€\n🔗 {item['Link']}"
            )

if __name__ == "__main__":
    run()
