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
    data.columns = [unidecode(col).replace(' ', '_') for col in data.columns]

    for col in data.select_dtypes(include=['object']).columns:
        data[col] = data[col].apply(lambda x: unidecode(x) if isinstance(x, str) else x)
    
    data['UF'] = data['UF'].apply(lambda x: str(x).replace('..', '').strip())
    return data

def transform_data(data, year):
    unit_columns = [
        "POSTO_DE_SAUDE", "CENTRO_DE_SAUDE_UNIDADE_BASICA", "POLICLINICA", "HOSPITAL_GERAL", "HOSPITAL_ESPECIALIZADO", 
        "UNIDADE_MISTA", "PRONTO_SOCORRO_GERAL", "PRONTO_SOCORRO_ESPECIALIZADO", "CONSULTORIO_ISOLADO", 
        "CLINICA_CENTRO_DE_ESPECIALIDADE", "UNIDADE_DE_APOIO_DIAGNOSE_E_TERAPIA_SADT_ISOLADO", 
        "UNIDADE_MOVEL_TERRESTRE", "UNIDADE_MOVEL_DE_NIVEL_PRE_HOSPITALAR_NA_AREA_DE_URGENCIA", "FARMACIA", 
        "UNIDADE_DE_VIGILANCIA_EM_SAUDE", "COOPERATIVA_OU_EMPRESA_DE_CESSAO_DE_TRABALHADORES_NA_SAUDE", 
        "CENTRO_DE_PARTO_NORMAL_ISOLADO", "HOSPITAL_DIA_ISOLADO", "CENTRAL_DE_REGULACAO_DE_SERVICOS_DE_SAUDE", 
        "LABORATORIO_CENTRAL_DE_SAUDE_PUBLICA_LACEN", "CENTRAL_DE_GESTAO_EM_SAUDE", 
        "CENTRO_DE_ATENCAO_HEMOTERAPIA_E_OU_HEMATOLOGICA", "CENTRO_DE_ATENCAO_PSICOSSOCIAL", 
        "CENTRO_DE_APOIO_A_SAUDE_DA_FAMILIA", "UNIDADE_DE_ATENCAO_A_SAUDE_INDIGENA", "PRONTO_ATENDIMENTO", 
        "POLO_ACADEMIA_DA_SAUDE", "TELESSAUDE", "CENTRAL_DE_REGULACAO_MEDICA_DAS_URGENCIAS", 
        "SERVICO_DE_ATENCAO_DOMICILIAR_ISOLADO_HOME_CARE", "UNIDADE_DE_ATENCAO_EM_REGIME_RESIDENCIAL", 
        "OFICINA_ORTOPEDICA", "LABORATORIO_DE_SAUDE_PUBLICA", "CENTRAL_DE_REGULACAO_DO_ACESSO", 
        "CENTRAL_DE_NOTIFICACAO_CAPTACAO_E_DISTRIB_DE_ORGAOS_ESTADUAL", 
        "POLO_DE_PREVENCAO_DE_DOENCAS_E_AGRAVOS_E_PROMOCAO_DA_SAUDE", "CENTRAL_DE_ABASTECIMENTO", "CENTRO_DE_IMUNIZACAO"
    ]
    
    transformed_data = []
    
    for _, row in data.iterrows():
        uf = row['UF']
        year_data = {'UF': uf, 'Ano': year}
        
        for i, val in enumerate(row[1:]):
            if i < len(unit_columns):
                unit_name = unit_columns[i]
                if isinstance(val, str) and val in ['-', 'nan', 'N/A', 'null']:
                    val = 0
                year_data[unit_name] = int(val) if pd.notna(val) else 0
        
        transformed_data.append(year_data)
    
    return pd.DataFrame(transformed_data)

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