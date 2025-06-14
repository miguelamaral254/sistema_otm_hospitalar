import pandas as pd
import os
import re  # Para usar expressões regulares
from unidecode import unidecode  # Importa a função para remover acentos

# Função para limpar os dados
def clean_data(file_path, skip_rows=7, delimiter=';'):
    print(f"Lendo o arquivo: {file_path}")
    data = pd.read_csv(file_path, encoding='ISO-8859-1', sep=delimiter, skiprows=skip_rows)
    
    # Remover metadados
    data = data[~data.iloc[:, 0].str.contains('Fonte:|Nota:|Morbidade|Cadastro Nacional|Sistema de|Período', na=False)]
    
    # Remover linhas após "Total"
    total_index = data[data.iloc[:, 0].str.contains('Total', na=False)].index
    if len(total_index) > 0:
        total_index = total_index[0]
        data = data.iloc[:total_index]  # Excluir a linha "Total" e tudo após ela

    # Renomear a primeira coluna
    if 'Região/UF' not in data.columns:
        data = data.rename(columns={data.columns[0]: 'Região/UF'})
    
    data = data.dropna(subset=['Região/UF'])
    data = data.replace('-', 0)
    data.iloc[:, 1:] = data.iloc[:, 1:].apply(pd.to_numeric, errors='coerce')

    # Remover acentos das palavras
    data['Região/UF'] = data['Região/UF'].apply(lambda x: unidecode(str(x)))  # Remover acentos nas regiões
    
    return data

# Função para transformar os dados no formato desejado
def transform_data(data, year):
    # Criar uma nova lista para armazenar os dados transformados
    transformed_data = []
    
    # Definir os nomes das equipes com as palavras-chave, sem números
    team_keywords = [
        "ESF - EQUIPE DE SAUDE DA FAMILIA", "ESF COM SAUDE BUCAL", 
        "EACS - EQUIPE DE AGENTES COMUNITARIOS DE SAUDE", "NASF - NUCLEO DE APOIO A SAUDE", 
        "EMSI - EQ MULTIDISC AT BASICA SAUDE INDIGENA", "EACSSB - EQ AGENTES COMUNITARIOS COM SAUDE BUCAL", 
        "ESFRSB - ESF RIBEIRINHA COM SAUDE BUCAL", "EAB1 - EQUIPE DE ATENCAO BASICA", 
        "EMAD - EQUIPE MULTIDISCIPLINAR DE ATENCAO DOMICILIAR", "ESF1 - ESTRATEGIA DE SAUDE DA FAMILIA", 
        "ESF4 - ESTRATEGIA DE SAUDE DA FAMILIA", "ESFTRANS - ESF TRANSITORIA", "eCR - EQ DOS CONSULTORIOS NA RUA",
        "EAP - EQUIPE DE ATENCAO PRIMARIA", "EABP1 - EQ ATENCAO BASICA PRISIONAL TIPO I", 
        "EABP1SM - EQ ATENCAO BASICA PRISIONAL TIPO I C SAUDE MENTAL", "EABP2 - EQ ATENCAO BASICA PRISIONAL TIPO II", 
        "EABP2SM - EQ ATENCAO BASICA PRISIONAL TIPO II C SAUDE MENTAL", "EABP3 - EQ ATENCAO BASICA PRISIONAL TIPO III"
    ]
    
    # Iterar sobre cada linha e separar os valores das colunas de tipo de equipe
    for _, row in data.iterrows():
        region_uf = row['Região/UF']
        
        # Iterar sobre as colunas de cada tipo de equipe (depois da coluna 'Região/UF')
        for i, col in enumerate(row[1:]):  # Para cada tipo de equipe
            if i < len(team_keywords):  # Certificar que o índice não ultrapassa o número de nomes de equipes
                team_name = team_keywords[i]
                
                # Remover qualquer número e sublinhado no começo do nome da equipe
                team_name_cleaned = re.sub(r'^\d+_', '', team_name)  # Remove o número no início (ex: 46_EMAD -> EMAD)
                
                # Adicionar a equipe com o nome limpo, sem números
                transformed_data.append([region_uf, year, team_name_cleaned, col])  # Adicionar o nome da equipe sem número
    
    # Criar um DataFrame com os dados transformados
    transformed_df = pd.DataFrame(transformed_data, columns=['Região/UF', 'Ano', 'Tipo de Equipe', 'Valor'])
    
    return transformed_df

# Caminho de entrada
raw_data_path = 'src/data/raw'

# Caminho de saída
cleaned_data_path = 'src/data/cleaned'
if not os.path.exists(cleaned_data_path):
    os.makedirs(cleaned_data_path)

# Inicializar um DataFrame vazio para juntar os dados de todos os anos
all_data = pd.DataFrame()

# Processar arquivos para os anos de 2020 a 2024
for year in range(2020, 2025):
    # Definir o arquivo de entrada para cada ano
    file_name = f'Equipes Saúde {year}.csv'
    file_path = os.path.join(raw_data_path, file_name)
    
    if os.path.exists(file_path):
        print(f"Iniciando o processamento do arquivo para {year}...")
        # Processar os dados
        year_data = clean_data(file_path)

        # Transformar os dados para o formato desejado
        transformed_data = transform_data(year_data, year)

        # Concatenar os dados de cada ano no DataFrame 'all_data'
        all_data = pd.concat([all_data, transformed_data], ignore_index=True)

        print(f"Arquivo 'Equipes_Saude_{year}_Limpo.csv' processado e adicionado com sucesso.")
    else:
        print(f"O arquivo para o ano {year} não foi encontrado.")

# Salvar os dados limpos e transformados em um único arquivo CSV
output_file = os.path.join(cleaned_data_path, 'Equipes_Saude_2020_2024_Limpo.csv')
all_data.to_csv(output_file, index=False)

print(f"Arquivo 'Equipes_Saude_2020_2024_Limpo.csv' salvo com sucesso.")