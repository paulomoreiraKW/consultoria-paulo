import requests
import hashlib
import pandas as pd
import os
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

def limpar_preco(preco_raw):
    try:
        # Extrai apenas os números do texto (ex: "250 000 €" -> 250000)
        p = "".join(filter(str.isdigit, str(preco_raw)))
        return float(p) if p else 0
    except: return 0

def calcular_score_pm5d(titulo, preco):
    p = float(preco)
    if p <= 0: return 1
    t = titulo.lower()
    # Referências de Mercado Aveiro/Arredores 2026
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
    print("🔎 Scraping CustoJusto (Parsing Resiliente)...")
    url = "https://www.custojusto.pt/aveiro/imobiliario/moradias-venda"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    items = []
    try:
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        # Seletor robusto por atributo de link
        for ad in soup.select("a[href*='/imovel/'], a[href*='/moradia/']"):
            try:
                titulo = ad.get_text(strip=True)
                link = ad["href"]
                parent = ad.find_parent()
                texto = parent.get_text(" ", strip=True)
                
                if any(z in texto.lower() for z in ZONAS_ALVO):
                    items.append({
                        "Titulo": titulo, "Preco": texto, "Local": texto, 
                        "Link": link, "Fonte": "CustoJusto"
                    })
            except: continue
    except Exception as e: print(f"❌ Erro CustoJusto: {e}")
    return items

def scraper_sapo():
    print("🔎 Scraping Sapo Casas (Fallback Seguro)...")
    url = "https://casa.sapo.pt/venda/moradias/aveiro/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    items = []
    try:
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        # Seletor genéricoarticle/div focado em conteúdo
        for ad in soup.select("article, div"):
            texto = ad.get_text(" ", strip=True)
            if "€" in texto and any(z in texto.lower() for z in ZONAS_ALVO):
                try:
                    link_tag = ad.find("a")
                    if not link_tag: continue
                    link = link_tag.get("href", "")
                    if not link.startswith("http"): link = "https://casa.sapo.pt" + link
                    
                    items.append({
                        "Titulo": texto[:80], "Preco": texto, "Local": texto,
                        "Link": link, "Fonte": "SapoCasas"
                    })
                except: continue
    except Exception as e: print(f"❌ Erro Sapo: {e}")
    return items

def run():
    print("🚀 INICIANDO MULTI-SCRAPER PROFISSIONAL")
    leads_encontradas = scraper_custojusto() + scraper_sapo()
    print(f"📡 Total bruto encontrado: {len(leads_encontradas)}")
    
    hashes_existentes = carregar_hashes_existentes()
    print(f"🧠 Memória de Leads (Hashes): {len(hashes_existentes)}")

    for item in leads_encontradas:
        preco = limpar_preco(item["Preco"])
        score = calcular_score_pm5d(item["Titulo"], preco)
        
        # Geração de Hash por Conteúdo (Título + Preço) para evitar duplicados por URL tracking
        h_str = f"{item['Titulo']}{preco}".strip().lower()
        h = hashlib.md5(h_str.encode()).hexdigest()
        
        if h in hashes_existentes: continue
        if score < 2: continue # Filtro mínimo de relevância

        # Debug Útil no Log do GitHub
        print(f"➡️ {item['Fonte']} | {item['Titulo'][:40]}... | {preco}€ | Score: {score}")

        lead = {
            "Referencia": h[:8], "Titulo": item["Titulo"][:100], "Localidade": item["Local"][:50],
            "Preco": preco, "Link_Fonte": item["Link"], "Fonte": item["Fonte"],
            "Score_PM5D": score, "Prioridade": "ALTA" if score >= 4 else "MEDIA",
            "Hash": h, "Estado": "NOVO", "Decisao": "", "Notas": ""
        }
        
        if enviar_para_sheet(lead):
            if score >= 4:
                enviar_telegram(f"💎 OPORTUNIDADE {score}/5\n{item['Titulo'][:100]}\nPreço: {preco}€\nLink: {item['Link']}")
            hashes_existentes.add(h)

if __name__ == "__main__":
    run()
