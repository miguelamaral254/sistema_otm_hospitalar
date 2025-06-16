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

def limpar_cache(spark):
    spark.catalog.clearCache()

def verificar_sucesso(statuses):
    if all(statuses):
        print("Machine Learning completo")
    else:
        print("Pipeline não foi completado com sucesso")

def main():
    spark = criar_sessao_spark()
    
    print("Iniciando o pipeline de Machine Learning...")

    statuses = []

    try:
        processar_vacinas(spark)
        print("processar_vacinas() sucesso")
        limpar_cache(spark)
        statuses.append(True)
    except Exception as e:
        print(f"processar_vacinas() falhou: {e}")
        statuses.append(False)

    try:
        processar_equipes(spark)
        print("processar_equipes() sucesso")
        limpar_cache(spark)
        statuses.append(True)
    except Exception as e:
        print(f"processar_equipes() falhou: {e}")
        statuses.append(False)

    try:
        processar_dados_populacao(spark)
        print("processar_dados_populacao() sucesso")
        limpar_cache(spark)
        statuses.append(True)
    except Exception as e:
        print(f"processar_dados_populacao() falhou: {e}")
        statuses.append(False)

    try:
        processar_influenza(spark)
        print("processar_influenza() sucesso")
        limpar_cache(spark)
        statuses.append(True)
    except Exception as e:
        print(f"processar_influenza() falhou: {e}")
        statuses.append(False)

    try:
        processar_leitos_sus_nao_sus(spark)
        print("processar_leitos_sus_nao_sus() sucesso")
        limpar_cache(spark)
        statuses.append(True)
    except Exception as e:
        print(f"processar_leitos_sus_nao_sus() falhou: {e}")
        statuses.append(False)

    try:
        processar_morbidade(spark)
        print("processar_morbidade() sucesso")
        limpar_cache(spark)
        statuses.append(True)
    except Exception as e:
        print(f"processar_morbidade() falhou: {e}")
        statuses.append(False)

    try:
        processar_tipo_estabelecimento(spark)
        print("processar_tipo_estabelecimento() sucesso")
        limpar_cache(spark)
        statuses.append(True)
    except Exception as e:
        print(f"processar_tipo_estabelecimento() falhou: {e}")
        statuses.append(False)

    verificar_sucesso(statuses)

    spark.stop()

if __name__ == "__main__":
    main()