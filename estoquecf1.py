import streamlit as st
import pandas as pd
from datetime import date

# Função para carregar os dados de um arquivo CSV
def carregar_dados(nome_arquivo, colunas):
    try:
        return pd.read_csv(nome_arquivo)
    except FileNotFoundError:
        return pd.DataFrame(columns=colunas)

# Função para salvar os dados em um arquivo CSV
def salvar_dados(df, nome_arquivo):
    df.to_csv(nome_arquivo, index=False)

# Carregando os dados iniciais
bandejas_compradas = carregar_dados('bandejas_compradas.csv', ['Código', 'Nome Variedade', 'Quantidade'])
semeio = carregar_dados('semeio.csv', ['Data', 'Código Variedade', 'Nome Variedade', 'Quantidade Semeada'])
plantios = carregar_dados('plantios.csv', ['Data', 'Código Variedade', 'Nome Variedade', 'Quantidade Vasos Plantados', 'Bandejas Usadas'])
descartes = carregar_dados('descartes.csv', ['Data', 'Tipo', 'Código Variedade', 'Nome Variedade', 'Quantidade Descartada'])

# Título do App
st.title('Cuca Fresca')

# Menu na Sidebar
st.sidebar.title("Menu de Controle")
menu = st.sidebar.radio("Selecione uma opção:", 
                        ('Controle de Bandejas Compradas', 
                         'Controle de Semeio', 
                         'Controle de Plantio', 
                         'Controle de Descarte'))

# Função para validar campos
def validar_campos(campos):
    for campo in campos:
        if not campo:
            st.error("Preencha todos os campos com informações válidas.")
            return False
    return True

def controle_bandejas():
    global bandejas_compradas  # Declaração da variável global

    st.header("Controle de Bandejas Compradas")

    # Inicializar variáveis locais para os campos
    codigo_bandeja = st.text_input('Código da Bandeja (6 números ou HBxxxx;)', "")
    nome_variedade = st.text_input('Nome da Variedade', "")
    quantidade_bandejas = st.number_input('Quantidade de Bandejas', min_value=1, value=1)

    if st.button('Adicionar Bandeja'):
        if not (codigo_bandeja and nome_variedade and quantidade_bandejas):
            st.warning("Preencha todos os campos com informações válidas.")
        else:
            nova_bandeja = pd.DataFrame({
                'Código': [codigo_bandeja],
                'Nome Variedade': [nome_variedade],
                'Quantidade': [quantidade_bandejas]
            })
            bandejas_compradas = pd.concat([bandejas_compradas, nova_bandeja], ignore_index=True)
            salvar_dados(bandejas_compradas, 'bandejas_compradas.csv')
            st.success(f'Bandeja de código {codigo_bandeja} adicionada com sucesso!')

    st.subheader("Bandejas Compradas")
    st.dataframe(bandejas_compradas)


# Controle de Semeio
def controle_semeio():
    global semeio  # Declaração da variável global

    st.header("Controle de Semeio")

    # Inputs para adicionar semeio
    data_semeio = st.date_input('Data do Semeio', value=date.today())
    codigo_variedade = st.text_input('Código das Bandejas (CF seguido de 4 dígitos)')
    nome_variedade = st.text_input('Nome da Variedade')
    quantidade_semeada = st.number_input('Quantidade Semeada (em bandejas)', min_value=1, step=1)

    if st.button('Adicionar Registro de Semeio'):
        if validar_campos([data_semeio, codigo_variedade, nome_variedade, quantidade_semeada]):
            if not codigo_variedade.startswith('CF') or not codigo_variedade[2:].isdigit() or len(codigo_variedade) != 6:
                st.error("O código deve iniciar com 'CF' seguido de 4 números.")
                return

            novo_semeio = pd.DataFrame({
                'Data': [data_semeio], 
                'Código Variedade': [codigo_variedade], 
                'Nome Variedade': [nome_variedade], 
                'Quantidade Semeada': [quantidade_semeada]
            })
            semeio = pd.concat([semeio, novo_semeio], ignore_index=True)
            salvar_dados(semeio, 'semeio.csv')
            st.success(f'Registro de semeio para a variedade {nome_variedade} adicionado com sucesso!')
            st.rerun()

    st.subheader("Histórico de Semeio")
    st.dataframe(semeio)

