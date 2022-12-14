import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import pymssql
import plotly.graph_objects as go
import plotly.express as px
import sql
from datetime import date
import json
import dataframe as DF
import Ferramenta_de_Balanceamento as fb
import pickle
from pathlib import Path
import streamlit_authenticator as stauth
import generate_keys as gk


# Executar a conexao com o servidor SQLSERVER
conn = sql.retornar_conexao_sql(fb.text_ip,fb.text_port,fb.text_database,fb.text_user,fb.text_password)
st.sidebar.write(fb.text_ip)

#with st.sidebar:
selected = option_menu(
    menu_title= None,
    options=["Balanceamento","Indicadores", "Caixas por área", "Abastecimento"],
    orientation="horizontal",
)

if selected == "Balanceamento":
    st.title("PAGINA INICIAL")

    st.sidebar.header("PARÂMETROS:")
    Medida_Selecionada = st.sidebar.radio("Escolha uma medida:",["Unidades","Acessos"], index = 1, horizontal=True)

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
    # with st.sidebar.expander("PARÂMETROS ATUALIZAÇÃO DA BASE:"):
    #     form2 = st.form("Parametros_Base")
    #     with form2:
    #         st.selectbox("Filial:",['Filial'])
    #         st.date_input("Data Inicial:",date.today())
    #         st.date_input("Data Final:",date.today())
    #         submit_button2 = st.form_submit_button("Submit")
    #     if submit_button2:
    #         st.write("Os dados de filial e o periodo serão atualizados..")

    # Gráfico do Balanceamento entre áreas
    st.header("Balanceamento Entre Áreas")
    sql1 = "SELECT * FROM VW_BASE_ACESSOS_AREA_PICKING_MAE ORDER BY AREA_PICKING_MAE, AREA_PICKING"
    df1 = pd.read_sql(sql1,conn)
    # Fazendo o gráfico do balanceamento entre areas
    if Medida_Selecionada == "Acessos":
        fig = go.Figure(data=[
        go.Bar(name='Atual', x=df1["AREA_PICKING"], y=df1["ACESSOS_ATUAL"]),
        go.Bar(name='Ideal', x=df1["AREA_PICKING"], y=df1["ACESSOS_IDEAL"])])
        # Change the bar mode
        fig.update_layout(barmode='group',title = "ACESSOS")
        st.plotly_chart(fig)
    else:
        fig = go.Figure(data=[
        go.Bar(name='Atual', x=df1["AREA_PICKING"], y=df1["UNIDADES_ATUAL"]),
        go.Bar(name='Ideal', x=df1["AREA_PICKING"], y=df1["UNIDADES_IDEAL"])])
        # Change the bar mode
        fig.update_layout(barmode='group', title = "UNIDADES")
        st.plotly_chart(fig)

    # Gráfico do Balanceamento entre estações
    st.header("Balanceamento Estações")
    sql2 = "SELECT * FROM VW_BASE_ACESSOS_AREA_PICKING ORDER BY AREA_PICKING, ESTACAO"
    df2 = pd.read_sql(sql2,conn)
    Area_Selecionada = st.selectbox("Area_Picking:",df2["AREA_PICKING"].unique())
    df2 = df2[(df2["AREA_PICKING"] == Area_Selecionada)]

    #executar a select para pegar o desvio médio entre estaçoes
    sql4 = "SELECT CONVERT(DECIMAL(5,2),AVG(ABS(DESVIO_IDEAL_ACESSOS_ESTACAO_COM_DESVIADOR))) AS DESVIO_MEDIO FROM VW_BASE_ACESSOS_AREA_PICKING WHERE AREA_PICKING = '"+Area_Selecionada+"'"
    df4 = pd.read_sql(sql4,conn)
    st.write("Desvio médio entre estações: " + str(df4["DESVIO_MEDIO"].values[0]))

    # Fazendo o gráfico do balanceamento entre estaçoes
    st.subheader("Balanceamento entre Estações")
    if Medida_Selecionada == "Acessos":
        fig2 = go.Figure(data=[
        go.Bar(name='Atual', x=df2["ESTACAO"], y=df2["ACESSOS"]),
        go.Bar(name='Ideal', x=df2["ESTACAO"], y=df2["ACESSOS_IDEAL"]),
        go.Line(name='Média', x=df2["ESTACAO"], y=df2["IDEAL_ACESSOS_ESTACAO_COM_DESVIADOR"])])
        # Change the bar mode
        fig2.update_layout(barmode='group',title = "ACESSOS")
        st.plotly_chart(fig2)
    else:
        fig2 = go.Figure(data=[
        go.Bar(name='Atual', x=df2["ESTACAO"], y=df2["UNIDADES"]),
        go.Bar(name='Ideal', x=df2["ESTACAO"], y=df2["UNIDADES_IDEAL"]),
        go.Line(name='Média', x=df2["ESTACAO"], y=df2["IDEAL_UNIDADES_ESTACAO_COM_DESVIADOR"])])
        # Change the bar mode
        fig2.update_layout(barmode='group',title = "UNIDADES")
        st.plotly_chart(fig2)

    # Gráfico do Balanceamento dentro da estação
    st.subheader("Balanceamento Dentro das Estações")
    sql3 = "SELECT * FROM VW_BASE_ACESSOS_AREA_PICKING_POSICAO_ESTANTE ORDER BY POSICAO_ESTANTE"
    df3 = pd.read_sql(sql3,conn)
    df3 = df3[(df3["AREA_PICKING"] == Area_Selecionada)]
    # Fazendo o gráfico do balanceamento dentro da estação
    if Medida_Selecionada == "Acessos":
        fig3 = go.Figure(data=[
        go.Bar(name='Atual', x=df3["POSICAO_ESTANTE"], y=df3["ACESSOS"]),
        go.Bar(name='Ideal', x=df3["POSICAO_ESTANTE"], y=df3["ACESSOS_IDEAL"])])
        # Change the bar mode
        fig2.update_layout(barmode='group',title = "ACESSOS")
        st.plotly_chart(fig3)
    else:
        fig3 = go.Figure(data=[
        go.Bar(name='Atual', x=df3["POSICAO_ESTANTE"], y=df3["UNIDADES"]),
        go.Bar(name='Ideal', x=df3["POSICAO_ESTANTE"], y=df3["UNIDADES_IDEAL"])])
        # Change the bar mode
        fig2.update_layout(barmode='group',title = "UNIDADES")
        st.plotly_chart(fig3)
        
