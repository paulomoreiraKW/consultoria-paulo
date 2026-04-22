import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import hashlib

# ==============================
# CONFIG
# ==============================

SHEET_ID = "1PoK3Gj6mdLVkniIzDgFNhwmOGgpznRAIC0CGzweASag"
SHEET_ACTIVOS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=ACTIVOS"
SHEET_LEADS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=LEADS"

TELEGRAM_TOKEN = "COLOCA_AQUI"
TELEGRAM_CHAT_ID = "COLOCA_AQUI"

HEADERS = {"User-Agent": "Mozilla/5.0"}

# ==============================
# TELEGRAM
# ==============================

def enviar_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg})
    except:
        pass

# ==============================
# HASH (DEDUPLICAÇÃO)
# ==============================

def gerar_hash(titulo, preco, local):
    base = f"{titulo}_{preco}_{local}"
    return hashlib.md5(base.encode()).hexdigest()

# ==============================
# SCORE AUTOMÁTICO (PRÉ-5D)
# ==============================

def calcular_score(preco, media_zona):
    try:
        preco = float(preco)
        media_zona = float(media_zona)

        if preco < media_zona * 0.8:
            return 5
        elif preco < media_zona * 0.9:
            return 4
        elif preco < media_zona:
            return 3
        else:
            return 2
    except:
        return 1

# ==============================
# SCRAPER OLX (BÁSICO)
# ==============================

def scrape_olx():
    url = "https://www.olx.pt/imoveis/apartamentos-casas-venda/"

    results = []

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "lxml")

        listings = soup.select("div[data-cy='l-card']")

        for item in listings[:20]:

            titulo = item.select_one("h6")
            preco = item.select_one("[data-testid='ad-price']")
            local = item.select_one("[data-testid='location-date']")

            titulo = titulo.text.strip() if titulo else ""
            preco = preco.text.strip().replace("€","").replace(" ","") if preco else "0"
            local = local.text.strip() if local else ""

            link = item.find("a")
            link = "https://www.olx.pt" + link["href"] if link else ""

            if titulo:
                results.append({
                    "Titulo": titulo,
                    "Preco": preco,
                    "Local": local,
                    "Link": link,
                    "Fonte": "OLX"
                })

    except Exception as e:
        print("Erro OLX:", e)

    return results

# ==============================
# SCRAPER IDEALISTA (SIMPLES)
# ==============================

def scrape_idealista():
    url = "https://www.idealista.pt/comprar-casas/"

    results = []

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "lxml")

        items = soup.select(".item")

        for item in items[:20]:

            titulo = item.select_one(".item-link")
            preco = item.select_one(".item-price")
            local = item.select_one(".item-location")

            titulo = titulo.text.strip() if titulo else ""
            preco = preco.text.strip().replace("€","").replace(".","") if preco else "0"
            local = local.text.strip() if local else ""

            link = titulo["href"] if titulo else ""
            link = "https://www.idealista.pt" + link if link else ""

            if titulo:
                results.append({
                    "Titulo": titulo,
                    "Preco": preco,
                    "Local": local,
                    "Link": link,
                    "Fonte": "Idealista"
                })

    except Exception as e:
        print("Erro Idealista:", e)

    return results

# ==============================
# LOAD EXISTENTE
# ==============================

def carregar_existente():
    try:
        df = pd.read_csv(SHEET_ACTIVOS)
        return df
    except:
        return pd.DataFrame()

# ==============================
# PIPELINE PRINCIPAL
# ==============================

def run():

    print("🔍 A caçar oportunidades...")

    existentes = carregar_existente()
    hashes_existentes = set()

    if not existentes.empty and "Hash" in existentes.columns:
        hashes_existentes = set(existentes["Hash"].astype(str))

    novos = []

    # SCRAPERS
    dados = []
    dados += scrape_olx()
    dados += scrape_idealista()

    for item in dados:

        hash_id = gerar_hash(item["Titulo"], item["Preco"], item["Local"])

        if hash_id in hashes_existentes:
            continue

        score = calcular_score(item["Preco"], 150000)  # média fictícia

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

        novos.append(novo)

        enviar_telegram(f"🔥 Novo activo ({prioridade})\n{item['Titulo']}\n{item['Preco']}€\n{item['Local']}")

    if novos:
        df_novos = pd.DataFrame(novos)

        print(f"✅ {len(novos)} novos activos encontrados")

        # GUARDAR LOCAL (backup)
        df_novos.to_csv("novos_activos.csv", index=False)

    else:
        print("Sem novidades")

# ==============================
# LOOP CONTÍNUO
# ==============================

if __name__ == "__main__":
    while True:
        run()
        time.sleep(300)  # 5 minutos
