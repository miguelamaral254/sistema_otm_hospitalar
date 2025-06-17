import os
from dotenv import load_dotenv
from pyspark.sql.functions import col, monotonically_increasing_id
from pyspark.sql import SparkSession

load_dotenv()

def carregar_csv_para_postgres(spark, csv_path, table_name, db_url, db_properties):
    df = spark.read.option("header", "true").csv(csv_path)
    df = df.withColumn("ano", col("ano").cast("int"))

    # Adiciona a coluna de id auto incrementado (não auto incremento diretamente no PostgreSQL, mas um id único)
    df = df.withColumn("id", monotonically_increasing_id())

    # Grava a tabela no PostgreSQL, incluindo a coluna 'id' como chave primária
    df.write.jdbc(url=db_url, table=table_name, mode="overwrite", properties=db_properties)

    # Após carregar os dados, cria o índice de chave primária no PostgreSQL
    criar_chave_primaria(db_url, db_properties, table_name)

def criar_chave_primaria(db_url, db_properties, table_name):
    import psycopg2

    try:
        conn = psycopg2.connect(db_url, user=db_properties["user"], password=db_properties["password"])
        cursor = conn.cursor()

        # Adiciona a chave primária auto-incremento após o carregamento dos dados
        alter_table_query = f"""
        ALTER TABLE {table_name} 
        ADD COLUMN id SERIAL PRIMARY KEY;
        """

        cursor.execute(alter_table_query)
        conn.commit()

        cursor.close()
        conn.close()

        print(f"Chave primária 'id' adicionada à tabela {table_name} com sucesso.")

    except Exception as e:
        print(f"Erro ao adicionar chave primária na tabela {table_name}: {e}")

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