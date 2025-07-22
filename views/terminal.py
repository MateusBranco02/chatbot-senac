from controllers.chatbot_controller import processar_pergunta


def iniciar_terminal():
    print('Olá, como posso te ajudar? \n')
    while True:
        pergunta = input('Pergunta:\n ')
        if pergunta.lower() == 'sair':
            print('Chatbot: Foi um prazer ajuda-lo, até mais! :)')
            break
        
        response = processar_pergunta(pergunta)
        print(f'\nChatbot:\n {response} \n')
