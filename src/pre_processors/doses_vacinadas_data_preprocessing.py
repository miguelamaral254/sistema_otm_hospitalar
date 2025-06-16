import pandas as pd
import os
from unidecode import unidecode

def clean_data(file_path):
    data = pd.read_excel(file_path, sheet_name='Sheet1')
    # Seleciona as colunas necessárias
    data = data[['Unidade da Federação', '1ª Dose', '2ª Dose', 'Dose Única', 'Total']]
    # Renomeia a coluna 'Unidade da Federação' para 'UF'
    data = data.rename(columns={'Unidade da Federação': 'UF'})
    # Substitui valores '-' por 0
    data = data.replace('-', 0)
    # Remove valores nulos
    data = data.dropna()
    # Limpeza e normalização dos nomes das colunas
    data.columns = data.columns.str.strip()  # Remove espaços extras
    # Limpar acentos e caracteres especiais nos nomes das colunas
    data.columns = [unidecode(col) for col in data.columns]
    # Substituir espaços por underscore
    data.columns = [col.replace(' ', '_') for col in data.columns]
    # Renomear colunas para o formato desejado
    data = data.rename(columns={
        '1a_Dose': 'Primeira_Dose',
        '2a_Dose': 'Segunda_Dose',
        'Dose_Única': 'Dose_Unica',
        'Total': 'Total_Doses'
    })
    return data

def save_to_csv(data, output_path):
    data.to_csv(output_path, index=False)
    print(f"Arquivo salvo em: {output_path}")

def process_files(raw_data_path, cleaned_data_path, years):
    if not os.path.exists(cleaned_data_path):
        os.makedirs(cleaned_data_path)
    
    all_data = pd.DataFrame()

    for year in years:
        file_name = f'Doses_vacinas_influenza_nordeste_{year}.xlsx'
        input_file = os.path.join(raw_data_path, file_name)
        
        if os.path.exists(input_file):
            data = clean_data(input_file)
            data['Ano'] = year
            all_data = pd.concat([all_data, data], ignore_index=True)

    output_file = os.path.join(cleaned_data_path, 'Doses_vacinas_influenza_nordeste_2021_2022_Limpo.csv')
    save_to_csv(all_data, output_file)

if __name__ == "__main__":
    raw_data_path = 'src/data/raw'
    cleaned_data_path = 'src/data/cleaned'
    years = [2021, 2022]
    
    process_files(raw_data_path, cleaned_data_path, years)