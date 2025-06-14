import pandas as pd
import os

# Função para limpar e reestruturar os dados
def clean_data(file_path, skip_rows=7, delimiter=';'):
    print(f"Lendo o arquivo: {file_path}")
    data = pd.read_csv(file_path, encoding='ISO-8859-1', sep=delimiter, skiprows=skip_rows)
    
    # Remover metadados
    data = data[~data.iloc[:, 0].str.contains('Fonte:|Nota:|Morbidade|Cadastro Nacional|Sistema de|Período', na=False)]
    
    # Remover linhas após "Total" (inclusive)
    total_index = data[data.iloc[:, 0].str.contains('Total', na=False)].index
    if len(total_index) > 0:
        total_index = total_index[0]
        data = data.iloc[:total_index]  # Excluir linha "Total" e tudo abaixo dela
    
    # Renomear a primeira coluna para 'Região/UF'
    if 'Região/UF' not in data.columns:
        data = data.rename(columns={data.columns[0]: 'Região/UF'})
    
    # Substituir valores '-' por 0
    data = data.replace('-', 0)
    
    # Converter todas as colunas numéricas para tipo numérico
    data.iloc[:, 1:] = data.iloc[:, 1:].apply(pd.to_numeric, errors='coerce')
    
    return data

def transform_data(data):
    # Criar uma nova coluna de "Ano"
    years = list(range(2020, 2025))
    # Inicializar uma lista vazia para armazenar os dados transformados
    transformed_data = []
    
    # Iterar sobre cada linha para transformar as colunas de cada mês em uma linha para cada ano
    for _, row in data.iterrows():
        region_uf = row['Região/UF']
        
        # Para cada ano, adicionar uma nova linha
        for i, year in enumerate(years):
            year_data = row.iloc[i+1:i+13].values  # Extrair os dados mensais do ano
            for month, value in zip(range(1, 13), year_data):
                transformed_data.append([region_uf, year, month, value])

    # Criar um DataFrame com os dados transformados
    transformed_df = pd.DataFrame(transformed_data, columns=['Região/UF', 'Ano', 'Mês', 'Valor'])
    
    return transformed_df

# Caminho de entrada
raw_data_path = 'src/data/raw'

# Caminho de saída
cleaned_data_path = 'src/data/cleaned'
if not os.path.exists(cleaned_data_path):
    os.makedirs(cleaned_data_path)

# Lista de anos para processar
years = range(2020, 2025)

# Inicializar um DataFrame vazio para juntar os dados de todos os anos
all_data = pd.DataFrame()

# Processar arquivos para cada ano
for year in years:
    # Gerar o caminho para o arquivo baseado no ano
    file_name = f"Influenza Região Nordeste {year}.csv"
    file_path = os.path.join(raw_data_path, file_name)
    
    # Verificar se o arquivo existe
    if os.path.exists(file_path):
        print(f"Processando o arquivo para o ano {year}...")
        
        # Limpar os dados do arquivo
        year_data = clean_data(file_path)
        
        # Transformar os dados
        transformed_data = transform_data(year_data)
        
        # Concatenar os dados de cada ano no DataFrame 'all_data'
        all_data = pd.concat([all_data, transformed_data], ignore_index=True)
    else:
        print(f"Arquivo para o ano {year} não encontrado.")

# Salvar os dados limpos e transformados em um único arquivo CSV
output_file = os.path.join(cleaned_data_path, 'Influenza_Regiao_Nordeste_2020_2024_Limpo.csv')
all_data.to_csv(output_file, index=False)

print(f"Arquivo 'Influenza_Regiao_Nordeste_2020_2024_Limpo.csv' salvo com sucesso.")