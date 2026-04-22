from bridge import enviar_para_sheet
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

TELEGRAM_TOKEN = "PauloMConsultoria_Bot"
TELEGRAM_CHAT_ID = "8788076131:AAGwzFhxzD_H4iV2J0BmAP9k4rzEvcEoDSE"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

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

import time
import random

def scrape_olx():
    url = "https://www.olx.pt/imoveis/apartamentos-casas-venda/?search%5Border%5D=created_at:desc"
    results = []
    print("🌐 Acedendo ao OLX...")

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        
        if r.status_code != 200:
            print(f"⚠️ OLX erro: {r.status_code}")
            return []

        soup = BeautifulSoup(r.text, "lxml")
        listings = soup.select("div[data-cy='l-card']")

        for item in listings[:15]:
            time.sleep(random.uniform(1.5, 3.5))
            
            try:
                title_el = item.select_one("h6")
                price_el = item.select_one("p[data-testid='ad-price']")
                location_el = item.select_one("p[data-testid='location-date']")
                link_el = item.select_one("a")

                if title_el and price_el and link_el:
                    titulo = title_el.get_text(strip=True)
                    preco_raw = price_el.get_text(strip=True).replace("€", "").replace(" ", "").replace(".", "").split(",")[0]
                    
                    results.append({
                        "Titulo": titulo,
                        "Preco": preco_raw,
                        "Local": location_el.get_text(strip=True) if location_el else "N/A",
                        "Link": "https://www.olx.pt" + link_el['href'] if link_el['href'].startswith("/") else link_el['href'],
                        "Fonte": "OLX"
                    })
            except:
                continue

        print(f"📦 OLX: {len(results)} itens.")
        return results

    except Exception as e:
        print(f"❌ Erro OLX: {e}")
        return []

# ==============================
# SCRAPER IDEALISTA (SIMPLES)
# ==============================

def scrape_idealista():
    url = "https://www.idealista.pt/comprar-casas/"

    results = []

    try:
        r = requests.get(url, headers=HEADERS, timeout=5)
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

    # TESTE RÁPIDO: Ver se o bridge funciona antes de tudo
    print("📡 Enviando sinal de teste para a Sheet...")
    teste = {
        "Referencia": "TEST123",
        "Titulo": "TESTE DE LIGAÇÃO",
        "Localidade": "Porto",
        "Preco": "100.000",
        "Link_Fonte": "https://teste.com",
        "Fonte": "TEST",
        "Score_PM5D": 5,
        "Prioridade": "ALTA",
        "Hash": "abc123test"
    }
    enviar_para_sheet(teste)

    existentes = carregar_existente()
    hashes_existentes = set()

    if not existentes.empty and "Hash" in existentes.columns:
        hashes_existentes = set(existentes["Hash"].astype(str))

    # SCRAPERS - Captura individual para diagnóstico
    print("🌐 Acedendo ao OLX...")
    dados_olx = scrape_olx()
    print(f"📦 OLX encontrou: {len(dados_olx)} itens")

    print("🌐 Acedendo ao Idealista...")
    dados_idealista = scrape_idealista()
    print(f"📦 Idealista encontrou: {len(dados_idealista)} itens")

    dados = dados_olx + dados_idealista
    print(f"🚀 Total bruto a processar: {len(dados)}")

    novos_para_csv = []

    for item in dados:
        hash_id = gerar_hash(item["Titulo"], item["Preco"], item["Local"])

        if hash_id in hashes_existentes:
            continue
        
        print(f"✨ Novo item detetado: {item['Titulo'][:30]}...")

        score = calcular_score(item["Preco"], 150000)  
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

        # ENVIO PARA GOOGLE SHEETS
        enviar_para_sheet(novo)

        # NOTIFICAÇÃO TELEGRAM
        enviar_telegram(f"🔥 Novo activo ({prioridade})\n{item['Titulo']}\n{item['Preco']}€\n{item['Local']}")
        
        novos_para_csv.append(novo)
        hashes_existentes.add(hash_id)

    if novos_para_csv:
        print(f"✅ {len(novos_para_csv)} novos activos processados!")
        df_novos = pd.DataFrame(novos_para_csv)
        df_novos.to_csv("novos_activos.csv", index=False)
    else:
        print("⏸️ Sem novidades (tudo o que foi encontrado já existe ou lista vazia)")

# ==============================
# LOOP CONTÍNUO
# ==============================

if __name__ == "__main__":
    run()
