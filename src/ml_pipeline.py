from pyspark.sql import SparkSession
from pipeline_components.vacina_ml_component import processar_vacinas
from pipeline_components.equipes_ml_component import processar_equipes
from pipeline_components.populacao_ml_component import processar_dados_populacao
from pipeline_components.influenza_ml_component import processar_influenza
from pipeline_components.leitos_ml_component import processar_leitos_sus_nao_sus
from pipeline_components.morbidade_ml_component import processar_morbidade
from pipeline_components.estabelecimento_ml_component import processar_tipo_estabelecimento

def criar_sessao_spark():
    spark = SparkSession.builder \
        .appName("PipelineMachineLearning") \
        .master("local[*]") \
        .config("spark.sql.shuffle.partitions", "100000") \
        .config("spark.sql.debug.maxToStringFields", "1000") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("ERROR")  
    return spark

def main():
    spark = criar_sessao_spark()
    
    print("Iniciando o pipeline de Machine Learning...")
    
    processar_vacinas(spark)
    processar_equipes(spark)
    processar_dados_populacao(spark)
    processar_influenza(spark)
    processar_leitos_sus_nao_sus(spark)
    processar_morbidade(spark)
    processar_tipo_estabelecimento(spark)
  
    spark.stop()

if __name__ == "__main__":
    main()