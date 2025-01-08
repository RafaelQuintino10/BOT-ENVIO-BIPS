import asyncio
import datetime
import logging
import sys
import psycopg2
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ContextTypes

active_chats = {}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),  
        logging.FileHandler("bot_visao_bips.log", encoding="utf-8"),  
    ],
)

def print(*args, **kwargs):
    logging.info(" ".join(map(str, args)))


async def conexao_banco():
    conexao = psycopg2.connect(
            host="localhost",
            database="bot_tips",
            user="postgres",
            password="fla1357912",
            port="5432"
        )
    return conexao 

async def rotina_disparos():
    try:
        conexao = await conexao_banco()
        cursor = conexao.cursor()

        cursor.execute("SELECT hora_inicio, hora_fim FROM tlg_bip LIMIT 1;")
        result = cursor.fetchone()
        # print(f"Horários encontrados: {result}")

        if result:
            hora_inicio = datetime.datetime.strptime(result[0].strip(), '%H:%M').time()
            hora_fim = datetime.datetime.strptime(result[1].strip(), '%H:%M').time()
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

# Função de envio de bips
async def bip_task(chat_id, chat_name, context: CallbackContext):
    database = await conexao_banco()
    cursor = database.cursor()
    hora_inicio, hora_fim =  await rotina_disparos()
    horarios_atuais = (hora_inicio, hora_fim) 
    while True:
        try:
            cursor.execute('''SELECT * FROM TLG_BIP WHERE FLAG_ALTERA = 1 AND COD_GRUPO = %s''', (chat_id,))
            tlg_bip_dados = cursor.fetchall()
            hora_envio = datetime.datetime.now()
            if tlg_bip_dados:
                for dados in tlg_bip_dados:
                    ID_BIP, COD_GRUPO, COD_SUPERVISAO, EMPR, CODFUN, POSTO, MENSAGEM, TOLERANCIA, RECORRENCIA,CONT_ABSTENSAO , ABSTENSAO, HORA_INICIO, HORA_FIM, FLAG_ALTERA, HORA_ALTERA = dados

                    # print(COD_SUPERVISAO)
                    hora_inicio, hora_fim = await rotina_disparos()
                    if (hora_inicio,hora_fim) != horarios_atuais:
                        horarios_atuais = (hora_inicio, hora_fim)
                        print(f"Nova rotina definida - Horário de início: {hora_inicio} // Horário do fim: {hora_fim}\nIniciando disparos...")
                        await context.bot.send_message(chat_id=chat_id, text=f"Nova rotina definida - Horário de início: {hora_inicio} // Horário do fim: {hora_fim}\nIniciando disparos...")
                    hora_atual = datetime.datetime.now().time()

                    if hora_inicio <= hora_atual <= hora_fim:
                        # Enviar a mensagem inicial
                        await context.bot.send_message(chat_id=chat_id, text=MENSAGEM)
                        print('Bip enviado!')
                        cursor.execute(
                            '''INSERT INTO TLG_BIPNOTIFIC (ID_BIP, COD_GRUPO, COD_SUPERVISAO, HORA_ENVIO) VALUES (%s, %s, %s, %s)''',
                            (ID_BIP, COD_GRUPO, COD_SUPERVISAO, hora_envio)
                        )
                        database.commit()

                        # Lógica de tolerância para resposta
                        resposta_recebida = False
                        for tentativa in range(1, 4):  
                            await asyncio.sleep(float(TOLERANCIA * 60))  # Tempo de tolerância
                            cursor.execute(
                                '''SELECT * FROM TLG_BIPNOTIFIC WHERE ID_BIP = %s AND COD_GRUPO = %s ORDER BY HORA_ENVIO DESC LIMIT 1''',
                                (ID_BIP, chat_id,)
                            )
                            notifica = cursor.fetchone()
                            print(notifica[4])
                            if notifica[4]:  # Resposta recebida
                                resposta_recebida = True
                                print("Resposta recebida, retornando à rotina.")
                                break

                            # Não houve resposta, enviar nova tentativa
                            try:
                                await context.bot.send_message(chat_id=chat_id, text=f'Tentativa {tentativa + 1}: {MENSAGEM}')
                                print(f"Tentativa {tentativa + 1} enviada.")
                                cursor.execute('''UPDATE TLG_BIP SET CONT_ABSTENSAO =  COALESCE(CONT_ABSTENSAO, 0 ) + 1 WHERE ID_BIP = %s AND COD_GRUPO =%s''', (ID_BIP,chat_id,))
                                database.commit()

                                # Verificar abstenção máxima
                                cursor.execute('''SELECT CONT_ABSTENSAO FROM TLG_BIP WHERE ID_BIP = %s AND COD_GRUPO =%s''', (ID_BIP, chat_id,))
                                abstencao_atual = cursor.fetchone()[0]
                                if abstencao_atual == 3:
                                    print(f"Abstenção atual: {abstencao_atual}")
                                    cursor.execute('SELECT * FROM TLG_BIPNOTIFIC WHERE CODFUN IS NOT NULL AND COD_GRUPO = %s ORDER BY HORA_RETORNO DESC LIMIT 1',(chat_id,))
                                    resposta_func = cursor.fetchone()
                                    print(f"Última resposta do funcionário: {resposta_func}")
                                    if resposta_func:
                                        codfun = resposta_func[4]
                                        empr = resposta_func[5]
                                        hora_envio = resposta_func[7]
                                        hora_retorno = resposta_func[8]
                                        if codfun is not None and empr is not None:
                                            codigo = str(codfun) + str(empr)
                                            print(codigo)
                                    
                                            cursor.execute('SELECT NAME FROM USERS WHERE CODE = %s', (codigo,))
                                            funcionario = cursor.fetchone()
                                            if funcionario:
                                                print(funcionario[0])
                                                msg_supervisao = f'Funcionário {funcionario[0]} no grupo {chat_name} não responde desde às {hora_retorno}!'
                                            else:
                                                print("Funcionario não encontrado!")
                                        else:
                                            print(f"Sem resposta registrada desde às {hora_envio}")
                                            msg_supervisao = f'Sem resposta registrada no grupo {chat_name} desde às {hora_inicio}!'
                                    else:
                                        print("Nenhuma dados encontrado em tlb_bipnotific")
                                    await context.bot.send_message(
                                        chat_id=int(COD_SUPERVISAO),
                                        text=msg_supervisao)
                                    cursor.execute('''UPDATE TLG_BIP SET CONT_ABSTENSAO = 0 WHERE ID_BIP = %s AND COD_GRUPO =%s''', (ID_BIP,chat_id,))
                                    database.commit()
                                    break

                            except Exception as error:
                                print(f'Erro ao enviar a mensagem pro grupo de supervisão : {error}')

                        tempo_total_passado = (datetime.datetime.now() - hora_envio).total_seconds()  # Tempo passado desde o primeiro envio
                        # print(f"Tempo passado: {tempo_total_passado}")
                        tempo_ate_proximo_bip = float((RECORRENCIA * 60)) - tempo_total_passado  # Tempo restante para o próximo bip
                        minutos = int(tempo_ate_proximo_bip / 60)
                        segundos = int(tempo_ate_proximo_bip % 60)
                        print(f"Tempo até o bip: {minutos} minutos e {segundos} segundos.")

                        if tempo_ate_proximo_bip <= 0:
                            tempo_ate_proximo_bip = float(RECORRENCIA * 60)  

                        print(f"Próximo bip será enviado em {minutos} minutos e {segundos} segundos.")
                        await asyncio.sleep(tempo_ate_proximo_bip)  # Aguardar o tempo de recorrência
                    else:
                        print(f"Fora do intervalo de {hora_inicio} e {hora_fim}. Aguardando...")
                        # await context.bot.send_message(chat_id=chat_id,text=f"Alerta: O usuário no grupo {chat_name} atingiu 3 abstenções.")
                        await asyncio.sleep(3)
                        
            else:
                await asyncio.sleep(3)  
        except Exception as error:
            print(f'Erro ao conectar ao banco de dados: {error}')
            await asyncio.sleep(3)  





