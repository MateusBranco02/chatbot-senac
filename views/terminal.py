from controllers.chatbot_controller import processar_pergunta


def iniciar_terminal():
    print('🤖 Olá sou o chatbot JP, como posso te ajudar? Caso deseje sair digite "sair" para encerrar. \n')
    while True:
        pergunta = input('Usuário: ')
        if pergunta.lower() == 'sair':
            print('Chatbot_JP: Foi um prazer ajuda-lo, até mais! :)')
            break
        
        response = processar_pergunta(pergunta)
        print(f'Chatbot_JP: {response} \n')
