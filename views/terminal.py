from controllers.chatbot_controller import processar_pergunta


def iniciar_terminal():
    print('🤖 Olá, como posso te ajudar? \n')
    while True:
        pergunta = input('Pergunta: ')
        if pergunta.lower() == 'sair':
            print('Chatbot: Foi um prazer ajuda-lo, até mais! :)')
            break
        
        response = processar_pergunta(pergunta)
        print(f'Chatbot_JP: {response} \n')
