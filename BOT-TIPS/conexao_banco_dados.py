import psycopg2
import sqlite3

# try:
#         # Conectar ao banco de dados
#         conexao = sqlite3.connect('bot_tips.db')
#         cursor = conexao.cursor()
        
#         cursor.execute('''
#     CREATE TABLE IF NOT EXISTS TLG_BIP (
#         ID_BIP INTEGER PRIMARY KEY AUTOINCREMENT,
#         COD_GRUPO INTEGER,
#         COD_SUPERVISAO INTEGER,
#         EMPR INTEGER,
#         CODFUN INTEGER,
#         POSTO TEXT,
#         MENSAGEM TEXT,
#         TOLERANCIA INTEGER,
#         RECORRENCIA INTEGER,
#         ABSTENSAO INTEGER,
#         HORA_INICIO TEXT,
#         HORA_FIM TEXT,
#         FLAG_ALTERA INTEGER,
#         HORA_ALTERA TIMESTAMP
#     )''')
#         conexao.commit()

#         print("Conexão estabelecida com sucesso")

# except Exception as error:
#     print(f"Erro ao conectar ao banco de dados: {error}")
# try:
#         # Conectar ao banco de dados
#         conexao = psycopg2.connect(
#             host="localhost",
#             database="bot_tips",
#             user="postgres",
#             password="fla1357912",
#             port="5432"
#         )
#         cursor = conexao.cursor()

#         print("Conexão estabelecida com sucesso")

    
#         cursor.execute('''
#             SELECT * FROM TLG_BIP WHERE FLAG_ALTERA = 0 
#             ''')
#         tlg_bip_dados = cursor.fetchall()
#         if tlg_bip_dados:
#             for dados in tlg_bip_dados:
#                 ID_BIP, COD_GRUPO, COD_SUPERVISAO, EMPR, CODFUN, POSTO, MENSAGEM, TOLERANCIA, RECORRENCIA, ABSTENSAO, HORA_INICIO, HORA_FIM, FLAG_ALTERA, HORA_ALTERA = dados
#                 print(MENSAGEM)


# except Exception as error:
#     print(f"Erro ao conectar ao banco de dados: {error}")


try:
        # Conectar ao banco de dados
        conexao = psycopg2.connect(
            host="localhost",
            database="bot_tips",
            user="postgres",
            password="fla1357912",
            port="5432"
        )
        cursor = conexao.cursor()

        print("Conexão estabelecida com sucesso")

    
        cursor.execute('''
        update tlg_bip set cont_abstensao = COALESCE(cont_abstensao, 0) + 1 where id_bip = 9
            ''')
        conexao.commit()
        print("Abstenção atualizada")
        


except Exception as error:
    print(f"Erro ao conectar ao banco de dados: {error}")


# try:
#         # Conectar ao banco de dados
#         conexao = sqlite3.connect('bot_tips.db')
#         cursor = conexao.cursor()
        
#         cursor.execute('''
#     CREATE TABLE IF NOT EXISTS TLG_BIPNOTIFIC ( 
#         ID_NOTIFICA    Serial 
#         ,ID_BIP         Integer 
#         ,COD_GRUPO     Numeric(20) 
#         ,COD_SUPERVISAO  Numeric(20) 
#         ,EMPR          Integer 
#         ,CODFUN        Integer 
#         ,MOTIVO      Text 
#         ,HORA_ENVIO    TimeStamp 
#         ,HORA_RETORNO    TimeStamp 
#         ,RET_SUPERVISAO  TimeStamp
#         )
#         ''')
#         conexao.commit()

#         print("Conexão estabelecida com sucesso")
# except Exception as error:
#     print(f"Erro ao conectar ao banco de dados: {error}")