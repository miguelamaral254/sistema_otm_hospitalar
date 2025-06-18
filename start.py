import sys
import os
from subprocess import run

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from src.loaders.raw_files_loader import baixar_e_descompactar
from src.data_pre_processing import processar_dados_pre_processamento
from data_processing import main as processar_dados
from ml_pipeline import main as execute_ml_pipeline


def run_raw_files_loader():
    print("Iniciando download de dados brutos...")
    baixar_e_descompactar()
    
def run_data_pre_processing():
    print("Iniciando pré-processamento de dados...")
    processar_dados_pre_processamento()

def run_ml_pipeline():
    print("Iniciando pipeline de Machine Learning...")
    execute_ml_pipeline()

def run_data_processing():
    print("Iniciando processamento de dados...")
    processar_dados()


def run():
    run_raw_files_loader()
    run_data_pre_processing()
    run_data_processing()
    run_ml_pipeline()
    


if __name__ == "__main__":
    run()