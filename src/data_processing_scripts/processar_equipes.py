import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

def processar_dados_equipes():
    spark = SparkSession.builder \
        .appName("ProcessarDadosEquipes") \
        .master("local[*]") \
        .config("spark.sql.shuffle.partitions", "8") \
        .getOrCreate()

    base_path = "src/data/cleaned"
    arquivo_equipes = "Equipes_Saude_2020_2024_Limpo.csv"  

    def ler_csv(nome_arquivo):
        file_path = os.path.join(base_path, nome_arquivo)
        if os.path.exists(file_path):
            return spark.read.option("header", True).option("sep", ",").csv(file_path)  
        else:
            print(f"Erro: O arquivo {file_path} não existe!")
            return None

    df_equipes = ler_csv(arquivo_equipes)
    if df_equipes is None:
        print("Erro: Não foi possível carregar os dados das equipes.")
        return
    
    df_equipes = df_equipes.toDF(*[col_name.strip().replace(' ', '_').lower() for col_name in df_equipes.columns])
    df_equipes = df_equipes.withColumn("ano", col("ano").cast("int")) \
                           .withColumn("valor", col("valor").cast("double"))

    output_path = "src/data/processed/equipes_saude_processed.parquet" 
    df_equipes.write.mode("overwrite").parquet(output_path)
    
    spark.stop()

processar_dados_equipes()