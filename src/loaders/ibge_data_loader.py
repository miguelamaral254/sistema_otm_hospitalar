import requests
import json

def fetch_ibge_data():
    print("🌍 Baixando dados populacionais do IBGE (SIDRA)...")

    url = "https://apisidra.ibge.gov.br/values/t/6579/n3/all/v/9324/p/2024"
    headers = {
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"❌ Erro ao acessar dados do IBGE (SIDRA): {response.status_code}")
    
    data = response.json()

    if not data or len(data) < 2:
        raise ValueError("⚠️ Dados do IBGE (SIDRA) retornaram vazios ou incompletos.")

    print("✅ Dados do IBGE carregados com sucesso.")
    print("🔎 Prévia dos dados do IBGE:")
    print(data[1])

    return data[1:]
