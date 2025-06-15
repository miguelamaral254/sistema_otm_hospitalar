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
        data = data.rename(columns={data.columns[0]: 'Região/UF'})
    
    data = data.replace('-', 0)
    data.iloc[:, 1:] = data.iloc[:, 1:].apply(pd.to_numeric, errors='coerce')
    data['Região/UF'] = data['Região/UF'].apply(lambda x: unidecode(str(x)).replace('..', '').strip())  # Removendo os '..'
    return data

def transform_data(data):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    transformed_data = []

    # Itera sobre cada linha para transformar os dados
    for _, row in data.iterrows():
        region_uf = row['Região/UF']
        
        # Para cada ano, monta os dados correspondentes aos meses
        year_data_dict = {'UF': region_uf}
        
        # Verifique se cada valor do mês está no intervalo correto
        for i in range(12):
            month_name = months[i]  # Nome do mês
            value = row.iloc[i + 1]  # Valor do mês correspondente
            
            # Adiciona o valor ao dicionário, convertendo para inteiro
            year_data_dict[month_name] = int(value) if pd.notna(value) else 0  # Garante que valores nulos sejam 0
        
        # Adiciona a linha de dados transformados
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
    file_name = f"Influenza Região Nordeste {year}.csv"
    file_path = os.path.join(raw_data_path, file_name)
    
    if os.path.exists(file_path):
        print(f"Processando o arquivo para o ano {year}...")
        year_data = clean_data(file_path)
        transformed_data = transform_data(year_data)
        transformed_data['Ano'] = year  # Garantir que o ano esteja na coluna Ano
        all_data = pd.concat([all_data, transformed_data], ignore_index=True)
    else:
        print(f"Arquivo para o ano {year} não encontrado.")

# Remover acentos
all_data_sem_acentos = remove_accents_from_df(all_data)
all_data_sem_acentos = all_data_sem_acentos.rename(columns={'Região/UF': 'UF'})

# Converter todas as colunas de meses para inteiros
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
for month in months:
    all_data_sem_acentos[month] = all_data_sem_acentos[month].astype(int)

# Salvar o arquivo final
output_file = os.path.join(cleaned_data_path, 'Influenza_Regiao_Nordeste_2020_2024_Limpo.csv')
all_data_sem_acentos.to_csv(output_file, index=False)

print(f"Arquivo 'Influenza_Regiao_Nordeste_2020_2024_Limpo.csv' salvo com sucesso.")