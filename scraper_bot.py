import requests
import hashlib
import pandas as pd
import os
import re
from bs4 import BeautifulSoup
from bridge import enviar_para_sheet

# Configurações de Ambiente
SHEET_ID = os.getenv("SHEET_ID", "1PoK3Gj6mdLVkniIzDgFNhwmOGgpznRAIC0CGzweASag")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

SHEET_LEADS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=LEADS"
ZONAS_ALVO = ["madeira", "azeméis", "feira", "ovar", "cambra", "arouca", "aveiro"]

def enviar_telegram(msg):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID: return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=10)
    except: pass

def limpar_preco(texto_raw):
    try:
        # 🔥 SOLUÇÃO REGEX: Procura números que venham antes do símbolo €
        # Captura grupos de dígitos que podem ter espaços ou pontos no meio
        match = re.search(r'([\d\s\.]+)\s*€', str(texto_raw))
        if match:
            valor = match.group(1)
            # Remove espaços e pontos para converter em número puro
            valor_limpo = re.sub(r'[\s\.]', '', valor)
            return float(valor_limpo)
        return 0
    except:
        return 0

def calcular_score_pm5d(titulo, preco):
    p = float(preco)
    if p <= 5000: return 1 # Evita lixo ou preços "sob consulta"
    t = titulo.lower()
    
    if any(w in t for w in ["terreno", "lote"]): ref = 75000
    elif any(w in t for w in ["apartamento", "t1", "t2"]): ref = 220000
    else: ref = 450000 # Moradias
    
    ratio = p / ref
    if ratio < 0.70: return 5
    if ratio < 0.85: return 4
    if ratio <= 1.05: return 3
    return 2

def carregar_hashes_existentes():
    try:
        df = pd.read_csv(SHEET_LEADS)
        return set(df["Hash"].astype(str)) if "Hash" in df.columns else set()
    except: return set()

def scraper_custojusto():
    print("🔎 Scraping CustoJusto...")
    url = "https://www.custojusto.pt/aveiro/imobiliario/moradias-venda"
    headers = {"User-Agent": "Mozilla/5.0"}
    items = []
    try:
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        for ad in soup.select("a[href*='/imovel/'], a[href*='/moradia/']"):
            try:
                titulo = ad.get_text(strip=True)
                link = ad["href"]
                parent = ad.find_parent()
                texto = parent.get_text(" ", strip=True)
                if any(z in texto.lower() for z in ZONAS_ALVO):
                    items.append({"Titulo": titulo, "PrecoRaw": texto, "Link": link, "Fonte": "CustoJusto"})
            except: continue
    except Exception as e: print(f"❌ Erro CJ: {e}")
    return items

def scraper_sapo():
    print("🔎 Scraping Sapo Casas...")
    url = "https://casa.sapo.pt/venda/moradias/aveiro/"
    headers = {"User-Agent": "Mozilla/5.0"}
    items = []
    try:
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        # Tentativa de seletor mais específico, senão volta ao genérico
        ads = soup.select("div.searchResultProperty") or soup.select("article")
        for ad in ads:
            texto = ad.get_text(" ", strip=True)
            if "€" in texto and any(z in texto.lower() for z in ZONAS_ALVO):
                try:
                    link_tag = ad.find("a")
                    if not link_tag: continue
                    link = link_tag.get("href", "")
                    if not link.startswith("http"): link = "https://casa.sapo.pt" + link
                    items.append({"Titulo": texto[:80], "PrecoRaw": texto, "Link": link, "Fonte": "SapoCasas"})
                except: continue
    except Exception as e: print(f"❌ Erro Sapo: {e}")
    return items

def run():
    print("🚀 INICIANDO PROCESSAMENTO DE LEADS")
    leads_raw = scraper_custojusto() + scraper_sapo()
    print(f"📡 Total bruto: {len(leads_raw)}")
    
    hashes_existentes = carregar_hashes_existentes()
    
    for item in leads_raw:
        preco = limpar_preco(item["PrecoRaw"])
        score = calcular_score_pm5d(item["Titulo"], preco)
        
        # DEBUG LOG para monitorização
        print(f"DEBUG → {item['Fonte']} | {item['Titulo'][:30]} | Preço: {preco}€ | Score: {score}")

        if score < 2: continue
        
        h_str = f"{item['Titulo']}{preco}".strip().lower()
        h = hashlib.md5(h_str.encode()).hexdigest()
        
        if h in hashes_existentes: continue

        lead = {
            "Referencia": h[:8], "Titulo": item["Titulo"][:100], "Localidade": "Aveiro/Zonas Alvo",
            "Preco": preco, "Link_Fonte": item["Link"], "Fonte": item["Fonte"],
            "Score_PM5D": score, "Prioridade": "ALTA" if score >= 4 else "MEDIA",
            "Hash": h, "Estado": "NOVO", "Decisao": "", "Notas": ""
        }
        
        ok = enviar_para_sheet(lead)
        print(f"📤 Envio para sheet: {ok}")
        
        if ok:
            if score >= 4:
                enviar_telegram(f"💎 OPORTUNIDADE {score}/5\n{item['Titulo'][:100]}\nPreço: {preco}€\n{item['Link']}")
            hashes_existentes.add(h)

if __name__ == "__main__":
    run()
