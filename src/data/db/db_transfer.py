import os
from dotenv import load_dotenv
from pyspark.sql.functions import col
from pyspark.sql import SparkSession

load_dotenv()

def carregar_csv_para_postgres(spark, csv_path, table_name, db_url, db_properties):
    df = spark.read.option("header", "true").csv(csv_path)
    df = df.withColumn("ano", col("ano").cast("int"))
    df.write.jdbc(url=db_url, table=table_name, mode="overwrite", properties=db_properties)

def limpar_cache(spark):
    spark.catalog.clearCache()

def main(spark):
    arquivos_tabelas = [
        ("src/data/cleaned/Doses_vacinas_influenza_nordeste_2021_2022_Limpo.csv", "doses_vacinas_influenza"),
        ("src/data/cleaned/Equipes_Saude_2020_2024_Limpo.csv", "equipes_saude"),
        ("src/data/cleaned/Influenza_Regiao_Nordeste_2020_2024_Limpo.csv", "influenza_regiao_nordeste"),
        ("src/data/cleaned/Leitos_SUS_e_Nao_SUS_2020_2024_Limpo.csv", "leitos_sus_nao_sus"),
        ("src/data/cleaned/Morbidade_Hospitalar_Regiao_Nordeste_2020_2024_Limpo.csv", "morbidade_hospitalar"),
        ("src/data/cleaned/Populacao_Estados_Nordeste_2024.csv", "populacao_estados_nordeste"),
        ("src/data/cleaned/Tipo_de_Estabelecimento_2020_2024_Limpo.csv", "tipo_estabelecimento")
    ]
    
    db_url = os.getenv("DB_URL")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_driver = os.getenv("DB_DRIVER")
    postgres_jar_path = os.getenv("POSTGRES_JAR_PATH")

    db_properties = {
        "user": db_user,
        "password": db_password,
        "driver": db_driver
    }

    for csv_path, table_name in arquivos_tabelas:
        carregar_csv_para_postgres(spark, csv_path, table_name, db_url, db_properties)
        print(f"Dados carregados com sucesso na tabela: {table_name}")
        limpar_cache(spark)

if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("CSV to Postgres") \
        .master("local[*]") \
        .config("spark.sql.shuffle.partitions", "1000") \
        .config("spark.jars", os.getenv("POSTGRES_JAR_PATH")) \
        .getOrCreate()

    main(spark)