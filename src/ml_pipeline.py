from pyspark.sql import SparkSession
import pandas as pd

def load_data(input_path: str):
    # Inicializar SparkSession
    spark = SparkSession.builder \
        .appName("Read Internacoes Parquet") \
        .getOrCreate()
    
    # Lê o arquivo Parquet
    df_spark = spark.read.parquet(input_path)
    
    # Convertendo o Spark DataFrame para Pandas
    df = df_spark.toPandas()
    
    # Verifique se os dados no Pandas DataFrame são os mesmos do Spark DataFrame
    df_spark_values = df_spark.collect()  # Coleta os dados do Spark
    df_pandas_values = df.values  # Obtém os valores do DataFrame Pandas

    # Comparando os valores
    if (df_spark_values == df_pandas_values).all():
        print("Os dados são os mesmos após a conversão.")
    else:
        print("Os dados possuem diferenças. Verifique com mais detalhes.")
    
    # Exibe as primeiras linhas do DataFrame para verificar se foi carregado corretamente
    print(df.head())
    
    # Finaliza a sessão Spark
    spark.stop()
    
    return df

if __name__ == "__main__":
    # Caminho para o arquivo Parquet
    input_path = "data/processed/internacoes_processed.parquet"
    
    # Chama a função para carregar os dados
    df = load_data(input_path)