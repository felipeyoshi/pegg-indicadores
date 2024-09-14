import datetime
import mysql.connector
from mysql.connector import Error

def create_connection(host, user, password, dbname):
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=dbname
    )
    return connection

def insert_data(user_info, responses, db_credentials):
    try:
        # Convert birth_date from 'DD/MM/YYYY' to 'YYYY-MM-DD' format
        birth_date_obj = datetime.datetime.strptime(user_info['birth_date'], '%d/%m/%Y').date()
        birth_date_formatted = birth_date_obj.strftime('%Y-%m-%d')
        
        connection = create_connection(db_credentials["MYSQL_HOST"], db_credentials["MYSQL_USER"], db_credentials["MYSQL_PASSWORD"], db_credentials["MYSQL_DBNAME"])
        cursor = connection.cursor()

        query_user = """
            INSERT INTO pegg_2024_usuarios (nome, sobrenome, email, data_nascimento, cidade, estado, profissao, termo, news)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        user_data = (user_info['first_name'], user_info['last_name'], user_info['email'], birth_date_formatted, user_info['city'], user_info['state'], user_info['role'], user_info['terms'], user_info['news'])
        cursor.execute(query_user, user_data)
        user_id = cursor.lastrowid

        query_survey = """
            INSERT INTO pegg_2024_indicadores (usuario_id, aba, pergunta, resposta, resposta_num)
                VALUES (%s, %s, %s, %s, %s)
        """

        for tab_name, answers in responses.items():
             for question, answer in answers.items():
                numeric_answer = convert_response_to_numeric(answer)
                cursor.execute(query_survey, (user_id, tab_name, question, answer, numeric_answer))
        
        connection.commit()
        print("Dados inseridos com sucesso!")
    
    except Error as e:
        print("Erro ao conectar ao MySQL", e)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Conexão ao MySQL fechada")

def convert_response_to_numeric(response_text):
    """Converte uma resposta textual para um valor numérico entre 1 e 5."""
    mapping = {
        "Nunca": 1,
        "Raramente": 2,
        "Às vezes": 3,
        "Frequentemente": 4,
        "Sempre": 5,
        "Discordo totalmente": 1,
        "Discordo": 2,
        "Neutro": 3,
        "Concordo": 4,
        "Concordo totalmente": 5,
        "Muito insatisfatória": 1,
        "Insatisfatória": 2,
        "Neutra": 3,
        "Satisfatória": 4,
        "Muito satisfatória": 5,
        "Muito negativo": 1,
        "Negativo": 2,
        "Neutro": 3,
        "Positivo": 4,
        "Muito positivo": 5
    }
    return mapping.get(response_text, 3)  # Retorna "Neutro" (3) se a resposta não estiver no mapeamento