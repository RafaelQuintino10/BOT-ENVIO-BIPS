import psycopg2
from datetime import datetime
from time import sleep

def rotina():
    try:
        conexao = psycopg2.connect(
            host="localhost",
            database="bot_tips",
            user="postgres",
            password="fla1357912",
            port="5432"
        )
        cursor = conexao.cursor()

        cursor.execute("SELECT hora_inicio, hora_fim FROM tlg_bip LIMIT 1;")
        result = cursor.fetchone()
        # print(f"Horários encontrados: {result}")

        if result:
            hora_inicio = datetime.strptime(result[0].strip(), '%H:%M').time()
            hora_fim = datetime.strptime(result[1].strip(), '%H:%M').time()
            # print(f"Horários de início e fim respectivamente: {hora_inicio} // {hora_fim}")
            return hora_inicio, hora_fim

        else:
            raise ValueError("Nenhum horário encontrado na tabela.")

    except Exception as e:
        print("Erro ao buscar horários:", e)
        raise

    finally:
        if conexao:
            conexao.close()

# rotina()

try:
    cont = 0
    hora_inicio, hora_fim = rotina()
    horarios_atuais = (hora_inicio, hora_fim)  # Inicializa com valores nulos
    print("Iniciando monitoramento de horários...")
    while True:

        hora_inicio, hora_fim = rotina()

        if (hora_inicio,hora_fim) != horarios_atuais:
            horarios_atuais = (hora_inicio, hora_fim)
            print(f"Nova rotina definida - Horário de início: {hora_inicio} // Horário do fim: {hora_fim}\nIniciando disparos...")
            
         

        hora_atual = datetime.now().time() 
        
        if hora_inicio <= hora_atual <= hora_fim:
            cont += 1
            print(f"Contando {cont}")
            sleep(2)
        else:
            print(f"Fora do intervalo de {hora_inicio} e {hora_fim}. Aguardando...")
            cont = 0 

        sleep(10)  

except Exception as e:
    print(f"Erro no processo: {e}")
