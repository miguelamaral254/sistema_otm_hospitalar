import pandas as pd
import os
import re
from unidecode import unidecode

def clean_data(file_path, skip_rows=7, delimiter=';'):
    print(f"Lendo o arquivo: {file_path}")
    data = pd.read_csv(file_path, encoding='ISO-8859-1', sep=delimiter, skiprows=skip_rows)
    data = data[~data.iloc[:, 0].str.contains('Fonte:|Nota:|Morbidade|Cadastro Nacional|Sistema de|Período', na=False)]
    total_index = data[data.iloc[:, 0].str.contains('Total', na=False)].index
    if len(total_index) > 0:
        total_index = total_index[0]
        data = data.iloc[:total_index]
    if 'Região/UF' in data.columns:
        data = data.rename(columns={'Região/UF': 'UF'})
    elif data.columns[0] != 'UF':
        data = data.rename(columns={data.columns[0]: 'UF'})
    data = data.dropna(subset=['UF'])
    data = data.replace('-', 0)
    data.iloc[:, 1:] = data.iloc[:, 1:].apply(pd.to_numeric, errors='coerce')
    data['UF'] = data['UF'].apply(lambda x: unidecode(str(x)))
    return data

def transform_data(data, year):
    transformed_data = []
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
    def clean_team_name(name):
        name = re.sub(r'^\d+_', '', name)
        name = re.sub(r'[ \-]+', '_', name)
        name = re.sub(r'[^A-Za-z0-9_]', '', name)
        return name.upper()
    for _, row in data.iterrows():
        uf = row['UF']
        for i, val in enumerate(row[1:]):
            if i < len(team_keywords):
                team_name = clean_team_name(team_keywords[i])
                transformed_data.append([uf, year, team_name, val])
    return pd.DataFrame(transformed_data, columns=['UF', 'Ano', 'Tipo_de_Equipe', 'Valor'])

def process_files(raw_path, cleaned_path, start_year=2020, end_year=2024):
    if not os.path.exists(cleaned_path):
        os.makedirs(cleaned_path)
    all_data = pd.DataFrame()
    for year in range(start_year, end_year + 1):
        file_name = f'Equipes Saúde {year}.csv'
        file_path = os.path.join(raw_path, file_name)
        if os.path.exists(file_path):
            print(f"Iniciando processamento do arquivo para {year}...")
            data = clean_data(file_path)
            transformed = transform_data(data, year)
            all_data = pd.concat([all_data, transformed], ignore_index=True)
            print(f"Arquivo para {year} processado com sucesso.")
        else:
            print(f"Arquivo para {year} não encontrado.")
    output_file = os.path.join(cleaned_path, 'Equipes_Saude_2020_2024_Limpo.csv')
    all_data.to_csv(output_file, index=False)
    print(f"Arquivo salvo em: {output_file}")

if __name__ == "__main__":
    raw_data_path = 'src/data/raw'
    cleaned_data_path = 'src/data/cleaned'
    process_files(raw_data_path, cleaned_data_path)
