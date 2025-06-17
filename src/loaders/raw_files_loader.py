import gdown
import zipfile
import os
import shutil

def baixar_e_descompactar():
    url = 'https://drive.google.com/uc?export=download&id=1hEztu3Tde0z_XC3uK688-tgrbx9-ryAp'  # Corrigido o link
    download_path = "src/data/arquivo.zip"
    
    os.makedirs(os.path.dirname(download_path), exist_ok=True)
    
    print(f"Baixando o arquivo de {url}...")
    gdown.download(url, download_path, quiet=False)
    print(f"Arquivo baixado com sucesso em {download_path}")

    print("Descompactando o arquivo...")
    try:
        with zipfile.ZipFile(download_path, 'r') as zip_ref:
            zip_ref.extractall("src/data")
        print("Descompactação concluída.")
    except zipfile.BadZipFile:
        print("Erro: O arquivo baixado não é um arquivo zip válido.")
        return

    if os.path.exists(download_path):
        os.remove(download_path)
        print(f"Arquivo {download_path} deletado com sucesso.")
    
    macosx_folder = os.path.join("src", "data", "__MACOSX")
    if os.path.exists(macosx_folder):
        shutil.rmtree(macosx_folder)
        print("Pasta __MACOSX deletada com sucesso.")

if __name__ == "__main__":
    baixar_e_descompactar()