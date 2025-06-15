
#from data_processing_scripts.processar_doses_vacinas import processar_doses_vacinas 
from data_processing_scripts.processar_equipes import processar_dados_equipes
from data_processing_scripts.processar_morbidade import processar_morbidade
from data_processing_scripts.processar_influenza import processar_influenza
from data_processing_scripts.processar_leitos_sus_nao_sus import processar_leitos_sus_nao_sus
from data_processing_scripts.processar_dados_ibge import processar_dados_ibge
from data_processing_scripts.processar_tipo_estabelecimento import processar_tipo_estabelecimento
def main():

    #processar_doses_vacinas()  
    #processar_dados_equipes()
    #processar_morbidade()
    #processar_influenza()
    #processar_leitos_sus_nao_sus()
    #processar_dados_ibge()
    processar_tipo_estabelecimento()
if __name__ == "__main__":
    main()