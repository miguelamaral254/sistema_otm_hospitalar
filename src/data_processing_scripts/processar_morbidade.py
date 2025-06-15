import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

def processar_morbidade():
    spark = SparkSession.builder \
        .appName("ProcessarMorbidade") \
        .master("local[*]") \
        .config("spark.sql.shuffle.partitions", "8") \
        .getOrCreate()

    base_path = "src/data/cleaned"
    arquivo_morbidade = "Morbidade_Hospitalar_Regiao_Nordeste_2020_2024_Limpo.csv"

    def ler_csv(nome_arquivo):
        file_path = os.path.join(base_path, nome_arquivo)
        if os.path.exists(file_path):
            return spark.read.option("header", True).option("sep", ",").csv(file_path)
        else:
            print(f"Erro: O arquivo {file_path} não existe!")
            return None

    df_morbidade = ler_csv(arquivo_morbidade)
    if df_morbidade is None:
        print("Erro: Não foi possível carregar os dados de morbidade.")
        return

#    print(f"Colunas lidas: {df_morbidade.columns}")

    df_morbidade = df_morbidade.toDF(*[col_name.strip().replace(' ', '_').lower() for col_name in df_morbidade.columns])

#    print(f"Colunas normalizadas: {df_morbidade.columns}")

    df_morbidade = df_morbidade.withColumn("ano", col("ano").cast("int")) \
                               .withColumn("mes", col("mes").cast("int")) \
                               .withColumn("valor", col("valor").cast("int"))

    output_path = "src/data/processed/morbidade_hospitalar_processed.parquet"
    df_morbidade.write.mode("overwrite").parquet(output_path)

    spark.stop()

processar_morbidade()