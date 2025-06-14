import os
import subprocess

influenza_script = 'src/processors/influenza_data_preprocessing.py'
equipes_script = 'src/processors/equipes_data_preprocessing.py'
estabelecimentos_script = 'src/processors/estabelecimentos_data_preprocessing.py'
obitos_script = 'src/processors/obitos_data_preprocessing.py'
leitos_script = 'src/processors/leitos_data_preprocessing.py'

def run_script(script_path):
    try:
        subprocess.run(["python", script_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o script {script_path}: {e}")

cleaned_data_path = 'src/data/cleaned'
if not os.path.exists(cleaned_data_path):
    os.makedirs(cleaned_data_path)

#run_script(influenza_script)
#run_script(equipes_script)
#run_script(estabelecimentos_script)
#run_script(obitos_script)
run_script(leitos_script)

print("Todos os arquivos foram processados e salvos com sucesso!")