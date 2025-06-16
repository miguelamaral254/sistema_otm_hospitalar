import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from shutil import rmtree

def processar_influenza():
    # Criar a sessão Spark
    spark = SparkSession.builder \
        .appName("ProcessarInfluenza") \
        .master("local[*]") \
        .config("spark.sql.shuffle.partitions", "8") \
        .getOrCreate()

    base_path = "src/data/cleaned"
    arquivo_influenza = "Influenza_Regiao_Nordeste_2020_2024_Limpo.csv"
    output_path = "src/data/processed/influenza_hospitalar_processed.parquet"

    # Função para ler o CSV
    def ler_csv(nome_arquivo):
        file_path = os.path.join(base_path, nome_arquivo)
        if os.path.exists(file_path):
            return spark.read.option("header", True).option("sep", ",").csv(file_path)
        else:
            print(f"Erro: O arquivo {file_path} não existe!")
            return None

    # Função para apagar o diretório Parquet se ele existir
    def apagar_diretorio_parquet(path):
        if os.path.exists(path):
            print(f"Apagando diretório existente: {path}")
            rmtree(path)  # Apaga o diretório e seu conteúdo
        else:
            print(f"Nenhum diretório encontrado para excluir: {path}")

    # Apagar o diretório Parquet antes de processar os novos dados
    apagar_diretorio_parquet(output_path)

    # Ler os dados do arquivo CSV
    df_influenza = ler_csv(arquivo_influenza)
    if df_influenza is None:
        print("Erro: Não foi possível carregar os dados de influenza.")
        return

    # Verificar as colunas lidas
    print(f"Colunas lidas: {df_influenza.columns}")

    # Limpar qualquer cache existente
    spark.catalog.clearCache()  # Limpa todos os caches

    # Normalizar os nomes das colunas (converter para minúsculas e substituir espaços por underscores)
    df_influenza = df_influenza.toDF(*[col_name.strip().replace(' ', '_').lower() for col_name in df_influenza.columns])

    # Verificar novamente as colunas após a normalização
    print(f"Colunas após normalização: {df_influenza.columns}")

    # Garantir que o ano esteja no tipo adequado
    df_influenza = df_influenza.withColumn("ano", col("ano").cast("int"))

    # Converter os valores dos meses de janeiro a dezembro para inteiro
    months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]

    for month in months:
        if month in df_influenza.columns:  # Verifica se a coluna existe antes de fazer a conversão
            df_influenza = df_influenza.withColumn(month, col(month).cast("int"))
        else:
            print(f"Coluna {month} não encontrada no DataFrame!")

    # Escreva o DataFrame como um arquivo Parquet
    df_influenza.write.mode("overwrite").parquet(output_path)

    # Parar o Spark
    spark.stop()

# Executar a função de processamento
processar_influenza()