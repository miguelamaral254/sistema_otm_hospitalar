from pyspark.sql import SparkSession
from data_processing_scripts.processar_doses_vacinas import processar_doses_vacinas
from data_processing_scripts.processar_equipes import processar_dados_equipes
from data_processing_scripts.processar_morbidade import processar_morbidade
from data_processing_scripts.processar_influenza import processar_influenza
from data_processing_scripts.processar_leitos_sus_nao_sus import processar_leitos_sus_nao_sus
from data_processing_scripts.processar_dados_ibge import processar_dados_ibge
from data_processing_scripts.processar_tipo_estabelecimento import processar_tipo_estabelecimento

def limpar_cache(spark):
    spark.catalog.clearCache()

def main():
    spark = SparkSession.builder \
        .appName("ProcessamentoDadosHospitais") \
        .master("local[*]") \
        .config("spark.sql.shuffle.partitions", "1000") \
        .config("spark.sql.debug.maxToStringFields", "1000") \
        .getOrCreate()  

    print("Processamento iniciado...")
    print("Espere um momento...")

    processar_doses_vacinas(spark)
    print("processar_doses_vacinas() sucesso")
    limpar_cache(spark)

    processar_dados_equipes(spark)
    print("processar_dados_equipes() sucesso")
    limpar_cache(spark)

    processar_morbidade(spark)
    print("processar_morbidade() sucesso")
    limpar_cache(spark)

    processar_influenza(spark)
    print("processar_influenza() sucesso")
    limpar_cache(spark)

    processar_leitos_sus_nao_sus(spark)
    print("processar_leitos_sus_nao_sus() sucesso")
    limpar_cache(spark)

    processar_dados_ibge(spark)
    print("processar_dados_ibge() sucesso")
    limpar_cache(spark)

    processar_tipo_estabelecimento(spark)
    print("processar_tipo_estabelecimento() sucesso")
    limpar_cache(spark)

    spark.stop()

if __name__ == "__main__":
    main()