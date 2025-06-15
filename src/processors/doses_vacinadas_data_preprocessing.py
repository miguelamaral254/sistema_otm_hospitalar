import pandas as pd
import os

def clean_data(file_path):
    data = pd.read_excel(file_path, sheet_name='Sheet1')
    data = data[['Unidade da Federação', '1ª Dose', '2ª Dose', 'Dose Única', 'Total']]
    data = data.rename(columns={'Unidade da Federação': 'UF'})
    data = data.replace('-', 0)
    data = data.dropna()
    data.columns = data.columns.str.strip()
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