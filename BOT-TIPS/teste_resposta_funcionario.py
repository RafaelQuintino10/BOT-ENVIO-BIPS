


import psycopg2


def conexao_banco():
    try:
            # Conectar ao banco de dados
        conexao = psycopg2.connect(
                host="localhost",
                database="bot_tips",
                user="postgres",
                password="fla1357912",
                port="5432")

        print("Conexão estabelecida com sucesso")

    except Exception as error:
        print(f"Erro ao conectar ao banco de dados: {error}")

    return conexao 

def resposta():
    conexao = conexao_banco()
    cursor = conexao.cursor()
    cursor.execute('select * from tlg_bipnotific order by hora_envio desc limit 1')
    resposta_func = cursor.fetchone()
    if resposta_func:
        codfun = resposta_func[4]
        empr = resposta_func[5]
        hora_envio = resposta_func[7]
        if codfun is not None and empr is not None:
            codigo = str(codfun) + str(empr)
            print(codigo)
    
            cursor.execute('select name from users where code = %s', (codigo,))
            funcionario = cursor.fetchone()
            if funcionario:
                print(funcionario[0])
            else:
                print("Funcionario não encontrado para este código!")
        else:
            print(f"Sem resposta registrada desde às {hora_envio}")
    else:
        print("Nenhuma dados encontrado em tlb_bipnotific")


resposta()