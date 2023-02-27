import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import pymssql
import plotly.graph_objects as go
import plotly.express as px
import sql
import openpyxl
import json
#import Ferramenta_de_Balanceamento as fb


#ABRINDO O ARQUIVO JSON
with open("dados_conexao.json") as conexao_json:
    dados_conexao = json.load(conexao_json)

# Executar a conexao com o servidor SQLSERVER
conn = sql.retornar_conexao_sql(dados_conexao['server'],dados_conexao['database'],dados_conexao['user'],dados_conexao['password'])

#with st.sidebar:
selected = option_menu(
    menu_title= None,
    options=["Entre Áreas","Entre Estações","Dentro da Estação"],
    orientation="horizontal",
)

if selected == "Entre Áreas":
    st.title("BALANCEAMENTO ENTRE AREA PICKING")
    st.sidebar.header("PARÂMETROS:")

    # Criando um formulário para entrar com os parâmetros
    sql1 = "SELECT AREA_PICKING_MAE,COUNT( DISTINCT AREA_PICKING) AS TOTAL_AREA_PICKING	FROM ENDERECOS GROUP BY	AREA_PICKING_MAE ORDER BY AREA_PICKING_MAE"
    df1 = pd.read_sql(sql1,conn)
    df1 = df1[(df1["TOTAL_AREA_PICKING"] > 1)]
    if  not df1.empty:
        # Criando um formulário para entrar com os parâmetros
        form = st.sidebar.form("Parâmetros:")
        txt_area_picking = form.selectbox("Area Picking Mãe:",df1)
        txt_limite_interacoes = form.text_input("Limite de Interações:")
        submit_button = form.form_submit_button("Submit")
        if submit_button:
            # Executar a procedure de balanceamento entre estaçoes
            spbalanceamento_entre_area_picking = 'PROCESSAR_BALANCEAMENTO_ENTRE_AREA_PICKING_FINAL'
            param_procedure = (txt_area_picking, txt_limite_interacoes,)
            sql.executar_procedure(spbalanceamento_entre_area_picking,param_procedure,conn)

        #executar a select para pegar os dados do balancemaento entre areas
        sql2 = "SELECT * FROM VW_BASE_ACESSOS_AREA_PICKING_MAE_REALIZADO ORDER BY AREA_PICKING_MAE, AREA_PICKING"
        df2 = pd.read_sql(sql2,conn)
            
        # Fazendo o gráfico do balanceamento entre areas
        fig1 = go.Figure(data=[
        go.Bar(name='Atual', x=df2["AREA_PICKING"], y=df2["ACESSOS_ATUAL"],text=(df2["ACESSOS_ATUAL"]/sum(df2["ACESSOS_ATUAL"])*100).round(2)),
        go.Bar(name='Ideal', x=df2["AREA_PICKING"], y=df2["ACESSOS_IDEAL"],text=(df2["ACESSOS_IDEAL"]/sum(df2["ACESSOS_IDEAL"])*100).round(2))])
        # Change the bar mode
        fig1.update_layout(barmode='group',title = "ACESSOS")
        st.plotly_chart(fig1)

        #executar a select para pegar a relação de DE_PARA
        st.header("Relação de DE-PARA:")
        sql3 = "SELECT * FROM VW_PRODUTOS_DE_PARA ORDER BY ESTACAO_DE,ENDERECO_DE"
        df3 = pd.read_sql(sql3,conn)
        if df3.empty:
            st.write("Não há dados pra serem visualizados...")
        else:
            st.write(df3)
            button_exportar = st.button("Exportar")
            if button_exportar:
                # exportar o arquivo de-para para o formato xls
                writer = pd.ExcelWriter(r"C:\Users\rocha\OneDrive\Documentos\Python\de-para.xlsx", engine= "openpyxl")
                df3.to_excel(writer,sheet_name = 'DE_PARA')
                writer.save()
                writer.close()
                # exportar o arquivo de-para para o formato csv
                df3.to_csv(r"C:\Users\rocha\OneDrive\Documentos\Python\de-para.csv",index=False)
                st.write("Arquivo exportado com sucesso...")

        #EXECUTAR VW_GERAR_PRODUTOS_SEM_ENDERECOS
        st.header("Produtos sem endereços")
        sql5 = "SELECT * FROM VW_GERAR_PRODUTOS_SEM_ENDERECOS"
        df5 = pd.read_sql(sql5,conn)
        if df5.empty:
            st.write("Não há dados pra serem visualizados...")
        else:
            st.write(df5)
            button_exportar = st.button("Exportar1")
            if button_exportar:
                #EXPORTAR O ARQUIVO PARA FPRMATO XLS
                writer = pd.ExcelWriter(r"C:\Users\rocha\OneDrive\Documentos\Python\sem_end.xlsx", engine= "openpyxl")
                df5.to_excel(writer,sheet_name = "PROD_SEM_ENDERECO")
                writer.save()
                writer.close()
                #EXPORTAR O ARQUIVO PARA O FORMATO CSV
                df5.to_csv(r"C:\Users\rocha\OneDrive\Documentos\Python\sem_end.csv",index=False)
                st.write("Arquivo exportado com sucesso...")
    else:
        st.sidebar.subheader("Não se aplica para este CD...")
    conn.close()
