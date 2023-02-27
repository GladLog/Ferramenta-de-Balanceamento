import sql
import pandas as pd
import Ferramenta_de_Balanceamento as fb

# Executar a conexao com o servidor SQLSERVER
conn = sql.retornar_conexao_sql(fb.text_ip,fb.text_database,fb.text_user,fb.text_password)

sql_BI1 = "SELECT * FROM BI_UNIDADES_DATA_AREA_PICKING"
df_BI1 = pd.read_sql(sql_BI1,conn)

sql_BI2 = "SELECT * FROM VW_BI_CAIXAS_INICIAM_ESTACAO_ATUAL WHERE AREA_PICKING_MAE = 'PRINCIPAL'"
df_BI2 = pd.read_sql(sql_BI2,conn)

sql_BI3 = "SELECT * FROM VW_BI_CAIXAS_INICIAM_ESTACAO_IDEAL WHERE AREA_PICKING_MAE = 'PRINCIPAL'"
df_BI3 = pd.read_sql(sql_BI3,conn)

sql_BI4 = "SELECT * FROM BASE_BALANCEAMENTO_ATUAL"
df_BI4 = pd.read_sql(sql_BI4,conn)

sql_BI5 = "SELECT * FROM BASE_BALANCEAMENTO_IDEAL"
df_BI5 = pd.read_sql(sql_BI5,conn)