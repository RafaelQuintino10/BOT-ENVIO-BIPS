import psycopg2
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Token do bot
# TOKEN = "8012171445:AAFK183HpQe5DfDOUvduPUyxqvKThQ1NFlc"

# # ID do grupo onde a mensagem será enviada
# TARGET_GROUP_ID = -1002458377129  # Substitua pelo ID do grupo de destino


# # Função para lidar com o comando /start
# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     # Verifica se a mensagem veio de um grupo
#     if update.message.chat.type in ['group', 'supergroup']:
#         chat_title = update.message.chat.title
#         user = update.message.from_user.first_name

#         # Envia uma mensagem de confirmação no grupo atual
#         await update.message.reply_text(f'Bot ativado por {user} no grupo "{chat_title}".')
#         print(f'Bot ativado no grupo: {chat_title}')

#         # Envia uma mensagem para o grupo de destino
#         await context.bot.send_message(
#             chat_id=TARGET_GROUP_ID,
#             text=f'Mensagem enviada do grupo "{chat_title}".'
#         )
#         print(f'Mensagem enviada para o grupo ID: {TARGET_GROUP_ID}')
#     else:
#         await update.message.reply_text('Este comando deve ser usado em um grupo.')


# # Configuração do bot
# def main():
#     # Cria a aplicação do bot
#     application = Application.builder().token(TOKEN).build()

#     # Adiciona o comando /start
#     application.add_handler(CommandHandler('start', start))

#     # Inicia o bot
#     print("Bot está rodando...")
#     application.run_polling()


# if __name__ == '__main__':
#     main()


async def conexao_banco():
    # conexao = sqlite3.connect('bot_tips.db')
    conexao = psycopg2.connect(
            host="localhost",
            database="bot_tips",
            user="postgres",
            password="fla1357912",
            port="5432"
        )
    return conexao 


TOKEN = "8012171445:AAFK183HpQe5DfDOUvduPUyxqvKThQ1NFlc"

# ID do grupo onde a mensagem será enviada
# TARGET_GROUP_ID = -1002458377129  # Substitua pelo ID do grupo de destino


# Função para lidar com o comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    database = await conexao_banco()
    cursor = database.cursor()
    cursor.execute('''SELECT * FROM TLG_BIP WHERE FLAG_ALTERA = 1''')
    tlg_bip_dados = cursor.fetchall()
    if tlg_bip_dados:
        for dados in tlg_bip_dados:
            ID_BIP, COD_GRUPO, COD_SUPERVISAO, EMPR, CODFUN, POSTO, MENSAGEM, TOLERANCIA, RECORRENCIA, ABSTENSAO, HORA_INICIO, HORA_FIM, FLAG_ALTERA, HORA_ALTERA = dados

        COD_SUPERVISAO_FLOAT = float(COD_SUPERVISAO)
        print(COD_SUPERVISAO_FLOAT)
        print(ABSTENSAO)

    if ABSTENSAO == 3:
        # Verifica se a mensagem veio de um grupo
        if update.message.chat.type in ['group', 'supergroup']:
            chat_title = update.message.chat.title
            user = update.message.from_user.first_name

            # Envia uma mensagem de confirmação no grupo atual
            await update.message.reply_text(f'Bot ativado por {user} no grupo "{chat_title}".')
            print(f'Bot ativado no grupo: {chat_title}')

            # Envia uma mensagem para o grupo de destino
            await context.bot.send_message(
                chat_id=COD_SUPERVISAO_FLOAT,
                text=f'Mensagem enviada do grupo "{chat_title}".'
            )
            print(f'Mensagem enviada para o grupo ID: {COD_SUPERVISAO}')
        else:
            await update.message.reply_text('Este comando deve ser usado em um grupo.')


# Configuração do bot
def main():
    # Cria a aplicação do bot
    application = Application.builder().token(TOKEN).build()

    # Adiciona o comando /start
    application.add_handler(CommandHandler('start', start))

    # Inicia o bot
    print("Bot está rodando...")
    application.run_polling()


if __name__ == '__main__':
    main()
