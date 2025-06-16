import gdown
import zipfile
import os
import shutil

def baixar_e_descompactar():
    url = 'https://drive.google.com/uc?export=download&id=1q0Bs4HpPWGVJu_ts0DJd5P_2aYxN1kzw'
    download_path = "src/data/arquivo.zip"
    
    os.makedirs(os.path.dirname(download_path), exist_ok=True)
    
    print(f"Baixando o arquivo de {url}...")
    gdown.download(url, download_path, quiet=False)
    print(f"Arquivo baixado com sucesso em {download_path}")

    print("Descompactando o arquivo...")
    with zipfile.ZipFile(download_path, 'r') as zip_ref:
        zip_ref.extractall("src/data")
    print("Descompactação concluída.")

    if os.path.exists(download_path):
        os.remove(download_path)
        print(f"Arquivo {download_path} deletado com sucesso.")
    
    macosx_folder = os.path.join("src", "data", "__MACOSX")
    if os.path.exists(macosx_folder):
        shutil.rmtree(macosx_folder)
        print("Pasta __MACOSX deletada com sucesso.")

if __name__ == "__main__":
    baixar_e_descompactar()