import requests
print("📄 HTML preview:", r.text[:500])
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
    try:
        numeros = re.findall(r'\d+', str(texto_raw))
        if not numeros: return 0
        valor = "".join(numeros)
        return float(valor)
    except:
        return 0

def calcular_score_pm5d(titulo, preco):
    p = float(preco)
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
    url = "https://www.custojusto.pt/aveiro/imobiliario/moradias-venda"
    headers = {"User-Agent": "Mozilla/5.0"}
    items = []
    try:
        r = requests.get(url, headers=headers, timeout=15)

print("📄 HTML preview:", r.text[:500])  # 👈 AQUI

soup = BeautifulSoup(r.text, "html.parser")

links = soup.find_all("a")
print("🔗 Total links encontrados:", len(links))  # 👈 E AQUI

for ad in soup.select("a[href*='/imovel/'], a[href*='/moradia/']"):
            try:
                titulo = ad.get_text(strip=True)
                link = ad["href"]
                parent = ad.find_parent()
                texto = parent.get_text(" ", strip=True)
                if any(z in texto.lower() for z in ZONAS_ALVO):
                    items.append({"Titulo": titulo, "PrecoRaw": texto, "Link": link, "Fonte": "CustoJusto"})
            except: continue
    except: pass
    return items

def scraper_sapo():
    url = "https://casa.sapo.pt/venda/moradias/aveiro/"
    headers = {"User-Agent": "Mozilla/5.0"}
    items = []
    try:
        r = requests.get(url, headers=headers, timeout=15)

print("📄 SAPO HTML preview:", r.text[:500])  # 👈 DEBUG 1

soup = BeautifulSoup(r.text, "html.parser")

links = soup.find_all("a")
print("🔗 SAPO total links:", len(links))  # 👈 DEBUG 2

ads = soup.select("div.searchResultProperty") or soup.select("article")
print("📦 SAPO ads encontrados:", len(ads))  # 👈 DEBUG 3

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
    leads_raw = scraper_custojusto() + scraper_sapo()
    print(f"📡 Total bruto encontrado: {len(leads_raw)}")
    
    hashes_existentes = carregar_hashes_existentes()
    print(f"🧠 Memória: {len(hashes_existentes)} hashes")

    for item in leads_raw:
        preco = limpar_preco(item["PrecoRaw"])
        score = calcular_score_pm5d(item["Titulo"], preco)
        
        print(f"🚨 DEBUG → {item['Fonte']} | {item['Titulo'][:30]} | {preco}€ | Score {score}")

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
        print(f"📤 Resultado envio: {ok}")
        
        if ok:
            if score >= 4:
                enviar_telegram(f"💎 OPORTUNIDADE {score}/5\n{item['Titulo'][:100]}\nPreço: {preco}€\n{item['Link']}")
            hashes_existentes.add(h)

if __name__ == "__main__":
    run()
