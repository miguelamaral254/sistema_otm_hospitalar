import os
import shutil
import kagglehub

def baixar_internacoes():
    """
    Função responsável por baixar o dataset de internações do Kaggle diretamente para o diretório 'data/raw'.
    Só baixa se os arquivos não existirem localmente.
    """
    try:
        raw_data_dir = "data/raw"
        os.makedirs(raw_data_dir, exist_ok=True)
        
        # Verificar se já temos os arquivos
        existing_files = set(os.listdir(raw_data_dir))
        expected_files = {f"RD2024{month:02d}.csv" for month in range(1, 13)}
        
        if existing_files.issuperset(expected_files):
            print("✅ Arquivos já existem em data/raw - pulando download")
            return

        # Baixar apenas se faltarem arquivos
        dataset_path = kagglehub.dataset_download("andersonfranca/sistema-de-informaes-hospitalares-sus")
        print(f"Dataset baixado para: {dataset_path}")
        
        moved_files = 0
        for file_name in os.listdir(dataset_path):
            if file_name.endswith(".csv"):
                src = os.path.join(dataset_path, file_name)
                dst = os.path.join(raw_data_dir, file_name)
                shutil.move(src, dst)
                print(f"Arquivo {file_name} movido para: {dst}")
                moved_files += 1

        if moved_files == 0:
            print("⚠️ Nenhum novo arquivo CSV encontrado no download")
        else:
            print(f"✅ {moved_files} arquivos novos movidos para {raw_data_dir}")
            
    except Exception as e:
        print(f"Erro ao baixar o dataset: {str(e)}")