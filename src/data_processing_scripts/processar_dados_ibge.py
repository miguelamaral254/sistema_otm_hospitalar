import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

def processar_dados_ibge(spark):
    base_path = "src/data/cleaned"
    arquivo_ibge = "Populacao_Estados_Nordeste_2024.csv" 

    def ler_csv(nome_arquivo):
        file_path = os.path.join(base_path, nome_arquivo)
        if os.path.exists(file_path):
            return spark.read.option("header", True).option("sep", ",").csv(file_path)
        else:
            print(f"Erro: O arquivo {file_path} não existe!")
            return None

    df_ibge = ler_csv(arquivo_ibge)
    if df_ibge is None:
        print("Erro: Não foi possível carregar os dados do IBGE.")
        return

    df_ibge = df_ibge.toDF(*[col_name.strip().replace(' ', '_').lower() for col_name in df_ibge.columns])
    df_ibge = df_ibge.withColumn("populacao", col("populacao").cast("int")) \
                     .withColumn("ano", col("ano").cast("int"))

    output_path = "src/data/processed/populacao_estados_nordeste_2024.parquet"
    df_ibge.write.mode("overwrite").parquet(output_path)