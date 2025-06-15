import os
from pyspark.sql import SparkSession

def ler_dados_equipes():
    spark = SparkSession.builder \
        .appName("LerDadosEquipes") \
        .master("local[*]") \
        .config("spark.sql.shuffle.partitions", "8") \
        .getOrCreate()

    file_path = "src/data/processed/equipes_saude_processed.parquet"

    if os.path.exists(file_path):
        df = spark.read.parquet(file_path)
        df.printSchema()
        df.show(5)
    else:
        print(f"Erro: O arquivo {file_path} não existe!")

    spark.stop()

ler_dados_equipes()