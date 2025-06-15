import pandas as pd
import os
from unidecode import unidecode
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

def clean_data(file_path, skip_rows=7, delimiter=';'):
    data = pd.read_csv(file_path, encoding='ISO-8859-1', sep=delimiter, skiprows=skip_rows)
    data = data[~data.iloc[:, 0].str.contains('Fonte:|Nota:|Morbidade|Cadastro Nacional|Sistema de|Período', na=False)]
    total_index = data[data.iloc[:, 0].str.contains('Total', na=False)].index
    if len(total_index) > 0:
        total_index = total_index[0]
        data = data.iloc[:total_index]
    if 'Região/UF' not in data.columns:
        data = data.rename(columns={data.columns[0]: 'Região/UF'})
    data = data.dropna(subset=['Região/UF'])
    data = data.replace('-', 0)
    data.iloc[:, 1:] = data.iloc[:, 1:].apply(pd.to_numeric, errors='coerce')
    return data

def transform_data(data, year):
    team_names = [
        "01_ESF_EQUIPE_DE_SAUDE_DA_FAMILIA", "02_ESFSB_M1_ESF_COM_SAUDE_BUCAL_M_I", 
        "03_ESFSB_M2_ESF_COM_SAUDE_BUCAL_M_II", "04_EACS_EQUIPE_DE_AGENTES_COMUNITARIOS_DE_SAUDE", 
        "05_EPEN_EQUIPE_DE_AT_SAUDE_SIST_PENITENCIARIO", "06_NASF1_NUCLEO_DE_APOIO_A_SAUDE_DA_FAMILIA_NASF_MODALIDADE_1", 
        "07_NASF2_NUCLEO_DE_APOIO_A_SAUDE_DA_FAMILIA_NASF_MODALIDADE_2", "08_EMSI_EQ_MULTIDISC_AT_BASICA_SAUDE_INDIGENA", 
        "10_EACSSB_M1_EQ_AGENTES_COMUNITARIOS_COM_SAUDE_BUCAL_MI", "11_EACSSB_M2_EQ_AGENTES_COMUNITARIOS_COM_SAUDE_BUCAL_MII", 
        "13_ESFRSB_MI_ESF_RIBEIRINHA_COM_SAUDE_BUCAL_MI", "16_EAB1_EQUIPE_DE_ATENCAO_BASICA_TIPO_I", 
        "19_EAB1SB_EQUIPE_DE_ATENCAO_BASICA_TIPO_I_COM_SAUDE_BUCAL", "22_EMAD_EQUIPE_MULTIDISCIPLINAR_DE_ATENCAO_DOMICILIAR_TIPO_I", 
        "23_EMAP_EQUIPE_MULTIDISCIPLINAR_DE_APOIO", "24_ESF1_ESTRATEGIA_DE_SAUDE_DA_FAMILIA_TIPO_I", 
        "25_ESF1SB_M1_ESF_TIPO_I_COM_SAUDE_BUCAL_MODALIDADE_I", "33_ESF4_ESTRATEGIA_DE_SAUDE_DA_FAMILIA_TIPO_IV", 
        "34_ESF4SB_M1_ESF_TIPO_IV_COM_SAUDE_BUCAL_MODALIDADE_I", "36_ESFTRANS_ESF_TRANSITORIA", 
        "37_ESFTRANSSB_M1_ESF_TRANSITORIA_COM_SAUDE_BUCAL_MI", "40_eCR_MI_EQUIPE_DOS_CONSULTORIOS_NA_RUA_MODALIDADE_I", 
        "41_eCR_MII_EQUIPE_DOS_CONSULTORIOS_NA_RUA_MODALIDADE_II", "42_eCR_MIII_EQUIPE_DOS_CONSULTORIOS_NA_RUA_MODALIDADE_III", 
        "45_NASF3_NUCLEO_DE_APOIO_A_SAUDE_DA_FAMILIA_NASF_MODALIDADE_3", "46_EMAD_EQUIPE_MULTIDISCIPLINAR_DE_ATENCAO_DOMICILIAR_TIPO_II", 
        "47_EAD_EQUIPE_DE_CUIDADOS_DOMICILIARES", "49_EAP", "50_EABP1_EQ_ATENCAO_BASICA_PRISIONAL_TIPO_I", 
        "51_EABP1SM_EQ_ATENCAO_BASICA_PRISIONAL_TIPO_I_C_SAUDE_MENTAL", "52_EABP2_EQ_ATENCAO_BASICA_PRISIONAL_TIPO_II", 
        "53_EABP2SM_EQ_ATENCAO_BASICA_PRISIONAL_TIPO_II_C_SAUDE_MENTAL", "54_EABP3_EQ_ATENCAO_BASICA_PRISIONAL_TIPO_III"
    ]
    transformed_data = []
    for _, row in data.iterrows():
        region_uf = row['Região/UF']
        for i, value in enumerate(row[1:]):
            if i < len(team_names):
                transformed_data.append([region_uf, year, team_names[i], value])
    transformed_df = pd.DataFrame(transformed_data, columns=['Região/UF', 'Ano', 'Tipo de Equipe', 'Valor'])
    return transformed_df

def remove_accents_and_rename(df):
    df.columns = [unidecode(col) for col in df.columns]
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].apply(lambda x: unidecode(x) if isinstance(x, str) else x)
    df = df.rename(columns={'Regiao/UF': 'UF'})
    return df

raw_data_path = 'src/data/raw'
cleaned_data_path = 'src/data/cleaned'
if not os.path.exists(cleaned_data_path):
    os.makedirs(cleaned_data_path)

all_data = pd.DataFrame()

for year in range(2020, 2025):
    file_name = f'Tipo de estabelecimento {year}.csv'
    file_path = os.path.join(raw_data_path, file_name)
    if os.path.exists(file_path):
        year_data = clean_data(file_path)
        transformed_data = transform_data(year_data, year)
        all_data = pd.concat([all_data, transformed_data], ignore_index=True)

all_data = remove_accents_and_rename(all_data)

output_file = os.path.join(cleaned_data_path, 'Tipo_de_Estabelecimento_2020_2024_Limpo.csv')
all_data.to_csv(output_file, index=False)
