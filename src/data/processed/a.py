import os
from pyspark.sql import SparkSession

def ler_parquet():
    # Cria a sessão Spark
    spark = SparkSession.builder \
        .appName("LerParquet") \
        .master("local[*]") \
        .config("spark.sql.shuffle.partitions", "8") \
        .getOrCreate()

    # Caminho para o arquivo parquet
    arquivo_parquet = "src/data/processed/doses_vacinas_processed.parquet"

    # Verifica se o arquivo existe
    if os.path.exists(arquivo_parquet):
        # Lê o arquivo parquet
        df_parquet = spark.read.parquet(arquivo_parquet)

        # Exibe o esquema (estrutura das colunas)
        df_parquet.printSchema()

        # Exibe as primeiras 5 linhas do DataFrame
        df_parquet.show(105)

        # Caso queira salvar novamente em formato CSV (opcional)
        # df_parquet.write.option("header", "true").csv("data/processed/doses_vacinas.csv")

    else:
        print(f"Erro: O arquivo {arquivo_parquet} não existe!")

    # Finaliza a sessão Spark
    spark.stop()

# Chama a função para ler o arquivo Parquet
ler_parquet()