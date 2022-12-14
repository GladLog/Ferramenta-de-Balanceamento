import pickle
from pathlib import Path
import streamlit_authenticator as stauth
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sql
from PIL import Image
from datetime import date
import json
import generate_keys as gk
import yaml
import jwt


st.set_page_config(page_title="Ferramenta_de_Balanceamento")
# #CARREGAR HASHED PASSWORDS
# passwords = ["123", "123"]
# hashed_passwords = stauth.Hasher(passwords).generate()

# #with open('C:\Users\rocha\OneDrive\Documentos\GitHub\Balanceamento\Balanceamento\config.yaml') as file:
#     #config = yaml.load(file, Loader=yaml.SafeLoader)
#     #config = yaml.safe_load(file)

# file_path = Path(__file__).parent / "config.yaml"
# with file_path.open("r") as file:
#    #config = yaml.safe_load(file)
#    config = yaml.load(file, Loader=yaml.SafeLoader)

# authenticator = stauth.Authenticate(
#     config['credentials'],
#     config['cookie']['name'],
#     config['cookie']['key'],
#     config['cookie']['expiry_days'],
#     config['preauthorized']
# )
# name, authenticator_status, username = authenticator.login("Login", "main")
# st.write(authenticator_status)
# st.write(f'name {name}')


# if authenticator_status == False:
#     st.error("Usuário/senha incorretos")
# #if authenticator_status == None:
#    # st.warning("Por favor entre com seu usuário e senha")

# if authenticator_status or authenticator_status == None:
st.title("PAGINA INICIAL")
    
    #ABRINDO O ARQUIVO JSON
with open("dados_conexao.json") as conexao_json:
        dados_conexao = json.load(conexao_json)

    #FORMULÁRIO PARA APONTAR PARA O IP DO SERVIDOR
with st.sidebar.expander("CONFIGURAR CONEXÕES"):
        form_ip = st.form("IP do Servidor:")    
with form_ip:
        text_ip = st.text_input("IP do Servidor:")
        text_port = st.text_input("Porta:",dados_conexao['port'])
        text_database = st.text_input("Bando de Dados:",dados_conexao['database'])
        text_user = st.text_input("Usuário:",dados_conexao['user'])
        text_password = st.text_input("Senha:",dados_conexao['password'], type="password")
        ip_button = st.form_submit_button("Atualizar")
if ip_button:
        st.write(text_ip)

    # Executar a conexao com o servidor SQLSERVER
conn = sql.retornar_conexao_sql(text_ip,text_port,text_database,text_user,text_password)

    #class Dataframe:
        #def __init__(self, df):
            #self.df_BI1 = df

    # Verificar se tem Aframe
sql0 = "SELECT COUNT (DISTINCT AREA_PICKING) AS TOT_AREA_PICKING FROM ENDERECOS WHERE AREA_PICKING = 'AFRAME'"
df0 = pd.read_sql(sql0,conn)

if df0["TOT_AREA_PICKING"].values[0] == 1:
        # Formulário para atualizar os parâmetros do AFRAME
        with open("parametros_aframe.json") as conexao_parametros_aframe:
            parametros_aframe = json.load(conexao_parametros_aframe)
        with st.sidebar.expander("PARÂMETROS DO AFRAME:"):
            form = st.form("Parametros_Aframe")
            col1, col2 = form.columns(2)
        with col1:
            txt_custo_funcionario = st.text_input("Custo Funcionário:",parametros_aframe['custo_funcionario'])
            txt_produtividade_reposicao_canal = st.text_input("Prod. Rep. Canal:",parametros_aframe['produtividade_acessar_canal'])
            txt_total_canais_maior = st.text_input("Total Canais Maior:",parametros_aframe['quantidade_canais'])
            txt_altura_canal_maior = st.text_input("Alt Canal Maior:",parametros_aframe['tamanho_canal'])
            txt_produtividade_backuploop_canal_maior = st.text_input("Prod. Canal Maior:",parametros_aframe['produtividade_backuploop'])
        with col2:
            txt_produtividade_manual = st.text_input("Prod. Manual:",parametros_aframe['produtividade_manual'])
            txt_tempo_enchimento_canal = st.text_input("Ench. Canal:",parametros_aframe['tempo_encher_canal'])
            txt_total_canais_menor = st.text_input("Canais Menor:",parametros_aframe['quantidade_canais_2'])
            txt_altura_canal_menor = st.text_input("Alt Canal Menor:",parametros_aframe['tamanho_canal_2'])
            txt_produtividade_backuploop_canal_menor = st.text_input("Prod. Canal Menor:",parametros_aframe['produtividade_backuploop_2'])
            submit_button = form.form_submit_button("Submit")

        if submit_button:
            # Executar as procedure para atualizar as bases
            sp_processar_sugestao_balanceamento_ideal = 'PROCESSAR_SUGESTAO_BALANCEAMENTO_IDEAL'
            param_procedure = (txt_custo_funcionario, txt_produtividade_manual, txt_produtividade_reposicao_canal,txt_tempo_enchimento_canal,txt_total_canais_maior,
                                txt_altura_canal_maior,txt_produtividade_backuploop_canal_maior,txt_total_canais_menor,txt_altura_canal_menor,txt_produtividade_backuploop_canal_menor,)
            sql.executar_procedure(sp_processar_sugestao_balanceamento_ideal,param_procedure,conn)

    # Formulário para atualizar a base de Dados ( Filial e Período)
        with st.sidebar.expander("PARÂMETROS ATUALIZAÇÃO DA BASE:"):
            form2 = st.form("Parametros_Base")
        with form2:
            st.selectbox("Filial:",['Filial'])
            st.date_input("Data Inicial:",date.today())
            st.date_input("Data Final:",date.today())
            submit_button2 = st.form_submit_button("Submit")
    #if submit_button2:
            #st.write("Os dados de filial e o periodo serão atualizados..")
            #sql_BI1 = "SELECT * FROM VW_BI_UNIDADES_DATA_AREA_PICKING"
            #Dataframe.df_BI1 = pd.read_sql(sql_BI1,conn)
            #Dataframe(pd.read_sql(sql_BI1,conn))


      








