import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

def processar_leitos_sus_nao_sus(spark):
    base_path = "src/data/cleaned"
    arquivo_leitos = "Leitos_SUS_e_Nao_SUS_2020_2024_Limpo.csv"

    def ler_csv(nome_arquivo):
        file_path = os.path.join(base_path, nome_arquivo)
        if os.path.exists(file_path):
            return spark.read.option("header", True).option("sep", ",").csv(file_path)
        else:
            print(f"Erro: O arquivo {file_path} não existe!")
            return None

    df_leitos = ler_csv(arquivo_leitos)
    if df_leitos is None:
        print("Erro: Não foi possível carregar os dados de leitos SUS e Não SUS.")
        return

    df_leitos = df_leitos.toDF(*[col_name.strip().replace(' ', '_').lower() for col_name in df_leitos.columns])

    df_leitos = df_leitos.withColumn("ano", col("ano").cast("int")) \
                         .withColumn("quantidade_sus", col("quantidade_sus").cast("int")) \
                         .withColumn("quantidade_nao_sus", col("quantidade_nao_sus").cast("int"))

    output_path = "src/data/processed/leitos_sus_nao_sus_processed.parquet"
    df_leitos.write.mode("overwrite").parquet(output_path)