import pandas as pd
import os
from unidecode import unidecode

def clean_data(file_path, skip_rows=7, delimiter=';'):
    print(f"Lendo o arquivo: {file_path}")
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
    data.columns = data.columns.str.strip()
    
    for col in data.columns[1:]:
        data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0).astype(int)
    
    return data

def transform_data(data, year):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    transformed_data = []

    for _, row in data.iterrows():
        region_uf = row['UF']
        year_data_dict = {'UF': region_uf, 'Ano': year}
        
        for i, month in enumerate(months):
            if i+1 < len(row): 
                value = row.iloc[i+1]
                year_data_dict[month] = int(value) if pd.notna(value) else 0
        
        transformed_data.append(year_data_dict)
    
    return pd.DataFrame(transformed_data)

def remove_accents_and_clean(df):
    df.columns = [unidecode(col) for col in df.columns]
    
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].apply(lambda x: unidecode(str(x)) if pd.notna(x) else x)
    
    df['UF'] = df['UF'].str.replace('..', '').str.strip()
    
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
        print(f"Processando o arquivo para o ano {year}...")
        try:
            year_data = clean_data(file_path)
            transformed_data = transform_data(year_data, year)
            all_data = pd.concat([all_data, transformed_data], ignore_index=True)
        except Exception as e:
            print(f"Erro ao processar {file_name}: {str(e)}")
    else:
        print(f"Arquivo para o ano {year} não encontrado.")

if not all_data.empty:
    all_data = remove_accents_and_clean(all_data)
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    for month in months:
        if month in all_data.columns:
            all_data[month] = all_data[month].astype(int)
    
    output_file = os.path.join(cleaned_data_path, 'Morbidade_Hospitalar_Regiao_Nordeste_2020_2024_Limpo.csv')
    all_data.to_csv(output_file, index=False)
    print("Arquivo processado e salvo com sucesso!")
else:
    print("Nenhum dado foi processado - dataframe vazio.")