if selected == "Entre Estações":
    st.title("BALANCEAMENTO ENTRE ESTAÇÕES")
    st.sidebar.header("PARÂMETROS:")

    # Criando um formulário para entrar com os parâmetros
    form = st.sidebar.form("Parâmetros:")
    sql4 = "SELECT DISTINCT AREA_PICKING FROM ENDERECOS ORDER BY AREA_PICKING"
    df4 = pd.read_sql(sql4,conn)
    txt_area_picking = form.selectbox("Area Picking:",df4)
    txt_desvio_medio = form.text_input("Desvio Médio:")
    txt_limite_interacoes = form.text_input("Limite de Interações:")
    submit_button = form.form_submit_button("Submit")
    if submit_button :
        # Executar a procedure de balanceamento entre estaçoes
        spbalanceamento_entre_estacoes = 'PROCESSAR_BALANCEAMENTO_ENTRE_ESTACOES_FINAL'
        param_procedure = (txt_area_picking, txt_desvio_medio, txt_limite_interacoes,)
        sql.executar_procedure(spbalanceamento_entre_estacoes,param_procedure,conn)

    #executar a select para pegar o desvio médio entre estaçoes
    sql1 = "SELECT CONVERT(DECIMAL(5,2),AVG(ABS(DESVIO_PERC))) AS DESVIO_MEDIO FROM VW_BASE_ACESSOS_RANKING"
    df1 = pd.read_sql(sql1,conn)
    st.write("Desvio médio entre estações: " + str(df1["DESVIO_MEDIO"].values[0]))

    st.header("Gráficos de Balanceamento Entre Estações")
    #executar a select para pegar os dados do desvio de balancemaento entre estaçoes
    sql2 = "SELECT AREA_PICKING,ESTACAO,ACESSOS,DESVIO_PERC,IDEAL_ACESSOS_ESTACAO_COM_DESVIADOR FROM VW_BASE_ACESSOS_RANKING ORDER BY ESTACAO"
    df2 = pd.read_sql(sql2,conn)
    # Fazendo o gráfico 
    fig1 = go.Figure(data=[
    go.Bar(name='Atual', x=df2["ESTACAO"], y=df2["ACESSOS"]),
    go.Line(name='Ideal', x=df2["ESTACAO"], y=df2["IDEAL_ACESSOS_ESTACAO_COM_DESVIADOR"])])
    # Change the bar mode
    fig1.update_layout(barmode='group')
    st.plotly_chart(fig1)

    fig2 = px.bar(df2, x="ESTACAO", y="DESVIO_PERC")
    st.plotly_chart(fig2)

    st.header("Relação de DE-PARA:")
    #executar a select para pegar a relação de DE_PARA
    sql3 = "SELECT * FROM VW_PRODUTOS_DE_PARA ORDER BY ESTACAO_DE,ENDERECO_DE"
    df3 = pd.read_sql(sql3,conn)
    if df3.empty:
        st.write("Não há dados pra serem visualizados...")
    else:
        st.write(df3)
        button_exportar = st.button("Exportar")
        if button_exportar:
            # exportar o arquivo de-para para o formato xls
            writer = pd.ExcelWriter(r"C:\Users\rocha\OneDrive\Documentos\Python\de-para.xlsx", engine= "openpyxl")
            df3.to_excel(writer,sheet_name = 'DE_PARA')
            writer.save()
            writer.close()
            # exportar o arquivo de-para para o formato csv
            df3.to_csv(r"C:\Users\rocha\OneDrive\Documentos\Python\de-para.csv",index=False)
            st.write("Arquivo exportado com sucesso...")

    conn.close()
