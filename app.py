import datetime
import streamlit as st
import plotly.graph_objects as go
from utils.mysql_utils import insert_data

custom_css = """
        <style>
        [data-testid="stSliderTickBarMin"],
        [data-testid="stSliderTickBarMax"] {
            font-size: 0px;
        }
        </style>

        """


def map_answer_to_score(answer):
    rating_scale = {
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
        "Nunca": 1,
        "Raramente": 2,
        "Às vezes": 3,
        "Frequentemente": 4,
        "Sempre": 5,
        "Muito negativo": 1,
        "Negativo": 2,
        "Neutro": 3,
        "Positivo": 4,
        "Muito positivo": 5
    }
    return rating_scale.get(answer, 0)

def plot_gauge(score, title, max_val, labels, colors):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': title},
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [6, max_val]},
            'bar': {'color': '#EE7798'},
            'steps': [
                {'range': [labels[i], labels[i+1]], 'color': colors[i]} for i in range(len(labels)-1)
            ]
        }
    ))
    config = {
        'displayModeBar': False
    }
    st.plotly_chart(fig, use_container_width=True, config=config)
    return fig

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
                st.success("Dados enviados com sucesso! Veja o resultado abaixo.")

                # Cálculo das pontuações e geração do relatório
                topic_scores = {}
                for topic, answers in responses.items():
                    total_score = 0
                    for question_text, answer in answers.items():
                        score = map_answer_to_score(answer)
                        total_score += score
                    topic_scores[topic] = total_score
                
                # Definição das avaliações e recomendações
                evaluations = {
                    "Gentileza": {
                        "title": "Gentileza gera relações de trabalho mais saudáveis, produtivas e felizes.",
                        "description": "Um ambiente de trabalho que cultiva o clima corporativo gentil tem muito a ganhar com isso. Mesmo nas situações complicadas e urgentes, praticar a gentileza transforma a pressa em solicitude, e a pressão em solução. Gritar, perder a paciência, ofender gratuitamente as pessoas e entrar em desespero tomando medidas inconsequentes são exemplos de atitudes descontroladas que não levam a nada. E mais: desestabilizam toda a equipe, gerando medo e desmotivação.Em tempos de burn out, stress generalizado e baixa tolerância a opiniões diferentes, colocar a gentileza em prática pode melhorar, e muito, a qualidade de vida no ambiente de trabalho. Experimente.",
                        "ranges": [
                            {
                                "min": 6, "max": 10,
                                "evaluation": "Baixa percepção de gentileza em circulação: perigo.",
                                "recommendation": "Recomendação: criar plano de emergência para colocar a gentileza em prática."
                            },
                            {
                                "min": 11, "max": 20,
                                "evaluation": "Percepção de gentileza na média, mas pode ser melhor: atenção.",
                                "recommendation": "Recomendação: mapear onde/quando/como reforçar a prática de gestos gentis."
                            },
                            {
                                "min": 21, "max": 30,
                                "evaluation": "Percepção de gentileza em alta: manter e surpreender.",
                                "recommendation": "Recomendação: transformar a experiência em estudo de boas práticas para inspirar outros modelos de negócio."
                            }
                        ]
                    },
                    "Generosidade": {
                        "title": "Gestos de generosidade são poderosos. Toda a equipe ganha com isso.",
                        "description": "Promover o compartilhar, o colaborar e o contribuir em um ambiente de trabalho pode transformar não apenas as relações entre as pessoas como os níveis gerais de produtividade. Saber a importância de distribuir conhecimento, acessos, informações, boas energias e soluções, para dentro e fora do modelo de negócio, fortalece o senso de pertencimento dos colaboradores e estimula a visão altruísta. Com tanta competitividade agressiva em circulação, com o egoísmo e a valorização exagerada do “eu” em divulgação, especialmente nas redes sociais, fazer o exercício de pensar em “nós” e em “estamos juntos” pode fazer toda a diferença. Vale testar.",
                        "ranges": [
                            {
                                "min": 6, "max": 10,
                                "evaluation": "Baixa percepção de generosidade em circulação: perigo.",
                                "recommendation": "Recomendação: criar plano de emergência para colocar a generosidade em prática."
                            },
                            {
                                "min": 11, "max": 20,
                                "evaluation": "Percepção de generosidade na média, mas pode ser melhor: atenção.",
                                "recommendation": "Recomendação: mapear onde/quando/como reforçar a prática de gestos generosos."
                            },
                            {
                                "min": 21, "max": 30,
                                "evaluation": "Percepção de generosidade em alta: manter e surpreender.",
                                "recommendation": "Recomendação: transformar a experiência em estudo de boas práticas para inspirar outros modelos de negócio."
                            }
                        ]
                    },
                    "Solidariedade": {
                        "title": "Solidariedade é um sistema complexo. É uma rede de inteligência coletiva.",
                        "description": "Estimular a solidariedade no ambiente de trabalho é uma inspiração da liderança, mas uma responsabilidade mútua, recíproca, que surge no sentimento de identificação das necessidades do outro. Significa entender que, cada um com uas habilidades e áreas de atuação, ninguém é melhor que ninguém pois existe uma interdependência: todos estão conectados e, sozinho, não dá para ir longe. Apesar das falas de “cada um por si”, promovendo a desunião e a competição desenfreada, é tempo de atuar em conjunto, repensar a lógica das relações e reunir o que cada um tem de melhor para poder potencializar.",
                        "ranges": [
                            {
                                "min": 6, "max": 10,
                                "evaluation": "Baixa percepção de solidariedade em circulação: perigo.",
                                "recommendation": "Recomendação: criar plano de emergência para colocar a solidariedade em prática."
                            },
                            {
                                "min": 11, "max": 20,
                                "evaluation": "Percepção de solidariedade na média, mas pode ser melhor: atenção.",
                                "recommendation": "Recomendação: mapear onde/quando/como reforçar a prática de gestos solidários."
                            },
                            {
                                "min": 21, "max": 30,
                                "evaluation": "Percepção de solidariedade em alta: manter e surpreender.",
                                "recommendation": "Recomendação: transformar a experiência em estudo de boas práticas para inspirar outros modelos de negócio."
                            }
                        ]
                    },
                    "Sustentabilidade": {
                        "title": "Antes de qualquer decisão, de RH ou de gestão, pense na sustentabilidade.",
                        "description": "Ambientes de trabalho sustentáveis se preocupam não apenas com o meio ambiente, mas com a saudabilidade de todos os espaços de relacionamento e produtividade, físicos e virtuais. Não adianta fazer divulgação de políticas corporativas positivas se, na essência, nada disso é verídico por não ser colocado em prática. Falar é fácil, e fazer dá trabalho e gera investimentos, mas vale muito. Quando a sustentabilidade se transforma em um hábito, tudo muda, especialmente o comprometimento das pessoas, que passam a confiar nas promessas e nas atitudes dos modelos de negócios para os quais trabalham.",
                        "ranges": [
                            {
                                "min": 6, "max": 10,
                                "evaluation": "Baixa percepção de sustentabilidade em circulação: perigo.",
                                "recommendation": "Recomendação: criar plano de emergência para colocar a sustentabilidade em prática."
                            },
                            {
                                "min": 11, "max": 20,
                                "evaluation": "Percepção de sustentabilidade na média, mas pode ser melhor: atenção.",
                                "recommendation": "Recomendação: mapear onde/quando/como reforçar a prática de gestos sustentáveis."
                            },
                            {
                                "min": 21, "max": 30,
                                "evaluation": "Percepção de sustentabilidade em alta: manter e surpreender.",
                                "recommendation": "Recomendação: transformar a experiência em estudo de boas práticas para inspirar outros modelos de negócio."
                            }
                        ]
                    },
                    "Diversidade": {
                        "title": "Diversidade é multiplicidade de ideias. Amplie os seus horizontes.",
                        "description": "Quanto o assunto é diversidade no ambiente de trabalho, todo mundo diz que respeita, mas nem todo mundo pratica. Há muitos preconceitos e julgamentos estruturais, e lidar com isso é desafiador. Tem a ver com a capacidade de receber, incluir, acolher e respeitar a pluralidade das pessoas, com suas histórias, crenças, estilos de vida, jeitos de ser por fora e por dentro, com tudo o que é diverso, múltiplo, variado. A diversidade realmente colocada em prática é pura potência, é força aplicada com a riqueza do que há de melhor, no diverso. Ninguém disse que é fácil de implementar, mas impossível também não é. Para saber, precisa implementar.",
                        "ranges": [
                            {
                                "min": 6, "max": 10,
                                "evaluation": "Baixa percepção de diversidade em circulação: perigo.",
                                "recommendation": "Recomendação: criar plano de emergência para colocar a diversidade em prática."
                            },
                            {
                                "min": 11, "max": 20,
                                "evaluation": "Percepção de diversidade na média, mas pode ser melhor: atenção.",
                                "recommendation": "Recomendação: mapear onde/quando/como reforçar a prática de inclusão."
                            },
                            {
                                "min": 21, "max": 30,
                                "evaluation": "Percepção de diversidade em alta: manter e surpreender.",
                                "recommendation": "Recomendação: transformar a experiência em estudo de boas práticas para inspirar outros modelos de negócio."
                            }
                        ]
                    },
                    "Respeito": {
                        "title": "Respeito não é uma opção. É uma condição para se trabalhar bem.",
                        "description": "Quando o assunto é respeito no ambiente de trabalho, todo mundo quer ser respeitado. Mas será o mesmo na hora de respeitar, tolerar, considerar e acolher? Saber levar em consideração as escolhas e os contextos das outras pessoas é primordial em todas as interações sociais, e deixa tudo mais claro, visível e aferível. O respeito estimula o bom convívio coletivo, evitando julgamentos, atitudes de reprovação e ofensas, que podem gerar imparcialidade e injustiça. Os benefícios são inúmeros, e o resultado é sempre positivo.",
                        "ranges": [
                            {
                                "min": 6, "max": 10,
                                "evaluation": "Baixa percepção de respeito em circulação: perigo.",
                                "recommendation": "Recomendação: criar plano de emergência para colocar o respeito em prática."
                            },
                            {
                                "min": 11, "max": 20,
                                "evaluation": "Percepção de respeito na média, mas pode ser melhor: atenção.",
                                "recommendation": "Recomendação: mapear onde/quando/como reforçar a prática de gestos respeitosos."
                            },
                            {
                                "min": 21, "max": 30,
                                "evaluation": "Percepção de respeito em alta: manter e surpreender.",
                                "recommendation": "Recomendação: transformar a experiência em estudo de boas práticas para inspirar outros modelos de negócio."
                            }
                        ]
                    },
                    "Cidadania": {
                        "title": "Cidadania é exercer direitos e deveres também, no trabalho e na sociedade.",
                        "description": "Exigir seus direitos no ambiente de trabalho é importante e cumprir com seus deveres também. O importante é saber participar: muitos reclamam, mas não fazem nada a não ser promover o teor tóxico das relações gerando fofocas e mal-estar ao invés de buscar uma forma de ajudar, seja qual for o desafio. É hora de sair da zona de conforto e atuar, em conjunto, para melhorar. De nada adianta o desejo de ser um cidadão do mundo se as pessoas não conseguem exercer seu papel cidadão em suas próprias casas, comunidades e ambientes de trabalho. Sempre é tempo de promover um ambiente propício, a partir do exemplo da liderança, e começar.",
                        "ranges": [
                            {
                                "min": 6, "max": 10,
                                "evaluation": "Baixa percepção de cidadania em circulação: perigo.",
                                "recommendation": "Recomendação: criar plano de emergência para colocar a cidadania em prática."
                            },
                            {
                                "min": 11, "max": 20,
                                "evaluation": "Percepção de cidadania na média, mas pode ser melhor: atenção.",
                                "recommendation": "Recomendação: mapear onde/quando/como reforçar a prática de participação cidadã."
                            },
                            {
                                "min": 21, "max": 30,
                                "evaluation": "Percepção de cidadania em alta: manter e surpreender.",
                                "recommendation": "Recomendação: transformar a experiência em estudo de boas práticas para inspirar outros modelos de negócio."
                            }
                        ]
                    }
                }

                # Função para obter a avaliação e recomendação
                def get_evaluation(topic, score):
                    topic_eval = evaluations.get(topic)
                    if not topic_eval:
                        return "", "", ""
                    title = topic_eval["title"]
                    description = topic_eval["description"]
                    for range_info in topic_eval["ranges"]:
                        if range_info["min"] <= score <= range_info["max"]:
                            evaluation = range_info["evaluation"]
                            recommendation = range_info.get("recommendation", "")
                            break
                    else:
                        evaluation = "Score fora do intervalo esperado."
                        recommendation = ""
                    return title, description, evaluation, recommendation

                # Exibição do relatório
                st.header("Relatório de Avaliação")
                for topic, score in topic_scores.items():
                    title, description, evaluation_text, recommendation_text = get_evaluation(topic, score)
                    st.subheader(title)
                    st.write(f"{description}")
                    st.write(f"**Pontuação:** {score}")
                    st.write(f"**{evaluation_text}**")
                    st.write(f"**{recommendation_text}**")
                    # Gerar gráfico gauge
                    max_score = 30  # Pontuação máxima possível
                    labels = [6, 11, 21, 30]  # Intervalos das avaliações
                    colors = ['red', 'yellow', 'green']  # Cores correspondentes
                    plot_gauge(score, topic, max_score, labels, colors)
                    st.markdown("---")  # Linha separadora entre os tópicos
            
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