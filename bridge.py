import requests
import json

# Centralizamos o link aqui. Se um dia mudares a folha, só mudas aqui.
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwSSqhOlsJsZ6_QLzvkE8YUURy3Q47OEVb1l8OErjerILx_oAcU27jqP8Ju3q6jPI-O0g/exec"

def enviar_para_sheet(item):
    """Função isolada para não carregar o main.py"""
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(WEBHOOK_URL, data=json.dumps(item), headers=headers, timeout=10)
        return response.status_code == 200
    except:
        return False
