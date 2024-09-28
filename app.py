import datetime
import streamlit as st
from utils.mysql_utils import insert_data

custom_css = """
        <style>
        [data-testid="stSliderTickBarMin"],
        [data-testid="stSliderTickBarMax"] {
            font-size: 0px;
        }
        </style>

        """

# Função para exibir perguntas com sliders
def show_questions(questions, tab):
    with tab:
        for question in questions:
            st.markdown(custom_css, unsafe_allow_html=True)
            st.select_slider(
                question["text"],
                options=question["format"],
                value=question["format"][2], # valor padrão como "Neutro" ou "Às vezes"
                key=question["text"]
            )

#Função para capturar os dados pessoais e enviar os dados
def get_user_info_and_submit(tab):
    with tab:
        with st.form("form_relatorio"):
            st.header("Informações Pessoais")
            first_name = st.text_input("Nome *")
            last_name = st.text_input("Sobrenome *")
            email = st.text_input("* Email *")
            birth_date = st.text_input("Data de Nascimento (DIA/MÊS/ANO) *", value=None)
            city = st.text_input("Cidade *")
            state = st.text_input("Estado *")
            role = st.text_input("Profissão / Atividade Exercida *")
            terms = st.checkbox("Li e aceito os Termos de Uso *")
            news = st.checkbox("Eu quero receber novidades e outras informações")
            submitted = st.form_submit_button("Enviar!")

        with open("./pdf/termos.pdf", "rb") as file:
            btn = st.download_button(
                label="Ler os Termos de Uso",
                data=file,
                file_name="Termos-e-Condicoes-de-Uso_EGG_2024.pdf",
                mime="application/pdf"
                )

        if submitted:
            if not (first_name and last_name and email and birth_date and city and state and role and terms):
                st.warning("Por favor, preencha todos os campos obrigatórios.")
            elif birth_date and not validate_date_format(birth_date):
                st.error("Formato de Data de Nascimento inválido. Por favor, use DIA/MÊS/ANO.")
            else:
                user_info = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'birth_date': birth_date,
                    'city': city,
                    'state': state,
                    'role': role,
                    'terms': terms,
                    'news': news
                }
                responses = {}
                for tab_name, questions in questions_dict.items():
                    tab_responses = {}
                    for question in questions:
                        answer = st.session_state.get(question["text"])
                        tab_responses[question["text"]] = answer
                    responses[tab_name] = tab_responses
                db_credentials = st.secrets["secrets"]
                insert_data(user_info, responses, db_credentials)
                st.success("Dados enviados com sucesso!")
            
def validate_date_format(date_str):
    try:
        datetime.datetime.strptime(date_str, '%d/%m/%Y')
        return True
    except ValueError:
        return False

st.image('./images/pegg_header.jpeg')

# Criando abas para cada princípio
tabs = st.tabs(["GENTILEZA", "GENEROSIDADE", "SOLIDARIEDADE", "SUSTENTABILIDADE", "DIVERSIDADE", "RESPEITO", "CIDADANIA", "DADOS"])

