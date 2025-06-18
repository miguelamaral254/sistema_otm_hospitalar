import os
from pyspark.sql import SparkSession

def ler_parquet():
    spark = SparkSession.builder \
        .appName("LerDadosEquipes") \
        .master("local[*]") \
        .config("spark.sql.shuffle.partitions", "8") \
        .getOrCreate()

    #file_path = "src/data/processed/equipes_saude_processed.parquet"
    file_path = "src/data/processed/influenza_hospitalar_processed.parquet"
    #file_path = "src/data/processed/leitos_sus_nao_sus_processed.parquet"
    #file_path = "src/data/processed/populacao_estados_nordeste_2024.parquet"
    #file_path = "src/data/processed/populacao_estados_nordeste_2024.parquet"
    #file_path = "src/data/processed/morbidade_hospitalar_processed.parquet"
  #  file_path = "src/data/processed/tipo_estabelecimento_processed.parquet"
    
    
    

    if os.path.exists(file_path):
        df = spark.read.parquet(file_path)
        df.printSchema()
        df.show(100)
    else:
        print(f"Erro: O arquivo {file_path} não existe!")

    spark.stop()

ler_parquet()