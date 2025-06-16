import gdown
import zipfile
import os

def baixar_e_descompactar():
    # URL do Google Drive
    url = 'https://drive.google.com/uc?export=download&id=1q0Bs4HpPWGVJu_ts0DJd5P_2aYxN1kzw'
    
    # Caminho onde o arquivo será baixado
    download_path = "src/data/raw/arquivo.zip"
    
    # Baixando o arquivo
    print(f"Baixando o arquivo de {url}...")
    gdown.download(url, download_path, quiet=False)
    print(f"Arquivo baixado com sucesso em {download_path}")

    # Descompactando o arquivo
    print("Descompactando o arquivo...")
    with zipfile.ZipFile(download_path, 'r') as zip_ref:
        zip_ref.extractall("src/data/raw")
    print("Descompactação concluída.")

if __name__ == "__main__":
    baixar_e_descompactar()