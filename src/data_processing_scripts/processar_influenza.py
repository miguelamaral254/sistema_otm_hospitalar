import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from shutil import rmtree

def processar_influenza(spark):
    base_path = "src/data/cleaned"
    arquivo_influenza = "Influenza_Regiao_Nordeste_2020_2024_Limpo.csv"
    output_path = "src/data/processed/influenza_hospitalar_processed.parquet"

    def ler_csv(nome_arquivo):
        file_path = os.path.join(base_path, nome_arquivo)
        if os.path.exists(file_path):
            return spark.read.option("header", True).option("sep", ",").csv(file_path)
        else:
            print(f"Erro: O arquivo {file_path} não existe!")
            return None

    def apagar_diretorio_parquet(path):
        if os.path.exists(path):
            rmtree(path)

    apagar_diretorio_parquet(output_path)

    df_influenza = ler_csv(arquivo_influenza)
    if df_influenza is None:
        print("Erro: Não foi possível carregar os dados de influenza.")
        return

    spark.catalog.clearCache()

    df_influenza = df_influenza.toDF(*[col_name.strip().replace(' ', '_').lower() for col_name in df_influenza.columns])

    df_influenza = df_influenza.withColumn("ano", col("ano").cast("int"))

    months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]

    for month in months:
        if month in df_influenza.columns:
            df_influenza = df_influenza.withColumn(month, col(month).cast("int"))

    df_influenza.write.mode("overwrite").parquet(output_path)