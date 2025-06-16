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
    processar_doses_vacinas()
    print("processar_doses_vacinas() sucesso")
    limpar_cache(spark)

    processar_dados_equipes()
    print("processar_dados_equipes() sucesso")
    limpar_cache(spark)

    processar_morbidade()
    print("processar_morbidade() sucesso")
    limpar_cache(spark)

    processar_influenza()
    print("processar_influenza() sucesso")
    limpar_cache(spark)

    processar_leitos_sus_nao_sus()
    print("processar_leitos_sus_nao_sus() sucesso")
    limpar_cache(spark)

    processar_dados_ibge()
    print("processar_dados_ibge() sucesso")
    limpar_cache(spark)

    processar_tipo_estabelecimento()
    print("processar_tipo_estabelecimento() sucesso")
    limpar_cache(spark)

if __name__ == "__main__":
    main()