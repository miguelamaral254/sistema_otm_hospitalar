import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

def processar_doses_vacinas():
    spark = SparkSession.builder \
        .appName("ProcessarDosesVacinas") \
        .master("local[*]") \
        .config("spark.sql.shuffle.partitions", "8") \
        .getOrCreate()

    base_path = "src/data/cleaned"
    arquivo_doses = "Doses_vacinas_influenza_nordeste_2021_2022_Limpo.csv"

    def ler_csv(nome_arquivo):
        file_path = os.path.join(base_path, nome_arquivo)
        if os.path.exists(file_path):
            return spark.read.option("header", True).option("sep", ",").csv(file_path) 
        else:
            print(f"Erro: O arquivo {file_path} não existe!")
            return None

    df_doses = ler_csv(arquivo_doses)
    if df_doses is None:
        print("Erro: Não foi possível carregar os dados de doses de vacinas.")
        return

    #print(f"Colunas lidas: {df_doses.columns}")

    df_doses = df_doses.toDF(*[col_name.strip().replace(' ', '_').lower() for col_name in df_doses.columns])

    #print(f"Colunas normalizadas: {df_doses.columns}")

    df_doses = df_doses.withColumn("primeira_dose", col("primeira_dose").cast("double")) \
                       .withColumn("segunda_dose", col("segunda_dose").cast("double")) \
                       .withColumn("dose_unica", col("dose_unica").cast("double")) \
                       .withColumn("total_doses", col("total_doses").cast("double"))

    output_path = "src/data/processed/doses_vacinas_processed.parquet"
    df_doses.write.mode("overwrite").parquet(output_path)

    spark.stop()

processar_doses_vacinas()