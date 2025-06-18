import os
import subprocess

# Caminhos dos scripts de pré-processamento
influenza_script = 'src/pre_processors/influenza_data_preprocessing.py'
equipes_script = 'src/pre_processors/equipes_data_preprocessing.py'
estabelecimentos_script = 'src/pre_processors/estabelecimentos_data_preprocessing.py'
morbidade_hosp_script = 'src/pre_processors/morbidade_hospitalar_data_preprocessing.py'
leitos_script = 'src/pre_processors/leitos_data_preprocessing.py'
vacinas_script = 'src/pre_processors/doses_vacinadas_data_preprocessing.py'
ibge_script = 'src/pre_processors/ibge_data_preprocessing.py'

# Função para executar os scripts de pré-processamento
def run_script(script_path):
    try:
        subprocess.run(["python", script_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o script {script_path}: {e}")

# Função para processar os dados de pré-processamento
def processar_dados_pre_processamento():
    # Caminho para salvar os arquivos processados
    cleaned_data_path = 'src/data/cleaned'
    if not os.path.exists(cleaned_data_path):
        os.makedirs(cleaned_data_path)

    # Executar os scripts de pré-processamento
    run_script(influenza_script)
    run_script(equipes_script)
    run_script(estabelecimentos_script)
    run_script(morbidade_hosp_script)
    run_script(leitos_script)
    run_script(vacinas_script)
    run_script(ibge_script)

    print("Todos os arquivos foram processados e salvos com sucesso!")

# Chamando a função para processar os dados
if __name__ == "__main__":
    processar_dados_pre_processamento()