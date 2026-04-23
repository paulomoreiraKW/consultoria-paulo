import requests
import hashlib
import pandas as pd
import os
import re
from bs4 import BeautifulSoup
from bridge import enviar_para_sheet

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
    if not texto_raw: return 0
    try:
        numeros = re.findall(r'\d+', str(texto_raw))
        if not numeros: return 0
        return float("".join(numeros))
    except: return 0

def calcular_score_pm5d(titulo, preco):
    p = float(preco)
    if p <= 0: return 2
    if p < 5000: return 1
    t = titulo.lower()
    if any(w in t for w in ["terreno", "lote"]): ref = 80000
    elif any(w in t for w in ["apartamento", "t1", "t2"]): ref = 220000
    else: ref = 450000
    ratio = p / ref
    if ratio < 0.70: return 5
    if ratio < 0.85: return 4
    if ratio <= 1.10: return 3
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
        html = r.text.lower()
        links = re.findall(r'href="(https://www.custojusto.pt/[^"]+)"', html)
        for link in set(links):
            if any(z in link for z in ZONAS_ALVO):
                items.append({
                    "Titulo": "Imóvel CustoJusto (Ver Link)",
                    "PrecoRaw": "0",
                    "Link": link,
                    "Fonte": "CustoJusto"
                })
    except: pass
    return items

def scraper_kw_feira():
    print("🔎 Scraping KW Area Feira...")
    url = "https://www.kwportugal.pt/KWAreaFeira"
    headers = {"User-Agent": "Mozilla/5.0"}
    items = []
    try:
        r = requests.get(url, headers=headers, timeout=15)
        html = r.text.lower()
        links = re.findall(r'href="(/imovel/[^"]+)"', html)
        for link in set(links):
            full_link = "https://www.kwportugal.pt" + link
            items.append({
                "Titulo": "Imóvel KW Area Feira",
                "PrecoRaw": "0",
                "Link": full_link,
                "Fonte": "KWFeira"
            })
    except: pass
    return items

def scraper_sapo():
    url = "https://casa.sapo.pt/venda/moradias/aveiro/"
    headers = {"User-Agent": "Mozilla/5.0"}
    items = []
    try:
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        ads = soup.select("div.searchResultProperty") or soup.select("article")
        for ad in ads:
            texto = ad.get_text(" ", strip=True)
            if any(z in texto.lower() for z in ZONAS_ALVO):
                try:
                    link_tag = ad.find("a")
                    if not link_tag: continue
                    link = link_tag.get("href", "")
                    if not link.startswith("http"): link = "https://casa.sapo.pt" + link
                    items.append({"Titulo": texto[:80], "PrecoRaw": texto, "Link": link, "Fonte": "SapoCasas"})
                except: continue
    except: pass
    return items

def run():
    print("🚀 INICIANDO PROCESSAMENTO")
    leads_raw = scraper_custojusto() + scraper_sapo() + scraper_kw_feira()
    
    if len(leads_raw) == 0:
        print("⚠️ Nenhum lead encontrado — enviando teste manual")
        leads_raw = [{"Titulo": "TESTE MANUAL", "PrecoRaw": "250000", "Link": "https://teste.pt", "Fonte": "DEBUG"}]

    print(f"📡 Total bruto: {len(leads_raw)}")
    hashes_existentes = carregar_hashes_existentes()

    for item in leads_raw:
        preco = limpar_preco(item["PrecoRaw"])
        score = calcular_score_pm5d(item["Titulo"], preco)
        
        print(f"🚨 STATUS → {item['Fonte']} | {preco}€ | Score {score}")

        h_str = f"{item['Link']}".strip().lower()
        h = hashlib.md5(h_str.encode()).hexdigest()
        
        if h in hashes_existentes:
            continue

        lead = {
            "Referencia": h[:8], "Titulo": item["Titulo"][:100], "Localidade": "Aveiro",
            "Preco": preco, "Link_Fonte": item["Link"], "Fonte": item["Fonte"],
            "Score_PM5D": score, "Prioridade": "ALTA" if score >= 4 else "MEDIA",
            "Hash": h, "Estado": "NOVO", "Decisao": "", "Notas": ""
        }
        
        ok = enviar_para_sheet(lead)
        print(f"📤 Resultado envio: {ok}")
        
        if ok:
            hashes_existentes.add(h)
            if score >= 4:
                enviar_telegram(f"💎 OPORTUNIDADE {score}/5\n{item['Titulo']}\nPreço: {preco}€\n{item['Link']}")

if __name__ == "__main__":
    run()
