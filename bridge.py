import requests
import json

WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwSSqhOlsJsZ6_QLzvkE8YUURy3Q47OEVb1l8OErjerILx_oAcU27jqP8Ju3q6jPI-O0g/exec"

def enviar_para_sheet(item):
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(WEBHOOK_URL, data=json.dumps(item), headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"⚠️ Erro Webhook: {response.status_code} - {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Falha na Bridge: {e}")
        return False
