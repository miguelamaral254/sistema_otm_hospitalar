import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

def processar_tipo_estabelecimento(spark):
    base_path = "src/data/cleaned"
    arquivo_estabelecimento = "Tipo_de_Estabelecimento_2020_2024_Limpo.csv"

    def ler_csv(nome_arquivo):
        file_path = os.path.join(base_path, nome_arquivo)
        if os.path.exists(file_path):
            return spark.read.option("header", True).option("sep", ",").csv(file_path)
        else:
            print(f"Erro: O arquivo {file_path} não existe!")
            return None

    df_estabelecimento = ler_csv(arquivo_estabelecimento)
    if df_estabelecimento is None:
        print("Erro: Não foi possível carregar os dados do Tipo de Estabelecimento.")
        return

    df_estabelecimento = df_estabelecimento.toDF(*[col_name.strip().replace(' ', '_').lower() for col_name in df_estabelecimento.columns])
    df_estabelecimento = df_estabelecimento.withColumn("ano", col("ano").cast("int"))

    output_path = "src/data/processed/tipo_estabelecimento_processed.parquet"
    df_estabelecimento.write.mode("overwrite").parquet(output_path)