if selected == "Dentro da Estação":
    st.title("BALANCEAMENTO DENTRO DAS ESTAÇÕES")
    st.sidebar.header("PARÂMETROS:")

    # Criando um formulário para entrar com os parâmetros
    form = st.sidebar.form("Parâmetros:")
    sql4 = "SELECT DISTINCT AREA_PICKING FROM ENDERECOS ORDER BY AREA_PICKING"
    df4 = pd.read_sql(sql4,conn)
    txt_area_picking = form.selectbox("Area Picking:",df4)
    txt_limite_interacoes = form.text_input("Limite de Interações:")
    submit_button = form.form_submit_button("Submit")
    if submit_button:
        # Executar a procedure de balanceamento entre estaçoes
        spbalanceamento_dentro_estacoes = 'PROCESSAR_BALANCEAMENTO_DENTRO_ESTACAO_FINAL'
        param_procedure = (txt_area_picking, txt_limite_interacoes,)
        sql.executar_procedure(spbalanceamento_dentro_estacoes,param_procedure,conn)

    #executar a select para pegar o desvio médio entre estaçoes
    sql1 = "SELECT CONVERT(DECIMAL(5,2),AVG(ABS(DESVIO_PERC))) AS DESVIO_MEDIO FROM VW_BASE_ACESSOS_RANKING"
    df1 = pd.read_sql(sql1,conn)
    st.write("Desvio médio entre estações: " + str(df1["DESVIO_MEDIO"].values[0]))

    st.header("Gráfico de balanceamento dentro da Estação")
    #executar a select para pegar a informação de Acessos por Posicao Estante
    sql2 = "SELECT AREA_PICKING,POSICAO_ESTANTE,ACESSOS, ACESSOS_IDEAL FROM VW_BASE_ACESSOS_AREA_PICKING_POSICAO_ESTANTE_REALIZADA ORDER BY POSICAO_ESTANTE"
    df2 = pd.read_sql(sql2,conn)
    df2 = df2[(df2["AREA_PICKING"] == txt_area_picking)]
    # Fazendo o gráfico 
    fig = go.Figure(data=[
    go.Bar(name='Atual', x=df2["POSICAO_ESTANTE"], y=df2["ACESSOS"]),
    go.Bar(name='Ideal', x=df2["POSICAO_ESTANTE"], y=df2["ACESSOS_IDEAL"])])
    # Change the bar mode
    fig.update_layout(barmode='group')
    st.plotly_chart(fig)

    st.header("Relação de DE-PARA:")
    #executar a select para pegar a relação de DE_PARA
    sql3 = "SELECT * FROM VW_PRODUTOS_DE_PARA ORDER BY ESTACAO_DE,ENDERECO_DE"
    df3 = pd.read_sql(sql3,conn)
    if df3.empty:
        st.write("Não há dados pra serem visualizados...")
    else:
        st.write(df3)
        button_exportar = st.button("Exportar")
        if button_exportar:
            # exportar o arquivo de-para para o formato xls
            writer = pd.ExcelWriter(r"C:\Users\rocha\OneDrive\Documentos\Python\de-para.xlsx", engine= "openpyxl")
            df3.to_excel(writer,sheet_name = 'DE_PARA')
            writer.save()
            writer.close()
            # exportar o arquivo de-para para o formato csv
            df3.to_csv(r"C:\Users\rocha\OneDrive\Documentos\Python\de-para.csv",index=False)
            st.write("Arquivo exportado com sucesso...")

    conn.close()