import os
import requests
import pandas as pd


def download_ibge_data(url: str, headers: dict) -> list:
    print("🌍 Baixando dados populacionais do IBGE (SIDRA)...")
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"❌ Erro ao acessar dados do IBGE (SIDRA): {response.status_code}")

    data = response.json()
    if not data or len(data) < 2:
        raise ValueError("⚠️ Dados do IBGE (SIDRA) retornaram vazios ou incompletos.")
    print("✅ Dados do IBGE carregados com sucesso.")
    print("🔎 Prévia dos dados do IBGE:")
    print(data[1])
    return data


def filter_nordeste_data(data: list) -> list:
    cod_ufs_nordeste = {"21", "22", "23", "24", "25", "26", "27", "28", "29"}
    nordeste_data = [row for row in data[1:] if row.get("D1C") in cod_ufs_nordeste]
    print(f"📌 Estados do Nordeste encontrados: {len(nordeste_data)}")
    return nordeste_data


def create_dataframe(filtered_data: list) -> pd.DataFrame:
    df = pd.DataFrame(filtered_data)[["D1N", "V", "D3C"]]
    df = df.rename(columns={
        "D1N": "UF",
        "V": "Populacao",
        "D3C": "Ano"
    })
    df["Populacao"] = df["Populacao"].astype(int)
    df["Ano"] = df["Ano"].astype(int)
    return df


def save_to_csv(df: pd.DataFrame, output_path: str):
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"✅ Arquivo salvo com sucesso em: {output_path}")


def fetch_ibge_data():
    url = "https://apisidra.ibge.gov.br/values/t/6579/n3/all/v/9324/p/2024"
    headers = {
        "Accept": "application/json"
    }

    data = download_ibge_data(url, headers)
    filtered_data = filter_nordeste_data(data)
    df = create_dataframe(filtered_data)
    output_file = "src/data/cleaned/Populacao_Estados_Nordeste_2024.csv"
    save_to_csv(df, output_file)
    return df


if __name__ == "__main__":
    fetch_ibge_data()
