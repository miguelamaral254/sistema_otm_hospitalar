import os
import pandas as pd
from unidecode import unidecode

def clean_data(file_path, skip_rows=7, delimiter=';'):
    data = pd.read_csv(file_path, encoding='ISO-8859-1', sep=delimiter, skiprows=skip_rows)
    data = data[~data.iloc[:, 0].str.contains('Fonte:|Nota:|Morbidade|Cadastro Nacional|Sistema de|Período', na=False)]
    total_index = data[data.iloc[:, 0].str.contains('Total', na=False)].index
    if len(total_index) > 0:
        total_index = total_index[0]
        data = data.iloc[:total_index]
    if 'Região/Unidade da Federação' in data.columns:
        data = data.rename(columns={'Região/Unidade da Federação': 'UF'})
    elif data.columns[0] != 'UF':
        data = data.rename(columns={data.columns[0]: 'UF'})
    data = data.loc[:, ~data.columns.str.contains('^Total', regex=True)]
    data.columns = [unidecode(col) for col in data.columns]
    for col in data.select_dtypes(include=['object']).columns:
        data[col] = data[col].apply(lambda x: unidecode(x) if isinstance(x, str) else x)
    data['UF'] = data['UF'].apply(lambda x: str(x).replace('..', '').strip())
    return data

def transform_data(data, year):
    unit_columns = [
        "POSTO DE SAUDE", "CENTRO DE SAUDE/UNIDADE BASICA", "POLICLINICA", "HOSPITAL GERAL", "HOSPITAL ESPECIALIZADO", 
        "UNIDADE MISTA", "PRONTO SOCORRO GERAL", "PRONTO SOCORRO ESPECIALIZADO", "CONSULTORIO ISOLADO", 
        "CLINICA/CENTRO DE ESPECIALIDADE", "UNIDADE DE APOIO DIAGNOSE E TERAPIA (SADT ISOLADO)", 
        "UNIDADE MOVEL TERRESTRE", "UNIDADE MOVEL DE NIVEL PRE-HOSPITALAR NA AREA DE URGENCIA", "FARMACIA", 
        "UNIDADE DE VIGILANCIA EM SAUDE", "COOPERATIVA OU EMPRESA DE CESSAO DE TRABALHADORES NA SAUDE", 
        "CENTRO DE PARTO NORMAL - ISOLADO", "HOSPITAL/DIA - ISOLADO", "CENTRAL DE REGULACAO DE SERVICOS DE SAUDE", 
        "LABORATORIO CENTRAL DE SAUDE PUBLICA LACEN", "CENTRAL DE GESTAO EM SAUDE", 
        "CENTRO DE ATENCAO HEMOTERAPIA E OU HEMATOLOGICA", "CENTRO DE ATENCAO PSICOSSOCIAL", 
        "CENTRO DE APOIO A SAUDE DA FAMILIA", "UNIDADE DE ATENCAO A SAUDE INDIGENA", "PRONTO ATENDIMENTO", 
        "POLO ACADEMIA DA SAUDE", "TELESSAUDE", "CENTRAL DE REGULACAO MEDICA DAS URGENCIAS", 
        "SERVICO DE ATENCAO DOMICILIAR ISOLADO(HOME CARE)", "UNIDADE DE ATENCAO EM REGIME RESIDENCIAL", 
        "OFICINA ORTOPEDICA", "LABORATORIO DE SAUDE PUBLICA", "CENTRAL DE REGULACAO DO ACESSO", 
        "CENTRAL DE NOTIFICACAO,CAPTACAO E DISTRIB DE ORGAOS ESTADUAL", 
        "POLO DE PREVENCAO DE DOENCAS E AGRAVOS E PROMOCAO DA SAUDE", "CENTRAL DE ABASTECIMENTO", "CENTRO DE IMUNIZACAO"
    ]
    
    transformed_data = []
    
    for _, row in data.iterrows():
        uf = row['UF']
        for i, val in enumerate(row[1:]):
            if i < len(unit_columns):
                unit_name = unit_columns[i]
                if isinstance(val, str) and val in ['-', 'nan', 'N/A', 'null']:
                    val = 0
                transformed_data.append([uf, year, unit_name, int(val) if pd.notna(val) else 0])
    
    return pd.DataFrame(transformed_data, columns=['UF', 'Ano', 'Tipo_de_Estabelecimento', 'Valor'])

raw_data_path = 'src/data/raw'
cleaned_data_path = 'src/data/cleaned'
if not os.path.exists(cleaned_data_path):
    os.makedirs(cleaned_data_path)

all_data = pd.DataFrame()

for year in range(2020, 2025):
    file_name = f"Tipo de Estabelecimento {year}.csv"
    file_path = os.path.join(raw_data_path, file_name)
    
    if os.path.exists(file_path):
        print(f"Processando o arquivo {year}...")
        year_data = clean_data(file_path)
        if year_data.empty:
            print(f"Warning: O arquivo {file_name} está vazio após limpeza. Pulando este arquivo.")
        else:
            transformed_data = transform_data(year_data, year)
            all_data = pd.concat([all_data, transformed_data], ignore_index=True)
    else:
        print(f"Arquivo para o ano {year} não encontrado.")

if not all_data.empty:
    output_file = os.path.join(cleaned_data_path, 'Tipo_de_Estabelecimento_2020_2024_Limpo.csv')
    all_data.to_csv(output_file, index=False)
    print("Todos os arquivos foram processados e salvos com sucesso!")
else:
    print("Nenhum arquivo foi processado.")