# Definindo todas as perguntas para cada aba
questions_dict = {
    "Gentileza": [
        {"text": "Você acha que seus colegas de trabalho são gentis e acolhedores em suas interações informais do dia a dia, como cumprimentar e dar passagem?", "format": ["Discordo totalmente", "Discordo", "Neutro", "Concordo", "Concordo totalmente"]},
        {"text": "Você acha que você é gentil e acolhedor em suas interações informais do dia a dia, como cumprimentar e dar passagem?", "format": ["Discordo totalmente", "Discordo", "Neutro", "Concordo", "Concordo totalmente"]},
        {"text": "Você acredita que a liderança demonstra gentileza e consideração ao lidar com os membros da equipe, usando comunicação gentil e não-violenta?", "format": ["Discordo totalmente", "Discordo", "Neutro", "Concordo", "Concordo totalmente"]},
        {"text": "Quando acontece algum desafio de convivência, você se sente à vontade para expressar suas preocupações e dar sugestões junto aos seus líderes e pares?", "format": ["Discordo totalmente", "Discordo", "Neutro", "Concordo", "Concordo totalmente"]},
        {"text": "Como você avalia a atitude geral de gentileza e compreensão em reuniões e interações técnicas de trabalho envolvendo prazos e urgências?", "format": ["Muito insatisfatória", "Insatisfatória", "Neutra", "Satisfatória", "Muito satisfatória"]},
        {"text": "A empresa promove iniciativas ou atividades que incentivam a prática de gentileza no ambiente de trabalho, reforçando a importância destas atitudes?", "format": ["Discordo totalmente", "Discordo", "Neutro", "Concordo", "Concordo totalmente"]}
    ],
    "Generosidade": [
        {"text": "Quando você observa que os colegas de trabalho estão dispostos a ajudar uns aos outros, doando tempo, conhecimento, boa vontade, mesmo quando não há um benefício imediato para eles?", "format": ["Nunca", "Raramente", "Às vezes", "Frequentemente", "Sempre"]},
        {"text": "Quando você está disposto a ajudar os seus colegas doando tempo, conhecimento, boa vontade, mesmo quando não há um benefício imediato para você?", "format": ["Nunca", "Raramente", "Às vezes", "Frequentemente", "Sempre"]},
        {"text": "A empresa incentiva ou recompensa comportamentos generosos entre os colaboradores, promovendo campanhas e ações de doação e voluntariado, por exemplo?", "format": ["Nunca", "Raramente", "Às vezes", "Frequentemente", "Sempre"]},
        {"text": "Quando você precisa de assistência ou alguma negociação especial, de tempo e/ou dinheiro, você sente que pode contar com a empresa para ajudar?", "format": ["Discordo totalmente", "Discordo", "Neutro", "Concordo", "Concordo totalmente"]},
        {"text": "Você acredita que a generosidade para com o time e para com o próximo é um valor reconhecido e valorizado pela liderança da empresa?", "format": ["Discordo totalmente", "Discordo", "Neutro", "Concordo", "Concordo totalmente"]},
        {"text": "Como você avalia a disponibilidade seu líder para compartilhar conhecimentos e recursos?", "format": ["Muito insatisfatória", "Insatisfatória", "Neutra", "Satisfatória", "Muito satisfatória"]}
    ],
    "Solidariedade": [
        {"text": "Você percebe que há um bom nível de apoio entre colegas em momentos de dificuldade, no desenvolvimento de um projeto ou em uma entrega?", "format": ["Discordo totalmente", "Discordo", "Neutro", "Concordo", "Concordo totalmente"]},
        {"text": "Você percebe é uma referência quando o assunto é apoio entre seus colegas em momentos de dificuldade, no desenvolvimento de um projeto ou em uma entrega?", "format": ["Discordo totalmente", "Discordo", "Neutro", "Concordo", "Concordo totalmente"]},
        {"text": "A empresa promove atividades ou eventos que incentivam a solidariedade e o trabalho em equipe?", "format": ["Discordo totalmente", "Discordo", "Neutro", "Concordo", "Concordo totalmente"]},
        {"text": "Quando ocorrem desafios ou crises, você sente que a equipe se une para enfrentá-los?", "format": ["Discordo totalmente", "Discordo", "Neutro", "Concordo", "Concordo totalmente"]},
        {"text": "Você sente que a empresa oferece suporte adequado aos colaboradores que enfrentam problemas pessoais ou profissionais?", "format": ["Discordo totalmente", "Discordo", "Neutro", "Concordo", "Concordo totalmente"]},
        {"text": "Qual é a sua percepção sobre a colaboração e o apoio entre as lideranças de departamentos diferentes?", "format": ["Muito insatisfatória", "Insatisfatória", "Neutra", "Satisfatória", "Muito satisfatória"]}
    ],
    "Sustentabilidade": [
        {"text": "A empresa adota práticas sustentáveis em suas relações com a sociedade e com o mercado, assim como ecológicas, em suas operações diárias?", "format": ["Discordo totalmente", "Discordo", "Neutro", "Concordo", "Concordo totalmente"]},
        {"text": "Você adota práticas práticas sustentáveis em suas relações com a sociedade e com o mercado e ecológicas em suas operações diárias, especialmente no ambiente de trabalho?", "format": ["Discordo totalmente", "Discordo", "Neutro", "Concordo", "Concordo totalmente"]},
        {"text": "Você recebe de seus líderes informações e treinamentos sobre práticas sustentáveis e como contribuir para elas no trabalho?", "format": ["Discordo totalmente", "Discordo", "Neutro", "Concordo", "Concordo totalmente"]},
        {"text": "A empresa tem um compromisso sério e formalizado sobre redução do impacto ambiental e aplicação de práticas sustentáveis em todas as suas relações?", "format": ["Discordo totalmente", "Discordo", "Neutro", "Concordo", "Concordo totalmente"]},
        {"text": "Você acredita que a empresa incentiva práticas sustentáveis entre os colaboradores e a comunidade?", "format": ["Discordo totalmente", "Discordo", "Neutro", "Concordo", "Concordo totalmente"]},
        {"text": "Qual é a sua percepção sobre o impacto das práticas de sustentabilidade da empresa na sua própria experiência de trabalho?", "format": ["Muito negativo", "Negativo", "Neutro", "Positivo", "Muito positivo"]}
    ],
    "Diversidade": [
        {"text": "A empresa promove e valoriza a diversidade em suas práticas de recrutamento e seleção, retenção e relacionamento com colaboradores?", "format": ["Discordo totalmente", "Discordo", "Neutro", "Concordo", "Concordo totalmente"]},
        {"text": "Você se considera uma pessoa inclusiva e aberta a acolher a diversidade, tanto de raça, gênero, cultura e crenças como de opiniões diversas das suas?", "format": ["Discordo totalmente", "Discordo", "Neutro", "Concordo", "Concordo totalmente"]},
        {"text": "Você sente que diferentes perspectivas e experiências são respeitadas e valorizadas no ambiente de trabalho?", "format": ["Discordo totalmente", "Discordo", "Neutro", "Concordo", "Concordo totalmente"]},
        {"text": "Existem políticas ou práticas na empresa que apoiam a inclusão de grupos diversos?", "format": ["Discordo totalmente", "Discordo", "Neutro", "Concordo", "Concordo totalmente"]},
        {"text": "Qual é o nível de diversidade de raça, gênero, classe socioecômica, nível de estudo, entre outros grupos de pertencimento, em sua equipe ou departamento?", "format": ["Muito insatisfatória", "Insatisfatória", "Neutra", "Satisfatória", "Muito satisfatória"]},
        {"text": "Você tem acesso a oportunidades de desenvolvimento e crescimento profissional independentemente do seu grupo de pertencimento?", "format": ["Discordo totalmente", "Discordo", "Neutro", "Concordo", "Concordo totalmente"]}
    ],
    "Respeito": [
        {"text": "Os colaboradores são tratados pela liderança com respeito em todas as interações, independentemente de suas funções ou cargos, raças ou credos?", "format": ["Discordo totalmente", "Discordo", "Neutro", "Concordo", "Concordo totalmente"]},
        {"text": "Você trata seus colegas de trabalho e demais colaboradores com respeito em todas as interações, independentemente de suas funções ou cargos, raças ou credos?", "format": ["Discordo totalmente", "Discordo", "Neutro", "Concordo", "Concordo totalmente"]},
        {"text": "Você se sente respeitado pela liderança e pelos colegas no ambiente de trabalho?", "format": ["Discordo totalmente", "Discordo", "Neutro", "Concordo", "Concordo totalmente"]},
        {"text": "A empresa tem políticas claras contra discriminação e assédio, e as aplica de forma eficaz?", "format": ["Discordo totalmente", "Discordo", "Neutro", "Concordo", "Concordo totalmente"]},
        {"text": "Você acredita que a comunicação na empresa é feita de maneira respeitosa e construtiva?", "format": ["Discordo totalmente", "Discordo", "Neutro", "Concordo", "Concordo totalmente"]},
        {"text": "Como você avalia o tratamento que recebe de su líder quando expressa suas opiniões ou feedbacks?", "format": ["Muito insatisfatória", "Insatisfatória", "Neutra", "Satisfatória", "Muito satisfatória"]}
    ],
    "Cidadania": [
        {"text": "Você se envolve em atividades ou iniciativas que beneficiam a comunidade local e demonstram a sua participação social?", "format": ["Discordo totalmente", "Discordo", "Neutro", "Concordo", "Concordo totalmente"]},
        {"text": "A empresa se envolve em atividades ou iniciativas que beneficiam a comunidade local e demonstram a sua participação social?", "format": ["Discordo totalmente", "Discordo", "Neutro", "Concordo", "Concordo totalmente"]},
        {"text": "Você é incentivado pela liderança a participar de ações de voluntariado, projetos comunitários ou ações de participação cidadã promovidos pela empresa?", "format": ["Discordo totalmente", "Discordo", "Neutro", "Concordo", "Concordo totalmente"]},
        {"text": "Como você avalia o impacto das ações da empresa em relação à participação social e cidadania?", "format": ["Muito insatisfatória", "Insatisfatória", "Neutra", "Satisfatória", "Muito satisfatória"]},
        {"text": "A empresa promove práticas de participação social e ambiental que refletem seu compromisso com a cidadania corporativa?", "format": ["Discordo totalmente", "Discordo", "Neutro", "Concordo", "Concordo totalmente"]},
        {"text": "Você sente que a empresa valoriza e reconhece suas contribuições para a comunidade e para causas sociais?", "format": ["Discordo totalmente", "Discordo", "Neutro", "Concordo", "Concordo totalmente"]}
    ]
}

# Exibindo as perguntas em cada aba
show_questions(questions_dict["Gentileza"], tabs[0])
show_questions(questions_dict["Generosidade"], tabs[1])
show_questions(questions_dict["Solidariedade"], tabs[2])
show_questions(questions_dict["Sustentabilidade"], tabs[3])
show_questions(questions_dict["Diversidade"], tabs[4])
show_questions(questions_dict["Respeito"], tabs[5])
show_questions(questions_dict["Cidadania"], tabs[6])

user_info = get_user_info_and_submit(tabs[7])