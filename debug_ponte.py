import requests
import json

# URL que forneceste
url = "https://script.google.com/macros/s/AKfycbwSSqhOlsJsZ6_QLzvkE8YUURy3Q47OEVb1l8OErjerILx_oAcU27jqP8Ju3q6jPI-O0g/exec"

data = {
    "Referencia": "TESTE01",
    "Titulo": "IMÓVEL TESTE BRIDGE",
    "Localidade": "Aveiro",
    "Preco": 150000,
    "Link_Fonte": "https://google.com",
    "Fonte": "DEBUG",
    "Score_PM5D": 5,
    "Prioridade": "ALTA",
    "Hash": "debug_hash_001",
    "Estado": "NOVO"
}

print(f"🚀 Enviando teste para: {url}...")
try:
    r = requests.post(url, json=data, timeout=15)
    print(f"📊 STATUS HTTP: {r.status_code}")
    print(f"📩 RESPOSTA DO GOOGLE: {r.text}")
except Exception as e:
    print(f"❌ ERRO NA CONEXÃO: {e}")
