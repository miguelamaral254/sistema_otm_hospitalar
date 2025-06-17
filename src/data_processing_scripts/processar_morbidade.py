import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

def processar_morbidade(spark):
    base_path = "src/data/cleaned"
    arquivo_morbidade = "Morbidade_Hospitalar_Regiao_Nordeste_2020_2024_Limpo.csv"
    
    def ler_csv(nome_arquivo):
        file_path = os.path.join(base_path, nome_arquivo)
        if os.path.exists(file_path):
            return spark.read.option("header", "true").option("sep", ",").csv(file_path)
        else:
            print(f"Erro: O arquivo {file_path} não existe!")
            return None

    df_morbidade = ler_csv(arquivo_morbidade)
    
    if df_morbidade is None:
        print("Erro: Não foi possível carregar os dados de morbidade.")
        return

    df_morbidade = df_morbidade.toDF(*[col_name.strip().replace(' ', '_').lower() for col_name in df_morbidade.columns])
    df_morbidade = df_morbidade.withColumn("ano", col("ano").cast("int"))

    months_columns = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    df_morbidade = df_morbidade.select("uf", "ano", *months_columns)

    output_dir = "src/data/processed"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_path = os.path.join(output_dir, "morbidade_hospitalar_processed.parquet")
    
    df_morbidade.write.mode("overwrite").parquet(output_path)
    
    print(f"Processamento concluído. Arquivo salvo em: {output_path}")

if __name__ == "__main__":
    spark = SparkSession.builder.appName("Processar Mortalidade e Morbidade").getOrCreate()
    processar_morbidade(spark)