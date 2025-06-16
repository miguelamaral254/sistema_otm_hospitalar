import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

def processar_tipo_estabelecimento():
    spark = SparkSession.builder \
        .appName("ProcessarTipoEstabelecimento") \
        .master("local[*]") \
        .config("spark.sql.shuffle.partitions", "8") \
        .getOrCreate()

    # Reduzindo o nível de log para erros apenas
    spark.sparkContext.setLogLevel("ERROR")

    base_path = "src/data/cleaned"
    arquivo_estabelecimento = "Tipo_de_Estabelecimento_2020_2024_Limpo.csv"  # Nome do arquivo CSV

    def ler_csv(nome_arquivo):
        file_path = os.path.join(base_path, nome_arquivo)
        if os.path.exists(file_path):
            return spark.read.option("header", True).option("sep", ",").csv(file_path)
        else:
            print(f"Erro: O arquivo {file_path} não existe!")
            return None

    # Lê o arquivo do tipo de estabelecimento
    df_estabelecimento = ler_csv(arquivo_estabelecimento)
    if df_estabelecimento is None:
        print("Erro: Não foi possível carregar os dados do Tipo de Estabelecimento.")
        return

    # Normaliza os nomes das colunas
    df_estabelecimento = df_estabelecimento.toDF(*[col_name.strip().replace(' ', '_').lower() for col_name in df_estabelecimento.columns])

    # Converte os tipos das colunas
    df_estabelecimento = df_estabelecimento.withColumn("ano", col("ano").cast("int"))

    # Salva o dataframe no formato parquet
    output_path = "src/data/processed/tipo_estabelecimento_processed.parquet"
    df_estabelecimento.write.mode("overwrite").parquet(output_path)

    spark.stop()

processar_tipo_estabelecimento()