async def bip(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    chat_name = update.message.chat.title
    asyncio.create_task(bip_task(chat_id, chat_name,context))  


async def handle_tips_code(update: Update, context: CallbackContext) -> None:
    database = await conexao_banco()
    message = update.message.text
    print("Mensagem recebida:", message)  
    chat_id = update.message.chat_id
    if message.isdigit() and len(message) >=4:
        cod_empr = message[:3] 
        cod_fun = message[3:]
        fun_timelog = datetime.datetime.now()

        try:
            cursor = database.cursor()

            cursor.execute('''
           SELECT * FROM TLG_BIPNOTIFIC WHERE COD_GRUPO = %s  AND CODFUN IS NULL ORDER BY HORA_ENVIO DESC LIMIT 1
            ''', (chat_id,))
            resposta_funcionario = cursor.fetchone()
            print(resposta_funcionario)

            if resposta_funcionario:
                id_bip = resposta_funcionario[1]  
                id_notifica = resposta_funcionario[0]
                cursor.execute('''
                UPDATE TLG_BIPNOTIFIC
                SET EMPR = %s, CODFUN = %s, HORA_RETORNO = %s
                WHERE ID_BIP = %s AND ID_NOTIFICA = %s
                ''', (cod_empr, cod_fun, fun_timelog, id_bip, id_notifica))
                resposta = f"Retorno registrado: Empresa {cod_empr}, Funcionário {cod_fun}"
                print(resposta)
                cursor.execute('''UPDATE TLG_BIP SET CONT_ABSTENSAO = 0 WHERE ID_BIP = %s''', (id_bip,))
                database.commit()
                print("Asbentsão zerada! / 1")
            else:
                resposta = "Nenhuma notificação encontrada para este grupo."
            

            database.commit()
        except Exception as e:
            print(f"Erro ao processar código: {e}")
            resposta = f"Erro ao processar código: {e}"
        finally:
            cursor.close()
            database.close()
    else:
        resposta = "Código inválido! Por favor, envie um código válido (mínimo de 4 dígitos)."

    await update.message.reply_text(resposta)
    print(f"Chat ID: {chat_id}, Empresa: {cod_empr}, Funcionário: {cod_fun}")



def main() -> None:
    

    try:
        #Token bot teste
        conexao_api = Application.builder().token("8012171445:AAFK183HpQe5DfDOUvduPUyxqvKThQ1NFlc").build()
        #Token bot visão bips
        # conexao_api = Application.builder().token("8092812812:AAFKtbKrUh1c1Rj0S1_LQ3EJWd-Rzgs_3Ps").build()
        conexao_api.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tips_code))
        conexao_api.add_handler(CommandHandler('bip', bip))  

        print("Iniciando o monitoramento...")
        conexao_api.run_polling()
    except Exception as e:
        print(f"Erro ao iniciar o bot: {e}")

if __name__ == '__main__':
    main()


