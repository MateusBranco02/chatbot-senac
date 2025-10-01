# Comando para rodar o projeto: uvicorn main:app --reload || python -m uvicorn main:app --reload

# from controllers.chatbot_controller import inicializar_dados_site
# from views.terminal import iniciar_terminal
from fastapi import FastAPI
from routes.routes import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# if __name__ == '__main__':
#     inicializar_dados_site()
#     iniciar_terminal()
