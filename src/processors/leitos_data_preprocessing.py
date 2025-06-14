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
    if 'Região/Unidade da Federação' not in data.columns:
        data = data.rename(columns={data.columns[0]: 'Região/Unidade da Federação'})
    data.columns = data.columns.str.strip()
    data = data.replace('-', 0)
    return data

def transform_data(data):
    transformed_data = []
    for _, row in data.iterrows():
        region_uf = row['Região/Unidade da Federação']
        sus_value = row.iloc[1]
        nao_sus_value = row.iloc[2]
        transformed_data.append([region_uf, sus_value, nao_sus_value])
    transformed_df = pd.DataFrame(transformed_data, columns=['Região/Unidade da Federação', 'Quantidade_SUS', 'Quantidade_Nao_SUS'])
    return transformed_df

def remove_accents_and_rename(df):
    df.columns = [unidecode(col) for col in df.columns]
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].apply(lambda x: unidecode(x) if isinstance(x, str) else x)
    df = df.rename(columns={'Regiao/Unidade da Federacao': 'UF'})
    return df

raw_data_path = 'src/data/raw'
cleaned_data_path = 'src/data/cleaned'
if not os.path.exists(cleaned_data_path):
    os.makedirs(cleaned_data_path)

years = range(2020, 2025)
all_data = pd.DataFrame()

for year in years:
    file_name = f'LEITO SUS E NÃO SUS {year}.csv'
    file_path = os.path.join(raw_data_path, file_name)
    if os.path.exists(file_path):
        try:
            year_data = clean_data(file_path)
            transformed_data = transform_data(year_data)
            transformed_data['Ano'] = year
            all_data = pd.concat([all_data, transformed_data], ignore_index=True)
            print(f"Arquivo 'LEITO_SUS_E_NAO_SUS_{year}_Limpo.csv' processado com sucesso.")
        except Exception as e:
            print(f"O arquivo {file_name} teve erro: {e}")
    else:
        print(f"O arquivo {file_name} não foi encontrado.")

if not all_data.empty:
    all_data = remove_accents_and_rename(all_data)
    output_file = os.path.join(cleaned_data_path, 'Leitos_SUS_e_Nao_SUS_2020_2024_Limpo.csv')
    all_data.to_csv(output_file, index=False)
    print("Todos os arquivos foram processados e salvos com sucesso!")
else:
    print("Nenhum arquivo foi processado.")