if selected == "Indicadores":
    # Carregar os dados do SQL
    df0 = DF.df_BI1
    df0["DATA"] = df0["DATA"].astype(str)
    df0["UNIDADES"] = df0["UNIDADES"].astype(int)
    # # Montar a tabela Pivot
    df_pivot_unidades = pd.pivot_table(df0,values="UNIDADES",index=["DATA"], columns=["AREA_PICKING"],aggfunc='sum' ,margins=True, margins_name="TOTAL")
    df_pivot_acessos = pd.pivot_table(df0,values="ACESSOS",index=["DATA"], columns=["AREA_PICKING"],aggfunc='sum' ,margins=True, margins_name="TOTAL")
    st.header("UNIDADES")
    st.dataframe(df_pivot_unidades)
    st.header("ACESSOS")
    st.dataframe(df_pivot_acessos)
    
if selected == "Caixas por área":
    st.header("Gráfico Caixas por área")
    df0 = DF.df_BI2
    fig = go.Figure(data=[
    go.Bar(name='Caixas', x=df0["ESTACAO"], y=df0["CX"]/df0["TT"]*100, text=(df0["CX"]/df0["TT"]*100).round(2))])
    # Change the bar mode
    fig.update_layout(barmode='group',title = "% Caixas que iniciam por estação atual")
    st.plotly_chart(fig)

if selected == "Caixas por área":
    df0 = DF.df_BI3
    fig = go.Figure(data=[
    go.Bar(name='Caixas', x=df0["ESTACAO"], y=df0["CX"]/df0["TT"]*100, text=(df0["CX"]/df0["TT"]*100).round(2))])
    # Change the bar mode
    fig.update_layout(barmode='group', title = "% Caixas que iniciam por estação ideal")
    st.plotly_chart(fig)

if selected == "Abastecimento":
    st.title("Relatório de abastecimento Atual")
    df0 = DF.df_BI4
    st.write(df0)

    st.title("Relatório abastecimento ideal")
    df5 = DF.df_BI5
    st.write(df5)
    
    
