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
        data = data.rename(columns={data.columns[0]: 'Região/UF'})
    
    data = data.replace('-', 0)
    data.iloc[:, 1:] = data.iloc[:, 1:].apply(pd.to_numeric, errors='coerce')
    data['Região/UF'] = data['Região/UF'].apply(lambda x: unidecode(str(x)).replace('..', '').strip())
    return data

def transform_data(data):
    months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    transformed_data = []

    for _, row in data.iterrows():
        region_uf = row['Região/UF']
        year_data_dict = {'uf': region_uf}
        
        for i in range(12):
            month_name = months[i]
            value = row.iloc[i + 1]
            year_data_dict[month_name] = int(value) if pd.notna(value) else 0
        
        transformed_data.append(year_data_dict)

    transformed_df = pd.DataFrame(transformed_data)
    return transformed_df

def remove_accents_from_df(df):
    df.columns = [unidecode(col) for col in df.columns]
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].apply(lambda x: unidecode(x) if isinstance(x, str) else x)
    return df

raw_data_path = 'src/data/raw'
cleaned_data_path = 'src/data/cleaned'
if not os.path.exists(cleaned_data_path):
    os.makedirs(cleaned_data_path)

all_data = pd.DataFrame()

for year in range(2020, 2025):
    file_name = f"Influenza Regiao Nordeste {year}.csv"
    file_path = os.path.join(raw_data_path, file_name)
    
    if os.path.exists(file_path):
        year_data = clean_data(file_path)
        transformed_data = transform_data(year_data)
        transformed_data['Ano'] = year
        all_data = pd.concat([all_data, transformed_data], ignore_index=True)

all_data_sem_acentos = remove_accents_from_df(all_data)
all_data_sem_acentos = all_data_sem_acentos.rename(columns={'Região/UF': 'uf'})

months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
for month in months:
    all_data_sem_acentos[month] = all_data_sem_acentos[month].astype(int)

output_file = os.path.join(cleaned_data_path, 'Influenza_Regiao_Nordeste_2020_2024_Limpo.csv')
all_data_sem_acentos.to_csv(output_file, index=False)

print(f"Arquivo 'Influenza_Regiao_Nordeste_2020_2024_Limpo.csv' salvo com sucesso.")