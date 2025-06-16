# ml_pipeline.py
from pipeline_components.vacina_ml_pipeline import processar_vacinas

def main():
    print("Iniciando o pipeline de Machine Learning...")
    
    # Chama o pipeline específico de vacinas
    processar_vacinas()

if __name__ == "__main__":
    main()