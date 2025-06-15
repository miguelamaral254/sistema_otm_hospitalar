import pandas as pd
import os
from unidecode import unidecode

def clean_data(file_path, skip_rows=7, delimiter=';'):
    data = pd.read_csv(file_path, encoding='ISO-8859-1', sep=delimiter, skiprows=skip_rows)

    data = data[~data.iloc[:, 0].str.contains('Fonte:|Nota:|Morbidade|Cadastro Nacional|Sistema de|Período', na=False)]
    total_index = data[data.iloc[:, 0].str.contains('Total', na=False)].index
    if len(total_index) > 0:
        total_index = total_index[0]
        data = data.iloc[:total_index]
    
    if 'Região/UF' not in data.columns:

        if 'Região/Unidade' in data.columns:
            data = data.rename(columns={'Região/Unidade': 'UF'})
        elif 'Região Nordeste' in data.columns:
            data = data.rename(columns={'Região Nordeste': 'UF'})
        else:
            data = data.rename(columns={data.columns[0]: 'UF'}) 
    
    data = data.dropna(subset=['UF'])
    data = data.replace('-', 0)
    data.iloc[:, 1:] = data.iloc[:, 1:].apply(pd.to_numeric, errors='coerce')
    return data

def transform_data(data, year):
    transformed_data = []
    for _, row in data.iterrows():
        region_uf = row['UF']  
        year_data = row.iloc[1:].values 
        for month, value in zip(range(1, 13), year_data):
            transformed_data.append([region_uf, year, month, value])
    transformed_df = pd.DataFrame(transformed_data, columns=['UF', 'Ano', 'Mês', 'Valor'])
    return transformed_df

def remove_accents_and_rename(df):
    df.columns = [unidecode(col) for col in df.columns]
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].apply(lambda x: unidecode(x) if isinstance(x, str) else x)
    
    df['UF'] = df['UF'].apply(lambda x: str(x).replace('..', '').strip()) 
    df['Valor'] = df['Valor'].fillna(0).astype(int) 
    return df

raw_data_path = 'src/data/raw'
cleaned_data_path = 'src/data/cleaned'
if not os.path.exists(cleaned_data_path):
    os.makedirs(cleaned_data_path)

years = range(2020, 2025)
all_data = pd.DataFrame()

for year in years:
    file_name = f"OBITOS {year}.csv"
    file_path = os.path.join(raw_data_path, file_name)
    
    if os.path.exists(file_path):
        print(f"Processando o arquivo {year} analisdado do arquivo (referente ao csv {year})...")  
        year_data = clean_data(file_path)
        if year_data.empty:
            print(f"Warning: O arquivo {file_name} está vazio após limpeza. Pulando este arquivo.")
        else:
            transformed_data = transform_data(year_data, year)  
            all_data = pd.concat([all_data, transformed_data], ignore_index=True)
    else:
        print(f"Arquivo para o ano {year} não encontrado.")

if not all_data.empty:
    all_data = remove_accents_and_rename(all_data)
    output_file = os.path.join(cleaned_data_path, 'Morbidade_Hospitalar_Regiao_Nordeste_2020_2024_Limpo.csv')
    all_data.to_csv(output_file, index=False)
    print("Todos os arquivos foram processados e salvos com sucesso!")
else:
    print("Nenhum arquivo foi processado.")