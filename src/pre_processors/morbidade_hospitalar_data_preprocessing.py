import pandas as pd
import os
from unidecode import unidecode

def clean_data(file_path, skip_rows=7, delimiter=';'):
    print(f"Lendo o arquivo: {file_path}")
    data = pd.read_csv(file_path, encoding='ISO-8859-1', sep=delimiter, skiprows=skip_rows)
    
    # Remover linhas com fontes e notas, que não contêm dados
    data = data[~data.iloc[:, 0].str.contains('Fonte:|Nota:|Morbidade|Cadastro Nacional|Sistema de|Período', na=False)]
    
    # Filtrando a linha de 'Total' e removendo
    total_index = data[data.iloc[:, 0].str.contains('Total', na=False)].index
    if len(total_index) > 0:
        total_index = total_index[0]
        data = data.iloc[:total_index]
    
    # Renomear a coluna para 'UF', se necessário
    if 'Região/UF' not in data.columns:
        if 'Região/Unidade' in data.columns:
            data = data.rename(columns={'Região/Unidade': 'UF'})
        elif 'Região Nordeste' in data.columns:
            data = data.rename(columns={'Região Nordeste': 'UF'})
        else:
            data = data.rename(columns={data.columns[0]: 'UF'})
    
    # Remover valores nulos na coluna 'UF'
    data = data.dropna(subset=['UF'])
    
    # Substituir valores '-' por 0
    data = data.replace('-', 0)
    
    # Limpeza de espaços nos nomes das colunas
    data.columns = data.columns.str.strip()
    
    # Convertendo os dados dos meses para numéricos
    for col in data.columns[1:]:
        data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0).astype(int)
    
    return data

def transform_data(data, year):
    months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    transformed_data = []

    # Transformando os dados para formato adequado
    for _, row in data.iterrows():
        region_uf = row['UF'].lower()  # Convertendo para minúsculo
        year_data_dict = {'uf': region_uf, 'ano': year}
        
        for i, month in enumerate(months):
            if i+1 < len(row): 
                value = row.iloc[i+1]
                year_data_dict[month] = int(value) if pd.notna(value) else 0
        
        transformed_data.append(year_data_dict)
    
    return pd.DataFrame(transformed_data)

def remove_accents_and_clean(df):
    # Remover acentos dos dados
    df.columns = [unidecode(col).lower() for col in df.columns]  # Convertendo colunas para minúsculo
    
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].apply(lambda x: unidecode(str(x)).lower() if pd.notna(x) else x)  # Convertendo valores textuais para minúsculo
    
    df['uf'] = df['uf'].str.replace('..', '').str.strip().str.lower()  # Limpando e convertendo UF para minúsculo
    
    return df

raw_data_path = 'src/data/raw'
cleaned_data_path = 'src/data/cleaned'

if not os.path.exists(cleaned_data_path):
    os.makedirs(cleaned_data_path)

years = range(2020, 2024)  # Ajuste para 2020 até 2023
all_data = pd.DataFrame()

# Processamento de cada ano
for year in years:
    file_name = f"mortalidade influenza mes {year}.csv"  # Corrigindo para o nome correto do arquivo
    file_path = os.path.join(raw_data_path, file_name)
    
    if os.path.exists(file_path):
        print(f"Processando o arquivo para o ano {year}...")
        try:
            year_data = clean_data(file_path)
            transformed_data = transform_data(year_data, year)
            all_data = pd.concat([all_data, transformed_data], ignore_index=True)
        except Exception as e:
            print(f"Erro ao processar {file_name}: {str(e)}")
    else:
        print(f"Arquivo para o ano {year} não encontrado.")

# Se houver dados, proceder com a limpeza e salvar o arquivo
if not all_data.empty:
    all_data = remove_accents_and_clean(all_data)
    months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    for month in months:
        if month in all_data.columns:
            all_data[month] = all_data[month].astype(int)
    
    # Salvando o arquivo final
    output_file = os.path.join(cleaned_data_path, 'mortalidade_influenza_nordeste_2020_2023_limpo.csv')  # Nome corrigido
    all_data.to_csv(output_file, index=False)
    print("Arquivo processado e salvo com sucesso!")
else:
    print("Nenhum dado foi processado - dataframe vazio.")