# Controle de Plantio
def controle_plantios():
    global plantios, bandejas_compradas

    st.header("Controle de Plantio")
    
    if bandejas_compradas.empty:
        st.warning("Nenhuma bandeja registrada. Por favor, registre bandejas primeiro no controle de bandejas compradas.")
        return

    nomes_variedades = bandejas_compradas['Nome Variedade'].unique().tolist()
    nome_variedade_plantio = st.selectbox('Nome da Variedade', nomes_variedades)
    
    if nome_variedade_plantio:
        codigos_variedade = bandejas_compradas[bandejas_compradas['Nome Variedade'] == nome_variedade_plantio]['Código'].tolist()
    else:
        codigos_variedade = []

    codigo_variedade_plantio = st.selectbox('Código da Variedade', codigos_variedade)
    quantidade_vasos_plantados = st.number_input('Quantidade de Vasos Plantados', min_value=1)
    quantidade_bandejas_usadas = st.number_input('Quantidade de Bandejas Usadas', min_value=1)

    if st.button('Adicionar Plantio'):
        if not (nome_variedade_plantio and codigo_variedade_plantio and quantidade_vasos_plantados and quantidade_bandejas_usadas):
            st.warning("Preencha todos os campos com informações válidas.")
        else:
            novo_plantio = pd.DataFrame({
                'Data': [date.today()],
                'Código Variedade': [codigo_variedade_plantio],
                'Nome Variedade': [nome_variedade_plantio],
                'Quantidade Vasos Plantados': [quantidade_vasos_plantados],
                'Bandejas Usadas': [quantidade_bandejas_usadas]
            })
            plantios = pd.concat([plantios, novo_plantio], ignore_index=True)

            index = bandejas_compradas[
                (bandejas_compradas['Código'] == codigo_variedade_plantio) & 
                (bandejas_compradas['Nome Variedade'] == nome_variedade_plantio)
            ].index

            if not index.empty:
                bandejas_compradas.loc[index, 'Quantidade'] -= quantidade_bandejas_usadas
                bandejas_compradas = bandejas_compradas[bandejas_compradas['Quantidade'] > 0]

            salvar_dados(plantios, 'plantios.csv')
            salvar_dados(bandejas_compradas, 'bandejas_compradas.csv')
            st.rerun()

            st.success(f"Plantio de {quantidade_vasos_plantados} vasos da variedade {nome_variedade_plantio} registrado com sucesso!")

    st.subheader("Histórico de Plantios")
    st.dataframe(plantios)

# Controle de Descarte
def controle_descarte():
    global descartes, bandejas_compradas

    st.header("Controle de Descarte")

    if bandejas_compradas.empty:
        st.warning("Nenhuma bandeja registrada. Por favor, registre bandejas primeiro no controle de bandejas compradas.")
        return

    nomes_variedades = bandejas_compradas['Nome Variedade'].unique().tolist()
    nome_variedade_descarte = st.selectbox('Nome da Variedade', nomes_variedades)

    if nome_variedade_descarte:
        codigos_variedade = bandejas_compradas[bandejas_compradas['Nome Variedade'] == nome_variedade_descarte]['Código'].tolist()
    else:
        codigos_variedade = []

    codigo_variedade_descarte = st.selectbox('Código da Variedade', codigos_variedade)
    tipo_descarte = st.selectbox('Tipo de Descarte', ['Bandejas', 'Vasos'])
    quantidade_descartada = st.number_input('Quantidade Descartada', min_value=1)

    if st.button('Adicionar Descarte'):
        if not (nome_variedade_descarte and codigo_variedade_descarte and tipo_descarte and quantidade_descartada):
            st.warning("Preencha todos os campos com informações válidas.")
        else:
            novo_descarte = pd.DataFrame({
                'Data': [date.today()],
                'Tipo': [tipo_descarte],
                'Código Variedade': [codigo_variedade_descarte],
                'Nome Variedade': [nome_variedade_descarte],
                'Quantidade Descartada': [quantidade_descartada]
            })
            descartes = pd.concat([descartes, novo_descarte], ignore_index=True)

            if tipo_descarte == 'Bandejas':
                index = bandejas_compradas[
                    (bandejas_compradas['Código'] == codigo_variedade_descarte) & 
                    (bandejas_compradas['Nome Variedade'] == nome_variedade_descarte)
                ].index

                if not index.empty:
                    bandejas_compradas.loc[index, 'Quantidade'] -= quantidade_descartada
                    bandejas_compradas = bandejas_compradas[bandejas_compradas['Quantidade'] > 0]

            salvar_dados(descartes, 'descartes.csv')
            salvar_dados(bandejas_compradas, 'bandejas_compradas.csv')
            st.rerun()

            st.success(f"{quantidade_descartada} {tipo_descarte} descartado(s) da variedade {nome_variedade_descarte} com sucesso!")

    st.subheader("Histórico de Descartes")
    st.dataframe(descartes)

# Seleção de Menu
if menu == 'Controle de Bandejas Compradas':
    controle_bandejas()
elif menu == 'Controle de Semeio':
    controle_semeio()
elif menu == 'Controle de Plantio':
    controle_plantios()
elif menu == 'Controle de Descarte':
    controle_descarte()
